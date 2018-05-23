#!/usr/bin/env python3
import json
import logging
from os import getuid, getgid
from os.path import join

import docker
from shellescape import quote

from .logger import log_from_docker
from .remote_paths import RemotePaths


class DockerRsync(object):
    def __init__(self, client=docker.from_env()):
        self.client = client
        self._ssh_volume_bind = {"bind": "/root/.ssh", "mode": "ro"}

    def _run(self, **kwargs):
        return self.client.containers.run("instrumentisto/rsync-ssh", **kwargs)

    def _run_via_ssh(self, host, remote_cmd):
        return self._run(command=["ssh", host] + remote_cmd,
                         volumes={"bb8_ssh": self._ssh_volume_bind},
                         remove=True)

    def _run_rsync(self, volumes, from_path, to_path, relative):
        chown = "{}:{}".format(getuid(), getgid())
        # Disable ssh compression:
        # https://galaxysd.github.io/20160302/Fastest-Way-Rsync
        ssh_cmd = "ssh -o Compression=no"

        cmd = ["rsync",
               # copy directories recursively
               "-r",
               # verbose - give info about what files are being transferred
               # and a brief summary at the end
               "-v",
               # specify remote shell program explicitly (i.e. ssh as opposed
               # to the default rsh)
               "-e", ssh_cmd,
               "--perms", "--owner", "--group",
               "--chown=" + chown,
               # delete destination files not in source
               "--delete",
               # print overall progress
               "--info=progress2",
               # preserve timestamps
               "--times",
               from_path,
               to_path
               ]
        if relative:
            cmd.append("--relative")

        logging.debug("Running rsync in docker with: " + " ".join(cmd))
        logging.debug("Volume mapping: " + str(volumes))
        container = self._run(command=cmd, volumes=volumes,
                              detach=True, remove=True)

        try:
            log_from_docker(container)
        except KeyboardInterrupt as e:
            logging.warning("Stopping container " + container.name)
            container.stop()
            raise e

    def _get_volume_args(self, local_volume, volume_mode):
        mounted_volume = join("/", local_volume)
        return {
            "bb8_ssh": self._ssh_volume_bind,
            local_volume: {"bind": mounted_volume, "mode": volume_mode}
        }

    def _make_remote_dir(self, host, path):
        self._run_via_ssh(host, ["mkdir", "-p", path])

    def _create_target_dirs(self, paths: RemotePaths):
        self._make_remote_dir(paths.host, paths.data())
        self._make_remote_dir(paths.host, paths.meta())

    def _write_metadata(self, metadata, paths: RemotePaths):
        metadata = json.dumps(metadata)
        path = join(paths.meta(), "metadata.json")
        cmd = "echo {data} > {path}".format(data=quote(metadata), path=path)
        self._run_via_ssh(paths.host, [cmd])

    # local_volume can be an absolute path or a named volume
    def backup_volume(self, local_volume, metadata, remote_paths: RemotePaths):
        volumes = self._get_volume_args(local_volume, "ro")

        remote_path = remote_paths.data(include_host=True)
        logging.info("Backing up to {} from {}".format(remote_path,
                                                       local_volume))
        self._create_target_dirs(remote_paths)
        self._run_rsync(volumes, local_volume, remote_path, relative=True)
        self._write_metadata(metadata, remote_paths)

    def restore_volume(self, local_volume, remote_paths: RemotePaths):
        mounted_volume = join("/", local_volume)
        volumes = self._get_volume_args(local_volume, "rw")

        remote_path = "{}{}/".format(remote_paths.data(include_host=True),
                                     local_volume)

        logging.info("Restoring from {} to {}".format(remote_path,
                                                      local_volume))
        self._run_rsync(volumes, remote_path, mounted_volume, relative=False)
