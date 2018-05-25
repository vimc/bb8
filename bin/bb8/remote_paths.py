import re
from os.path import join


class RemotePaths(object):
    def __init__(self, target_name, starport):
        self.host = "{user}@{addr}".format(**starport)
        self.remote_bucket_path = self._remote_bucket_path(target_name,
                                                           starport)

    @property
    def data(self):
        return self._get_path("data")

    @property
    def meta(self):
        return self._get_path("meta")

    @property
    def metadata_file(self):
        return join(self.meta, "metadata.json")

    @property
    def rsync_path(self):
        return "{host}:{path}".format(host=self.host, path=self.data)

    def _get_path(self, directory):
        return "{bucket}/{directory}/".format(bucket=self.remote_bucket_path,
                                              directory=directory)

    @staticmethod
    def _remote_bucket_path(target_name, starport):
        backup_location = starport["backup_location"]
        p = "{backup_location}/{name}".format(
            backup_location=backup_location,
            name=target_name
        )
        return re.sub("/+", "/", p)
