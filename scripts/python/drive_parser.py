#!/bin/usr python3

import os

# ----- SETUP VARIABLES ------ #
FILE_PATH = 'C:\\Users\\Jon\\Documents\\Code\\inventory_audit\\sample_info\\server-specs'
DELL_FILE_PATH = 'C:\\Users\\Jon\\Documents\\Code\\inventory_audit\\sample_info\\server-specs\\6TJ74S1-spec'
HP_DRIVES = 'hp-drives.txt'
DELL_DRIVES = 'server-drives.txt'
TERM = 'drive'
HP_DRIVE_ATTRIBS = [
    "InterfaceType",
    "Size",
    "RotationalSpeed",
    "FirmwareRevision",
    "SerialNumber",
    "PHYTransferRate",
]

class DriveProcess(object):
    '''
    This class will be used to process the output files
    for hard drive information. It will take a file object and determine
    based on prefix whether how the information should be parsed.

    For now there will only be two manufactures. 

    Example:
    drive = DriveProcess(file_path)

    When the new instance is called it will return a list of dicts
    containing drive attributes
    '''

    def __init__(self, file_path):
        assert os.path.exists(file_path), "File path is not valid or does not exist"
        self.path = os.path.abspath(file_path)
        self.files = self.get_files(file_path)
        self.content = self.file_to_lines(self.files)


    def file_to_lines(self,files):
        result = dict()
        for d, l in files.items():
            result[d] = dict()
            for f in l:
                with open(self.path + '\\' + d + '\\' + f, 'r') as file:
                    result[d].update({f: file.read().split('\n')})

        return result 
                
            
    def get_files(self,file_path):
        dirs = os.listdir(file_path)
        files = dict()
        for d in dirs:
            files[d] = os.listdir(file_path + '\\' + d)

        return files




server_files = {
    'HP': {
        'path': FILE_PATH,
        'drives': {
            'file':'hp-drives.txt',
            'attributes': [
                "InterfaceType",
                "Make",
                "Model",
                "Size",
                "RotationalSpeed",
                "FirmwareRevision",
                "SerialNumber",
                "PHYTransferRate",
            ],
            'split-term': 'drive',
            'process': ''
        },
        'memory': 'dmi-memory.txt',
        'system': 'dmi-system.txt',
        'hpdiscovery': 'hpdiscovery-report.xml',
        'lshw': 'lshw-report.txt',
    },
    'DELL': {
        'path': DELL_FILE_PATH,
        'drives': {
            'file':'server-drives.txt',
            'attributes': [
                'RawSize',
                'DeviceFirmwareLevel',
                'Make',
                'Model',
                'Serial',
                'DeviceSpeed',
                'PDType'
            ],
            'split-term': 'Enclosure Device ID',
            'process': lambda drives : [ parse_megaraid_inquiry_field(drive) for drive in drives ],
            },
        'controller': 'server-adapter-spec.txt',
        'memory': 'dmi-memory.txt',
        'system': 'dmi-system.txt',
        'hpdiscovery': 'hpdiscovery-report.xml',
        'lshw': 'lshw-report.txt'
    }
}


def open_spec_file(brand, spec, path_list=server_files):
    '''
    Simple utility to make opening and setting up file test more quickley
    '''
    TERM = path_list[brand][spec]['split-term']
    with open(path_list[brand]['path'] + '\\' + path_list[brand][spec]['file'], 'r') as f:
        return f.read().split('\n')


# ------ BEGIN FUNCTIONS -------- #
def get_context(lines, term=TERM):
    '''
    Get the end index for each start index in a list

    example:
    get_context('drive',)
    > [3,8]
    '''
    if type(lines).__name__ == 'str':
        lines = lines.split('\n')

    start_index = term_index(term,lines)
    end_index = list()

    for index, value in enumerate(lines):
        if start_index[index+1:] == []:
            end_index.append(len(lines))
            context = list(zip(start_index, end_index))
            break
        end_index.append(start_index[index+1] -1 )

    return sublist(context,lines)


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
def term_index(term, lines):
    '''
    Small function that takes a list and a string and returns a list of line
    indexes where that term shows up
    '''
    result = list()

    for index, line in enumerate(lines):
        if term in line:
            result.append(index)

    return result


def sublist(bounds, lines):
    '''
    Takes a list and some indecies and returns a list of lists
    In other words it splits a list into chunks

    The intended use is for grouping lines from a file
    '''
    return [lines[i[0]:i[1]] for i in bounds]


def lines_to_dict(lines):
    '''
    Takes a list of file lines and converts it into a python dictionary

    This is a very specific tool used for how hp outputs the drive contents
    
    Example:
    lines_to_dict(file_lines)
    > {'physicaldrive': 1, 'SerialNumber': '12345hgfd'}
    '''
    if type(lines).__name__ != 'list':
        raise TypeError(
            "Argument needs to be of <class list>, "
            "<class {}> was given instead".format(type(lines).__name__)
            ,lines)

    result = dict()

    for line in lines:
        line = line.strip()
        spec = line.split(':')
        result[spec[0].replace(' ','').strip()] = spec[-1].strip()

    return result


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

