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

    def check(self):
        self.new_files = os.listdir(self.path)
        result = self._compare()
        self.old_files = self.new_files
        return result

    def watch(self, tasks):
        '''
        This method will start a loop which is intended to be 
        used in a main script.

        It will continue to check a directory for newly added or changed files and folders.
        Any new directories will be capture as a list and passed to task objects. These tasks
        are given as a list at call time.

        Example:
            watcher.watch([task1,task2,task3])

        Parameters:
            tasks = object or function (object must be callable)

        Returns:
            None (this method has side effects)
        '''
        while True:
            result = self.check()
            if result != None:
                [ task(result) for task in tasks ]

