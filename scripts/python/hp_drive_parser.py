#!/bin/usr python3

from itertools import islice

FILE_PATH = '..\\..\\sample_info\\server-specs\\USE014NF5K-spec'
FILE = 'hp-drives.txt'
TERM = 'drive'

with open(FILE_PATH + '\\' + FILE, 'r') as f:
    drive_file = f.read()

file_lines = drive_file.split('\n')


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


def get_context(term,lines):
    '''
    Get the end index for each start index in a list

    example:
    get_context('drive',)
    > [3,8]
    '''
    start_index = term_index(term,lines)
    end_index = list()

    for index, value in enumerate(lines):
        if start_index[index+1:] == []:
            end_index.append(len(lines))
            context = list(zip(start_index, end_index))
            break
        end_index.append(start_index[index+1] -1 )

    return sublist(context,lines)


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
    result = dict()

    for line in lines:
        line = line.strip()
        spec = line.split(':')
        result[spec[0].replace(' ','').strip()] = spec[-1].strip()

    return result