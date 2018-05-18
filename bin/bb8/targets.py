import docker


class TargetOptions:
    def __init__(self, backup, restore, user):
        self.backup = backup
        self.restore = restore
        self.user = user

    @classmethod
    def from_data(cls, data):
        return TargetOptions(data.get("backup", True),
                             data.get("restore", True),
                             data.get("user", "root"))

    def __eq__(self, other):
        return self.backup == other.backup and self.restore == other.restore


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

    def __eq__(self, other):
        return self.id == other.id \
               and self.path == other.path \
               and self.options == other.options


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

    def __eq__(self, other):
        return self.id == other.id \
               and self.volume == other.volume \
               and self.options == other.options
