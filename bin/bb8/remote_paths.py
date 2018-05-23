import re
from os.path import join


class RemotePaths(object):
    def __init__(self, target_name, starport):
        self.host = "{user}@{addr}".format(**starport)
        self.remote_bucket_path = self._remote_bucket_path(target_name,
                                                           starport)

    def data(self, include_host=False):
        return self.get_path("data", include_host=include_host)

    def meta(self, include_host=False):
        return self.get_path("meta", include_host=include_host)

    def metadata_file(self, include_host=False):
        return join(self.meta(include_host=include_host), "metadata.json")

    def rsync_path(self):
        return self.data(include_host=True)

    def get_path(self, directory, include_host=False):
        path = "{bucket}/{directory}/".format(bucket=self.remote_bucket_path,
                                              directory=directory)
        if include_host:
            path = "{host}:{path}".format(host=self.host, path=path)
        return path

    @staticmethod
    def _remote_bucket_path(target_name, starport):
        backup_location = starport["backup_location"]
        p = "{backup_location}/{name}".format(
            backup_location=backup_location,
            name=target_name
        )
        return re.sub("/+", "/", p)
