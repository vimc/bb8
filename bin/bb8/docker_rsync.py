#!/usr/bin/env python3
import logging
import re
from os import getuid, getgid
from os.path import join

import docker

from .logger import log_from_docker


class DockerRsync(object):
    def __init__(self, client=docker.from_env()):
        self.client = client
        self._ssh_volume_bind = {"bind": "/root/.ssh", "mode": "ro"}

    def _run(self, **kwargs):
        return self.client.containers.run("instrumentisto/rsync-ssh", **kwargs)

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

    def _get_host(self, starport):
        return "{user}@{addr}".format(**starport)

    def _get_target_path(self, backup_location, name):
        template = "{backup_location}/{name}"
        dir = template.format(name=name, backup_location=backup_location)
        return re.sub("/+", "/", dir)

    def _get_remote_data_dir(self, host, target_path):
        return "{host}:{target_path}/data/".format(host=host,
                                                   target_path=target_path)

    def _make_remote_dir(self, host, path):
        self._run(command=["ssh", host, "mkdir", "-p", path],
                  volumes={"bb8_ssh": self._ssh_volume_bind},
                  remove=True)

    def _create_target_dirs(self, host, target_path):
        self._make_remote_dir(host, join(target_path, "data"))
        self._make_remote_dir(host, join(target_path, "meta"))

    def _validate_instance(self, host, name, target_path, instance_guid):
        remote_id = self._run(command=["ssh", host, "less", target_path],
                              volumes={"bb8_ssh": self._ssh_volume_bind},
                              remove=True)
        if len(remote_id) == 0:
            self._save_instance_guid(host, target_path, instance_guid)
        else:
            if remote_id != instance_guid:
                raise Exception("This target has been backed up by a different instance of bb8: " + name)

    def _save_instance_guid(self, host, target_path, guid):
        self._run(command=["ssh", host, "echo", guid, ">", target_path],
                  volumes={"bb8_ssh": self._ssh_volume_bind},
                  remove=True)

    # local_volume can be an absolute path or a named volume
    def backup_volume(self, settings, name, local_volume):
        starport = settings.starport
        volumes = self._get_volume_args(local_volume, "ro")

        host = self._get_host(starport)
        target_path = self._get_target_path(starport["backup_location"], name)
        remote_dir = self._get_remote_data_dir(host, target_path)

        self._create_target_dirs(host, target_path)
        self._validate_instance(host, name, join(target_path, "meta", "guid"), settings.instance_guid)
        self._run_rsync(volumes, local_volume, remote_dir, True)

    def restore_volume(self, settings, name, local_volume):
        starport = settings.starport
        mounted_volume = join("/", local_volume)
        volumes = self._get_volume_args(local_volume, "rw")

        host = self._get_host(starport)
        target_path = self._get_target_path(starport["backup_location"], name)
        remote_dir = self._get_remote_data_dir(host, target_path)
        remote_path = "{}{}/".format(remote_dir, local_volume)

        logging.info(
            "Restoring from {} to {}".format(remote_path, local_volume))
        self._run_rsync(volumes, remote_path, mounted_volume, False)
