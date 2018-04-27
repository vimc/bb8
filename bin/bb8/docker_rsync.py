#!/usr/bin/env python3
import logging
from os.path import join

import docker

from .logger import log_from_docker


class DockerRsync(object):
    def __init__(self, client=docker.from_env()):
        self.client = client

    def _run_rsync(self, mode, volumes, from_path, to_path, local_user="root"):
        """Rsyncs from from_path to to_path. In a backup, from_path with be
        local and to_path will be remote. In a restore, the reverse is true.

        When restoring you can provide a local_user. Restored files will be
        owned by this user."""

        if mode not in ["backup", "restore"]:
            raise Exception("Invalid rsync mode: {}".format(mode))

        cmd = ["rsync",
               # copy directories recursively
               "-r",
               # verbose - give info about what files are being transferred
               # and a brief summary at the end
               "-v",
               # specify remote shell program explicitly (i.e. ssh as opposed
               # to the default rsh)
               "-e", "ssh",
               # preserve permissions
               "--perms",
               # delete destination files not in source
               "--delete",
               # print overall progress
               "--info=progress2",
               from_path,
               to_path
               ]

        if mode == "backup":
            # Not sure what this does
            cmd.append("--relative")
        elif mode == "restore":
            # set owner when restoring
            cmd.append("--chown={}:{}".format(local_user, local_user))

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

    def _get_remote_dir(self, starport):
        return "{user}@{addr}:{backup_location}".format(**starport)

    # local_volume can be an absolute path or a named volume
    def backup_volume(self, settings, local_volume):
        starport = settings.starport
        volumes = self._get_volume_args(local_volume, "ro")

        remote_dir = self._get_remote_dir(starport)

        self._run_rsync("backup", volumes, local_volume, remote_dir)

    def restore_volume(self, settings, local_volume, local_user):
        starport = settings.starport
        mounted_volume = join("/", local_volume)
        volumes = self._get_volume_args(local_volume, "rw")

        remote_dir = self._get_remote_dir(starport)
        remote_path = "{}{}/".format(remote_dir, local_volume)

        logging.info(
            "Restoring from {} to {}".format(remote_path, local_volume))
        self._run_rsync("restore", volumes, remote_path, mounted_volume,
                        local_user)
