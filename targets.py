from os import makedirs
from os.path import isdir

class DirectoryTarget:
    def __init__(self, path):
        self.path = path

    @property
    def id(self):
        return "Directory: " + self.path

    def before_restore(self):
        if not isdir(self.path):
            print("Creating empty directory " + self.path)
            makedirs(self.path)
