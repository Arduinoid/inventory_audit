#!/bin/usr python3

from json import JSONDecodeError, loads
import os
import re

# ----- SETUP VARIABLES ------ #
FILE_PATH = 'C:\\Users\\Jon\\Documents\\Code\\inventory_audit\\sample_info\\server-specs'

class BaseProcess(object):
    '''
    This is the base class that other parser classes will inherit from.
    It contains the common properties and methods used by other parsers 
    '''

    def __init__(self, file_path, file_name=None):
        assert os.path.exists(file_path), "File path is not valid or does not exist"
        self.path = os.path.abspath(file_path)
        self.file_name = file_name
        self.content = None
        self.json_data = None
        self.tag = None

    def get_file_content(self, directory, file):
        """Opens and extracts contents of a file"""
        with open(self.path + '\\' + directory + '\\' + file, 'r') as f:
            if '.txt' in file:
                self.content = [ i.strip() for i in f.read().split('\n') if i != '' ]
            else:
                self.content = f.read()

    def get_context(self, lines, term):
        '''
        Get the end index for each start index in a list

        example:
        get_context(lines, term=TERM)
        > [3,8]
        '''
        start_index = self.term_index(term,lines)
        end_index = list()

        for index, value in enumerate(lines):
            if start_index[index+1:] == []:
                end_index.append(len(lines))
                context = list(zip(start_index, end_index))
                break
            end_index.append(start_index[index+1] -1 )

        return sublist(context,lines)

    def term_index(self, term, lines):
        '''
        Small function that takes a list and a string and returns a list of line
        indexes where that term shows up
        '''
        result = list()
        for index, line in enumerate(lines):
            if term in line:
                result.append(index)
        return result

    def _fix_json(self, data):
        '''
        Input a string containing json and return a corrected
        json string.

        This function assumes that the invalid json needs to be wrapped in 
        a list and proper comma delimiters be inserted between objects
        '''
        data = data.strip()
        if data.find('[') != 0:
            data = '[' + data + ']'
        data = re.sub("}\s*{", "},{", data)
        return data

    def get_json_data(self, directory):
        self.tag = directory.split('-')[0]
        data = self.get_file_content(directory, self.file_name)
        if data:
            try:
                self.json_data = loads(data)
            except JSONDecodeError:
                data = self._fix_json(data)
                self.json_data = loads(data)

    def split_by_term(self, data):
        last_term = 0
        first_term = 0
        result = list()
        for index, value in enumerate(data):
            if self.descriptor in value:
                first_term = index
                sub_data =self.list_to_dict(data[last_term:first_term])
                if sub_data != {}:
                    result.append(sub_data)
                last_term = first_term
        return result

    def list_to_dict(self, list_, delimiter=':'):
        '''
        Takes a string and a delimiter then splits into key values.
        returns a dict
        '''
        result = dict()
        key, value = (0, -1)
        for string in list_:
            spec = string.split(delimiter)
            result.update({ spec[key].replace(' ','') : spec[value] })
        return result


class MacAddressParse(BaseProcess):
    '''
    This class will extract mac address information
    based on a descriptor in a cards product name
    '''
    def __init__(self,file_path, descriptor, file_name='lshw-network.json'):
        super().__init__(file_path, file_name)
        self.descriptor = descriptor
        self.attributes = ['tag','mac']

    def __call__(self, directory):
        self.get_json_data(directory)
        return self.get_each_card()

    def get_each_card(self):
            if isinstance(self.json_data,list):
                for i in self.json_data:
                    if self._get_mac_address(self._is_product(i)):
                        return self._get_mac_address(self._is_product(i))
            elif isinstance(self.json_data,dict):
                return self._get_mac_address(self._is_product(self.json_data))

    def _get_mac_address(self, card):
        if card:
            print('Service Tag | Mac Address')
            print(self.tag,'|',card['serial'],'\n')
            return {'tag': self.tag, 'mac': card['serial']}

    def _is_product(self, card):
        if self.descriptor in card['product']:
            return card


class ServerParse(BaseProcess):
    def __init__(self,file_path):
        self.file_path = file_path
        self.content = dict()
        self.attributes = [
            'make',
            'model',
            'serial',
            'memory_total',
            'memory_count',
            'memory_size',
            'cpu',
            'cpu_count',
            'mac',
            'controller',
            'cache',
            ]

    def __call__(self, directory):
        self.process(directory)

    def process(self,directory):
        tag = directory.split('-')[0]
        payload = dict()
        with open(self.file_path + '/' + directory) as f:
            pass


class MemoryParser(BaseProcess):
    def __init__(self, file_path, term, file_name='dmi-memory.txt'):
        super().__init__(file_path, file_name)
        self.content = None
        self.descriptor = term
        self.attributes = None

    def __call__(self,directory):
        self.get_file_content(directory, self.file_name)
        return self.split_by_term(self.content)


class CPUParser(BaseProcess):
    pass


class DriveParser(BaseProcess):
    pass


class NetworkParser(BaseProcess):
    pass


########################################
# CLEAN UP ZONE FOLLOWING THIS COMMENT #
########################################


# ------ BEGIN FUNCTIONS -------- #

def process_drives(brand):
    '''
    Takes a list of list and returns a list of dicts

    Using a lot of the utility functions this, function processes
    sub lists into easier to use dictionaries for later usage

    One of those intended uses is converting to json and then sending to a 
    RESTful API

    example:
    process_drives([
        ['spec1: value1', '   spec2: value2'],
        ['spec1: value1', '   spec2: value2']
    ]) 
    > [
        {'spec1': 'value1', 'spec2': 'value2'},
        {'spec1': 'value1', 'spec2': 'value2'}
        ]
    '''
    spec = 'drives'
    process = server_files[brand][spec]['process']
    attribs = server_files[brand][spec]['attributes']
    drives = [lines_to_dict(drive) for drive in get_context(open_spec_file(brand,spec,server_files),spec)]
    drives = [get_drive_attributes(process(drive),attribs) for drive in drives]

    return drives


# ------- UTILITY FUNCTIONS ------- #

def sublist(bounds, lines):
    '''
    Takes a list and some indecies and returns a list of lists
    In other words it splits a list into chunks

    The intended use is for grouping lines from a file
    '''
    return [lines[i[0]:i[1]] for i in bounds]

def get_drive_attributes(dict_, attribs):
    '''
    Take a dictionary of HP drive specs and return a new dictionary of specs 
    based on a given list
    '''
    try:
        assert type(dict_).__name__ == 'dict', "Need to make sure to pass in a dict"
        return { key: dict_[key] for key in attribs }
    except KeyError:
        print("Key value does not exist in your list or dict argument")


def parse_megaraid_inquiry_field(dict_):
    '''
    Takes a dictionary of megaraid attributes and parses
    the 'InquiryData' field into it's separate 'make','model', and 'serial' data.
    This is then injected back into the dictionary and returned. A non destructive
    copy of the given dict is returned
    '''
    result = list()
    data = dict_['InquiryData'].strip()
    while True:
        index = data.find(' ')
        result.append(data[:index])
        data = data[index:].strip()
        if data.find(' ') < 0:
            result.append(data)
            break

    assert len(result) == 3, f'Result does not have all three datum: {result}'
    dict_['Make'] = result[0]
    dict_['Model'] = result[1]
    dict_['Serial'] = result[2]

    return dict_


def parse_hp_model_field(dict_):
    '''
    Takes a dict of HP drive attributes and will parse the 'Model'
    field into 'Make' and 'Model' values. This is because the hp utility 
    that produces this data puts this info together in the 'Model' attribute. 
    There will then be a new dict returned containing a new 'Make' field and the 
    existing 'Model' field will only contain the model info
    '''
    data = dict_['Model'].strip().split(' ')
    dict_['Make'], dict_['Model'] = data
    return dict_

