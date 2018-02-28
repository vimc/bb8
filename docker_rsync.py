#!/usr/bin/env python3
from os.path import join
from os import getuid, getgid
import docker

from logger import log_from_docker

client = docker.from_env()


def run_rsync(volumes, from_path, to_path, relative):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    # --delete = delete destination files not in source
    uid = getuid()
    gid = getgid()
    cmd = ["rsync", "-rv", "-e", "ssh", "--perms", "--owner", "--group", "--chown={}:{}".format(uid, gid),
           from_path, to_path, "--delete"]
    if relative:
        cmd.append("--relative")

    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True)

    log_from_docker(container)


def get_volume_args(settings, local_volume, volume_mode):
    mounted_volume = join("/", local_volume)
    return {
        settings.known_hosts_path: {"bind": "/root/.ssh/known_hosts", "mode": "rw"},
        settings.ssh_key_path: {"bind": "/root/.ssh/id_rsa", "mode": "ro"},
        local_volume: {"bind": mounted_volume, "mode": volume_mode}
    }


# local_volume can be an absolute path or a named volume
def backup_volume(settings, local_volume):
    starport = settings.starport
    volumes = get_volume_args(settings, local_volume, "ro")

    destination_path = "{user}@{addr}:{backup_location}".format(**starport)

    run_rsync(volumes, local_volume, destination_path, True)


def restore_volume(settings, local_volume):
    starport = settings.starport
    mounted_volume = join("/", local_volume)
    volumes = get_volume_args(settings, local_volume, "rw")

    remote_dir = "{user}@{addr}:{backup_location}".format(**starport)
    remote_path = "{}{}/".format(remote_dir, local_volume)

    run_rsync(volumes, remote_path, mounted_volume, False)
