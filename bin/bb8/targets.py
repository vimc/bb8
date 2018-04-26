import docker


class TargetOptions:
    def __init__(self, data):
        self.backup = data.get("backup", True)
        self.restore = data.get("restore", True)


class DirectoryTarget:
    def __init__(self, name, path, options):
        self.name = name
        self.path = path
        self.options = options

    @property
    def id(self):
        return "Directory: " + self.name

    @property
    def mount_id(self):
        return self.path

    def before_restore(self):
        pass


class NamedVolumeTarget:
    def __init__(self, name, volume, options, docker_client=None):
        self.name = name
        self.volume = volume
        self.options = options
        self.docker = docker_client or docker.client.from_env()

    @property
    def id(self):
        return "Named volume: " + self.name

    @property
    def mount_id(self):
        return self.volume

    def _volume_exists(self):
        return self.volume in [x.name for x in self.docker.volumes.list()]

    def before_restore(self):
        if not self._volume_exists():
            print("Creating docker volume with name '{}'".format(self.volume))
            self.docker.volumes.create(self.volume)
