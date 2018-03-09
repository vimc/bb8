#!/usr/bin/env python3
import logging
from os import getuid, getgid
from os.path import join

import docker

from logger import log_from_docker

client = docker.from_env()


def run_rsync(volumes, from_path, to_path, relative):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    # --delete = delete destination files not in source
    # --info=progress2 - print overall progress
    uid = getuid()
    gid = getgid()
    cmd = ["rsync", "-rv", "-e", "ssh", "--perms", "--owner", "--group", "--chown={}:{}".format(uid, gid),
           from_path, to_path, "--delete", "--info=progress2"]
    if relative:
        cmd.append("--relative")

    logging.debug("Running rsync in docker with: " + " ".join(cmd))
    logging.debug("Volume mapping: " + str(volumes))
    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True, remove=True)

    try:
        log_from_docker(container)
    except KeyboardInterrupt as e:
        logging.warning("Stopping container " + container.name)
        container.stop()
        raise e


def get_volume_args(settings, local_volume, volume_mode):
    mounted_volume = join("/", local_volume)
    return {
        "bb8_ssh": {"bind": "/root/.ssh", "mode": "rw"},
        local_volume: {"bind": mounted_volume, "mode": volume_mode}
    }


def get_remote_dir(starport):
    return "bb8@{}:{}".format(starport["addr"], starport["backup_location"])


# local_volume can be an absolute path or a named volume
def backup_volume(settings, local_volume):
    starport = settings.starport
    volumes = get_volume_args(settings, local_volume, "ro")

    remote_dir = get_remote_dir(starport)

    run_rsync(volumes, local_volume, remote_dir, True)


def restore_volume(settings, local_volume):
    starport = settings.starport
    mounted_volume = join("/", local_volume)
    volumes = get_volume_args(settings, local_volume, "rw")

    remote_dir = get_remote_dir(starport)
    remote_path = "{}{}/".format(remote_dir, local_volume)

    logging.info("Restoring from {} to {}".format(remote_path, local_volume))
    run_rsync(volumes, remote_path, mounted_volume, False)
