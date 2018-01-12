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

    def __init__(self, path):
        self.path = path
        self.old_files = os.listdir(path)
        self.new_files = None

    def _compare(self):
        result = set(self.new_files) - set(self.old_files)
        if result != set():
            return list(result)

    def check(self):
        self.new_files = os.listdir(self.path)
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
            result = self.check()
            if result != None:
                for r in result:
                    if '-spec' in r:
                        for task in tasks:
                            task(r)
            sleep(interval)


class ThermalPrinter(object):
    '''
    p = ThermalPrinter(mac.extract,template, 'Zebra')
    '''
    def __init__(self, template, processor, printer=z):
        self.printer = printer
        self.template = template
        self.content = None
        self.processor = processor

    def __call__(self, directory):
        self.content = self.processor(directory)
        if self.content != None:
            self.print_out()

    def print_out(self):
        payload = self.template.format(**self.content)
        self.printer.output(payload)


class CSVReport(object):
    def __init__(self, file_path, report_name, processor):
        self.file_path = file_path
        self.report_name = self.new_report(report_name)
        self.processor = processor
        self.headers = self.processor.attributes
        self.file = None
        self.writer = None

    def __call__(self, directory):
        self.write_row(self.processor(directory))
        print('new row written')

    def __del__(self):
        self.file.close()

    def open_report(self):
        self.file = open(self.file_path + '/' + self.report_name, 'w', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=self.headers)
        self.writer.writeheader()

    def new_report(self,name):
        formatted = '{}_{}.csv'.format(name, datetime.now())
        return formatted.replace(' ','_').replace(':','-')

    def write_row(self, data):
        self.writer.writerow(data)
