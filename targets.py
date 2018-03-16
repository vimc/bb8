import logging
import docker


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
    def __init__(self, name, volume, docker_client=None):
        self.name = name
        self.volume = volume
        self.docker = docker_client or docker.client.from_env()

    @property
    def id(self):
        return "Named volume: " + self.name

    @property
    def mount_id(self):
        return self.volume

    def _volume_exists(self):
        try:
            self.docker.volumes.get(self.volume)
            return True
        except:
            docker.errors.NotFound
            return False

    def before_restore(self):
        if not self._volume_exists():
            logging.info("Creating docker volume with name '{}'".format(
                self.volume))
            self.docker.volumes.create(self.volume)
