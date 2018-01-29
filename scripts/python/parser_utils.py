#!/bin/usr python3

from json import JSONDecodeError, loads
import os
import re

from utils import PrinterTemplate

# ----- SETUP VARIABLES ------ #
# FILE_PATH = 'C:\\Users\\Jon\\Documents\\Code\\inventory_audit\\sample_info\\server-specs'

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
        self.delimiter = ':'
        self.empty_terms = None
        self.data = None
        self.tag = None

    def extract_file_content(self, directory):
        """Opens and extracts contents of a file"""
        self.get_service_tag(directory)
        with open(self.path + '\\' + directory + '\\' + self.file_name, 'r') as f:
            if '.txt' in self.file_name:
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
        data = self.insert_commas(self.wrap_in_list(self.remove_trailing_comma(data)))
        return data

    def remove_trailing_comma(self, data):
        if ',' in data[-1]:
            data = data[:-1]
        return data

    def wrap_in_list(self, data):
        if data.find('[') != 0:
            data = '[' + data + ']'
        return data

    def insert_commas(self, data):
        data = re.sub("}\s*{", "},{", data)
        return data

    def get_json_data(self):
        self.data = loads(self._fix_json(self.content))

    def get_service_tag(self, directory):
        self.tag = directory.split('-')[0]

    def split_by_term(self, data):
        last_index = 0
        first_index = 0
        result = list()
        for d in self.term_index(data):
            if d == first_index:
                continue
            first_index = d
            result.append(self.list_to_dict(data[last_index:first_index]))
            last_index = first_index
        self.data = result

    def term_index(self, data):
        for index, value in enumerate(data):
            if self.descriptor in value:
                yield index
        else:
            yield len(data)

    def list_to_dict(self, list_):
        '''
        Takes a string and a delimiter then splits into key values.
        returns a dict
        '''
        result = dict()
        key, value = (0, -1)
        for string in list_:
            spec = string.split(self.delimiter)
            result.update({ spec[key].replace(' ','') : spec[value].strip() })
        return result

    def filter_empty_terms(self, dict_):
        '''
        Takes a dict of parts info and returns any that don't
        match empty terms
        '''
        key = list(self.empty_terms)[0]
        terms = self.empty_terms[key]
        return not any(term for term in terms if term in dict_[key])

    def extract_attributes(self):
        result = list()
        for data in self.data:
            result.append({ k: data[v] if isinstance(v,str) else data[v[0]][v[1]] for k,v in self.attributes.items()})
        return result


class MacAddressParse(BaseProcess):
    '''
    This class will extract mac address information
    based on a descriptor in a cards product name
    '''
    def __init__(self,file_path, descriptor, file_name='lshw-network.json'):
        super().__init__(file_path, file_name)
        self.descriptor = descriptor
        self.attributes = ['mac','tag']
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.get_json_data()
        return self.get_each_card()

    def get_each_card(self):
            if isinstance(self.data,list):
                for i in self.data:
                    if self._get_mac_address(self._is_product(i)):
                        return self._get_mac_address(self._is_product(i))
            elif isinstance(self.data,dict):
                return self._get_mac_address(self._is_product(self.data))

    def _get_mac_address(self, card):
        if card:
            
            return {'tag': self.tag, 'mac': card['serial']}

    def _is_product(self, card):
        if self.descriptor in card['product']:
            return card


class ServerParse(BaseProcess):
    def __init__(self,file_path):
        super().__init__(file_path)
        self.file_path = file_path
        self.content = None
        self.components = {
            'chassis' : ChassisParser(file_path),
            'cpu': CPUParser(file_path),
            'memory': MemoryParser(file_path),
            'drives': DriveParser(file_path),
            'network': NetworkParser(file_path),
        }
        self.attributes = self.collect_attributes()
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.process(directory)

    def collect_attributes(self):
        result = list()
        for key, value in self.components.items():
            result.append(value.attributes)
        return result

    def process(self,directory):
        tag = directory.split('-')[0]
        payload = dict()
        with open(self.file_path + '/' + directory) as f:
            pass


class MemoryParser(BaseProcess):
    def __init__(self, file_path, term='Size', file_name='dmi-memory.txt'):
        super().__init__(file_path, file_name)
        self.content = None
        self.descriptor = term
        self.attributes = [
            'Size',
            'Type',
            'TypeDetail',
            'Manufacturer',
            'SerialNumber',
            'PartNumber',
            'Rank',
            'Speed',
        ]
        self.empty_terms = {
            'Size': [
                'NoModuleInstalled'
            ]
        }
        # self.template = PrinterTemplate(self.attributes)

    def __call__(self,directory):
        self.extract_file_content(directory)
        self.split_by_term(self.content)
        return list(filter(self.filter_empty_terms, self.data))
        # return self.data


class CPUParser(BaseProcess):
    def __init__(self, file_path, file_name='lshw-processor.json'):
        super().__init__(file_path, file_name)
        self.attributes = {
            'make':'vendor',
            'model':'version',
            'speed':'size',
            'cores': ['configuration', 'cores'],
            'width': 'width',
            'threads': ['configuration', 'threads'],
        }
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.get_json_data()
        self.convert_speed()
        return self.extract_attributes()

    def convert_speed(self):
        for d in self.data:
            d['size'] = d['size'] / 1000**3

class DriveParser(BaseProcess):
    def __init__(self, file_path, term='physicaldrive', file_suffix='-drives.txt'):
        super().__init__(file_path)
        self.file_suffix = file_suffix
        self.descriptor = term
        self.make = None
        self.attributes = {
            'make': 'Make',
            'model': 'Model',
            'size': 'Size',
            'serial': 'SerialNumber',
            'type': 'DriveType',
            'interface': 'InterfaceType',
            'firmware': 'FirmwareRevision',
        }
        self.procedures = {
            'hp': self.hp_process,
            'dell': self.dell_process,
            'server': self.server_process,
        }
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.set_server_make(directory)
        self.extract_file_content(directory)
        self.split_by_term(self.content)
        self.process_by_make()
        return self.extract_attributes()

    def hp_process(self):
        self.data = list(map(self.split_hp_model_field, self.data[1:]))

    def dell_process(self):
        pass

    def server_process(self):
        pass

    def process_by_make(self):
        processor = self.procedures[self.make]
        processor()

    def split_hp_model_field(self, dict_):
        '''
        Takes a dict of HP drive attributes and will parse the 'Model'
        field into 'Make' and 'Model' values. This is because the hp utility 
        that produces this data puts this info together in the 'Model' attribute. 
        There will then be a new dict returned containing a new 'Make' field and the 
        existing 'Model' field will only contain the model info
        '''
        data = dict_['Model'].strip().split()
        dict_['Make'], dict_['Model'] = data
        return dict_

    def set_server_make(self, directory):
        files = os.listdir(self.path + '\\' + directory)
        for file in files:
            if file.find(self.file_suffix) > -1:
                self.make = file.split('-')[0]
                break
        self.file_name = self.make + self.file_suffix


class NetworkParser(BaseProcess):
    def __init__(self, file_path, file_name='lshw-network.json'):
        super().__init__(file_path, file_name)
        self.attributes = {
            'make': 'vendor',
            'model': 'product',
            'mac': 'serial',
        }
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        self.get_json_data()
        return self.extract_attributes()


class ChassisParser(BaseProcess):
    def __init__(self, file_path, file_name='dmi-system.txt'):
        super().__init__(file_path, file_name)
        self.attributes = [
            'Manufacturer',
            'ProductName',
            'SerialNumber',
        ]
        self.template = PrinterTemplate(self.attributes)

    def __call__(self, directory):
        self.extract_file_content(directory)
        return self.list_to_dict(self.content)


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




