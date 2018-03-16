import logging
from subprocess import run, PIPE


class DirectoryTarget:
    def __init__(self, name, path):
        self.name = name
        self.path = path

    @property
    def id(self):
        return "Directory: " + self.name

    @property
    def mount_id(self):
        return self.path

    def before_restore(self):
        pass


class NamedVolumeTarget:
    def __init__(self, name, volume):
        self.name = name
        self.volume = volume

    @property
    def id(self):
        return "Named volume: " + self.name

    @property
    def mount_id(self):
        return self.volume

    def _volume_exists(self):
        text = run(
            ["docker", "volume", "ls", "-q"],
            stdout=PIPE, universal_newlines=True
        ).stdout
        names = text.split('\n')
        return self.volume in names

    def before_restore(self):
        if not self._volume_exists():
            logging.info("Creating docker volume with name '{}'".format(self.name))
            run(["docker", "volume", "create", "--name", self.volume], stdout=PIPE)
