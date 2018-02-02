#!/usr/bin/env python3
from os.path import abspath, join
import docker

from logger import log_from_docker

client = docker.from_env()


def run_rsync(volumes, from_path, to_path, relative):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    # --delete = delete destination files not in source
    cmd = ["rsync", "-rv", "-e", "ssh", from_path, to_path, "--delete"]

    if relative:
        cmd = ["rsync", "-rv", "-e", "ssh", "--relative", from_path, to_path, "--delete"]

    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True)

    log_from_docker(container)


def create_volumes(settings, local_volume, volume_mode):
    mounted_volume = join("/", local_volume)
    return {abspath(settings.known_hosts_path): {"bind": "/root/.ssh/known_hosts", "mode": "rw"},
            abspath(settings.ssh_key_path): {"bind": "/root/.ssh/id_rsa", "mode": "ro"},
            local_volume: {"bind": "{}".format(mounted_volume), "mode": volume_mode}}


# local_volume can be an absolute path or a named volume
def backup_volume(settings, local_volume):
    starport = settings.starport
    volumes = create_volumes(settings, local_volume, "ro")

    destination_path = "{}@{}:{}".format(starport["user"],
                                         starport["addr"],
                                         starport["backup_location"])

    run_rsync(volumes, local_volume, destination_path, True)


def restore_volume(settings, local_volume):
    starport = settings.starport
    mounted_volume = join("/", local_volume)
    volumes = create_volumes(settings, local_volume, "rw")

    remote_path = "{}@{}:{}{}/".format(starport["user"],
                                       starport["addr"],
                                       starport['backup_location'],
                                       local_volume)

    run_rsync(volumes, remote_path, mounted_volume, False)
