#!/bin/usr python3

# ----- SETUP VARIABLES ------ #
HP_FILE_PATH = 'C:\\Users\\Jon\\Documents\\Code\\inventory_audit\\sample_info\\server-specs\\USE014NF5K-spec'
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

server_files = {
    'HP': {
        'path': HP_FILE_PATH,
        'drives': {
            'file':'hp-drives.txt',
            'attributes': [
                "InterfaceType",
                "Size",
                "RotationalSpeed",
                "FirmwareRevision",
                "SerialNumber",
                "PHYTransferRate",
            ],
            'split-term': 'drives'
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
            'split-term': 'Enclosure Device ID'
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


def process_drive_list(drive_list):
    '''
    Takes a list of list and returns a list of dicts

    Using a lot of the utility functions this, function processes
    sub lists into easier to use dictionaries for later usage

    One of those intended uses is converting to json and then sending to a 
    RESTful API

    example:
    process_drive_list([
        ['spec1: value1', '   spec2: value2'],
        ['spec1: value1', '   spec2: value2']
    ]) 
    > [
        {'spec1': 'value1', 'spec2': 'value2'},
        {'spec1': 'value1', 'spec2': 'value2'}
        ]
    '''
    try:
        return [get_hp_drive_attributes(lines_to_dict(drive)) for drive in drive_list]
    except:
        print("Could not process drive list")


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


def get_hp_drive_attributes(dict_, attribs=server_files['HP']['drives']['attributes']):
    '''
    Take a dictionary of HP drive specs and return a new dictionary of specs 
    based on a given list
    '''
    try:
        assert type(dict_).__name__ == 'dict', "Need to make sure to pass in a dict"
        return { key: dict_[key] for key in attribs }
    except KeyError:
        print("Key value does not exist in your list or dict argument")


def parse_megaraid_inquery_field(dict_):
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
