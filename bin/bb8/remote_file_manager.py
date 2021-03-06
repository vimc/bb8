import json

import docker
from shellescape import quote

from .remote_paths import RemotePaths


def default_metadata():
    return {
        "last_backup": None,
        "instance_guid": None
    }


class RemoteFileManager(object):
    def __init__(self, paths: RemotePaths, docker_client=docker.from_env()):
        self.paths = paths
        self.docker_client = docker_client

    def run_remote_cmd(self, remote_cmd):
        cmd = ["ssh", self.paths.host, remote_cmd]
        volumes = {
            "bb8_ssh": {"bind": "/root/.ssh", "mode": "ro"}
        }
        return self.docker_client.containers.run("instrumentisto/rsync-ssh",
                                                 command=cmd,
                                                 volumes=volumes,
                                                 remove=True)

    def get_metadata(self):
        # The '|| true' makes the command exit with status 0 and return the
        # empty string if the file doesn't exist
        remote_cmd = 'cat {path} || true'.format(path=self.paths.metadata_file)
        output = self.run_remote_cmd(remote_cmd)
        if output:
            return json.loads(output)
        else:
            return default_metadata()

    def write_metadata(self, metadata):
        json_content = json.dumps(metadata)
        path = self.paths.metadata_file
        cmd = "echo {data} > {path}".format(data=quote(json_content), path=path)
        self.run_remote_cmd(cmd)

    def _make_remote_dir(self, path):
        self.run_remote_cmd("mkdir -p {}".format(path))

    def create_directories(self):
        self._make_remote_dir(self.paths.data)
        self._make_remote_dir(self.paths.meta)

    def get_rsync_path(self):
        return self.paths.rsync_path

    def validate_instance(self, local_guid):
        metadata = self.get_metadata()
        remote_guid = metadata.get("instance_guid", None)
        if remote_guid and local_guid and remote_guid != local_guid:
            raise Exception("Target {} has been backed up by a different "
                            "instance of bb8.".format(self.paths.target_name))
