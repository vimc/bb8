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

    def _volume_exists(self, docker):
        return self.volume in [x.name for x in docker.volumes.list()]

    def before_restore(self, docker):
        if not self._volume_exists(docker):
            print("Creating docker volume with name '{}'".format(self.volume))
            docker.volumes.create(self.volume)
            run(["docker", "volume", "create", "--name", self.volume], stdout=PIPE)
