'''
This is a module to contain some useful functions and classes
'''
import os


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
            result = self._check():
            func(result, *args, **kwargs) if result != None else None
