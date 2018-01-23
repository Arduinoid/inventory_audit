'''
This is a module to contain some useful functions and classes
'''
import csv, os, re
from datetime import datetime
from time import sleep
from zebra import zebra

TEMPLATE = '''
^XA
^FO70,50
^A0,30,30
^FD
MAC:{mac}
^FS
^FO70,90
^A0,30,30
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
    Takes an object that should return a list of dicts when called.
    The object should also have a callable template attribute that returns
    a string that is used for a template. The template and the content are combined
    and then printed.

    p = ThermalPrinter(mac, printer=Zebra)
    '''
    def __init__(self, parser, printer=z):
        self.printer = printer
        self.template = None
        self.content = None
        self.parser = parser
        self.payload = list()

    def __call__(self, directory):
        self.compose_content(directory)
        self.print_out()

    def print_out(self):
        for p in self.payload:
            self.printer.output(p)

    def compose_content(self, directory):
        self.content = self.parser(directory)
        self.template = self.parser.template()
        for c in self.content:
            temp = self.template.format(**c)
            self.payload.append(temp)


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


class PrinterTemplate(object):
    def __init__(self, attrs, label_size=(3,1), font_size=30, margin=20):
        self.attrs = list(attrs)
        self.font_size = font_size
        self.dpi = 203
        self.label_size = None
        self.margin = None
        self.line_positions = None
        self.data = None
        self.main_temp = '^XA\n{main}\n^XZ'
        self.attr_content = '^FO20,{pos_y}\n^A0,{size},{size}\n^FD\n{attribute}: {{{attribute}}}\n^FS'
        self.payload = None
        self.convert_size(label_size)
        self.set_margin(margin)
        self.calculate_positions()
        self.combine_data()
        self.generate()

    def __call__(self):
        return self.payload

    def generate(self):
        result = ''
        for d in self.data:
            result += self.attr_content.format(
                pos_y=d[1],
                size=self.font_size,
                attribute=d[0]
            )
        self.payload = self.main_temp.format(main=result)

    def convert_size(self, size):
        '''Takes a tuple and returns a tuple'''
        height, width = size
        self.label_size = (height*self.dpi, width*self.dpi)

    def set_margin(self, percent):
        '''
        Takes an whole int that represents percent and sets
        the margin field based on label height 
        
        set_margin(20)
        '''
        convert = percent * 0.01
        self.margin = int(self.label_size[1] * convert)

    def calculate_positions(self):
        start = self.margin
        end = self.label_size[1] - self.margin
        step = self.font_size + 10
        self.line_positions = list(range(start,end,step))

    def combine_data(self):
        self.data = zip(self.attrs, self.line_positions)