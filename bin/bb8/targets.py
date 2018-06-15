import docker
import os


class TargetOptions:
    def __init__(self, backup, restore):
        self.backup = backup
        self.restore = restore

    @classmethod
    def from_data(cls, data):
        return TargetOptions(data.get("backup", True),
                             data.get("restore", True))

    def __eq__(self, other):
        return self.backup == other.backup and self.restore == other.restore


class DirectoryTarget:
    def __init__(self, name, path, options, docker_client=None):
        self.name = name
        self.path = path
        self.options = options
        self.docker = docker_client or docker.client.from_env()

    @property
    def id(self):
        return "Directory: " + self.name

    @property
    def mount_id(self):
        return self.path

    def before_restore(self):
        pass

    def exists_locally(self):
        volumes = {self.mount_id: {"bind": "/data", "mode": "ro"}}
        output = self.docker.containers.run("bash",
                                            command=["bash", "-c", '[ -d /data ] && echo 1'],
                                            volumes=volumes,
                                            remove=True).decode('utf-8').strip()
        return output == "1"

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

    def exists_locally(self):
        return self.mount_id in [v.id for v in self.docker.volumes.list()]

    def __eq__(self, other):
        return self.id == other.id \
               and self.volume == other.volume \
               and self.options == other.options
