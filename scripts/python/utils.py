'''
This is a module to contain some useful functions and classes
'''
import csv, os, re
from datetime import datetime
from time import sleep
from zebra import zebra

TEMPLATE = '''
^XA
^FO100,100
^A0,60,60
^FD
MAC:{mac}
^FS
^FO100,200
^A0,60,60
^FD
TAG:{tag}
^FS
^XZ
'''

z = zebra(queue='ZDesigner GK420d')


class FileWatcher(object):
    '''
    Helper class that will perform checks against a directory
    for when new files and folders show up.
    '''

    def __init__(self, path, descriptor='-spec'):
        self.path = path
        self.descriptor = descriptor
        self.old_files = self._filter_folders()
        self.new_files = None

    def _compare(self):
        result = set(self.new_files) - set(self.old_files)
        if result != set():
            return list(result)

    def _filter_folders(self):
        result = list()
        for file in os.listdir(self.path):
            if self.descriptor in file:
                result.append(file)
        return result
        # Debating on whether the above code is better which is more readable 
        # or is the more terse list comprehesion below better to save on lines...
        # return [file for file in os.listdir(self.path) if self.descriptor in file]

    def update(self, path):
        self.new_files = self._filter_folders()
        result = self._compare()
        self.old_files = self.new_files
        return result

    def watch(self, *tasks, interval=1):
        '''
        This method will start a loop which is intended to be 
        used in a main script.

        It will continue to check a directory for newly added or changed files and folders.
        Any new directories will be capture as a list and passed to task objects. These tasks
        are given as parameters at call time.

        Example:
            watcher.watch(task1,task2,task3)
            <or>
            tasks = [task1,task2,task3]
            watcher.watch(*tasks)

        Parameters:
            *tasks = object or function (object must be callable)

        Returns:
            None (this method has side effects)
        '''
        while True:
            result = self.update(self.path)
            if result != None:
                for r in result:
                    for task in tasks:
                        task(r)
            sleep(interval)


class ThermalPrinter(object):
    '''
    Takes a string template containing key value formating and runs 
    several given processor objects to compose the content that will be merged 
    with the template and sent to a printer.

    p = ThermalPrinter(template, [mac, specs, memory], 'Zebra')
    '''
    def __init__(self, template, processors, printer=z):
        self.printer = printer
        self.template = template
        self.content = dict()
        self.processors = processors

    def __call__(self, directory):
        self.compose_content(directory)
        if self.isEmpty(self.content):
            self.print_out()
            self._flush_content()

    def print_out(self):
        payload = self.template.format(**self.content)
        self.printer.output(payload)

    def compose_content(self, directory):
        for p in self.processors:
            self.content.update(p(directory)) if p(directory) else None

    def isEmpty(self, dict_):
        if dict_ and len(dict_) > 0 and isinstance(dict_,dict):
                return dict_

    def _flush_content(self):
        self.content = dict()


class CSVReport(object):
    def __init__(self, file_path, report_name, processor):
        self.file_path = file_path
        self.report_name = report_name
        self.POnumber = None
        self.processor = processor
        self.headers = self.processor.attributes
        self.file = None
        self.file_name = None
        self.writer = None

    def __call__(self, directory):
        self.write_row(self.processor(directory))

    def __del__(self):
        self.file.close()

    def open_report(self):
        self.file = open(self.file_path + '/' + self.file_name, 'w', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=self.headers)
        self.writer.writeheader()

    def new_report(self):
        formatted = '{}_PO-{}_{}.csv'.format(self.report_name, self.POnumber, datetime.now())
        return formatted.replace(' ','_').replace(':','-')

    def write_row(self, data):
        if data:
            self.writer.writerow(data)
            print('new row written to report','\n')
        else:
            print('Empty data, no rows written','\n')

    def get_po_input(self):
        valid = False
        while not valid:
            POnum = input('Please enter PO number: ')
            print(POnum,type(POnum))
            if POnum.isalnum:
                self.POnumber = POnum
                self.file_name = self.new_report()
                print("PO input excepted")
                print("Scan servers to populate report located at:")
                print(self.file_path, self.file_name)
                valid = True
            else:
                print("please enter a valid alpha numeric PO Number containing no symbols")


