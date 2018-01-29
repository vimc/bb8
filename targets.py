from os import makedirs
from os.path import isdir
from subprocess import run, PIPE


class DirectoryTarget:
    def __init__(self, path):
        self.path = path

    @property
    def id(self):
        return "Directory: " + self.path


class NamedVolumeTarget:
    def __init__(self, name):
        self.name = name

    @property
    def id(self):
        return "Named volume: " + self.name

    def _volume_exists(self):
        text = run(
            ["docker", "volume", "ls", "-q"],
            stdout=PIPE, universal_newlines=True
        ).stdout
        names = text.split('\n')
        return self.name in names
