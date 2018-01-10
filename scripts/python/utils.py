'''
This is a module to contain some useful functions and classes
'''
import os
import re


class FileWatcher(object):
    '''
    Helper class that will perform checks against a directory
    for when new files and folders show up.
    '''

    def __init__(self, path, func):
        self.path = path
        self.func = func
        self.old_files = os.listdir(path)
        self.new_files = None

    def _compare(self):
        result = set(self.new_files) - set(self.old_files)
        if result != set():
            return list(result)

    def _check(self):
        self.new_files = os.listdir(self.path)
        result = self._compare()
        self.old_files = self.new_files
        return result

    def watch(self):
        while True:
            result = self._check()
            if result != None:
                [self.func("New file: {}".format(r)) for r in result]


def fix_json(data):
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