#!/usr/bin/env python3
import logging
from os import getuid, getgid
from os.path import join

import docker

from .logger import log_from_docker


class DockerRsync(object):
    def __init__(self, client=docker.from_env()):
        self.client = client

    def _run_rsync(self, volumes, from_path, to_path, relative):

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
               # preserve file permissions
               "--perms",
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
        container = self.client.containers.run("instrumentisto/rsync-ssh",
                                               command=cmd, volumes=volumes,
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
            "bb8_ssh": {"bind": "/root/.ssh", "mode": "ro"},
            local_volume: {"bind": mounted_volume, "mode": volume_mode}
        }

    # local_volume can be an absolute path or a named volume
    def backup_volume(self, local_volume, remote_path):
        volumes = self._get_volume_args(local_volume, "ro")

        logging.info("Backing up to {} from {}".format(remote_path,
                                                       local_volume))
        self._run_rsync(volumes, local_volume, remote_path, relative=True)

    def restore_volume(self, local_volume, remote_path):
        mounted_volume = join("/", local_volume)
        volumes = self._get_volume_args(local_volume, "rw")

        remote_path = "{}{}/".format(remote_path, local_volume)

        logging.info("Restoring from {} to {}".format(remote_path,
                                                      local_volume))
        self._run_rsync(volumes, remote_path, mounted_volume, relative=False)
