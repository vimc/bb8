#!/usr/bin/env python3
from os.path import abspath, join
import docker

from logger import log_from_docker

client = docker.from_env()


# target_volume can be an absolute path or a named volume
def backup_volume(settings, local_volume, starport):
    mounted_volume = join("/", local_volume)
    volumes = {abspath(settings.known_hosts_path): {"bind": "/root/.ssh/known_hosts", "mode": "rw"},
               abspath(settings.ssh_key_path): {"bind": "/root/.ssh/id_rsa", "mode": "ro"},
               local_volume: {"bind": "{}".format(mounted_volume), "mode": "ro"}}

    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    destination_path = "{}@{}:{}".format(starport["user"],
                                         starport["addr"],
                                         starport["backup_location"])
    cmd = ["rsync", "-rv", "-e", "ssh", "--relative", mounted_volume, destination_path]

    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True)

    log_from_docker(container)


def restore_volume(settings, local_volume, starport):
    mounted_volume = join("/", local_volume)
    volumes = {abspath(settings.known_hosts_path): {"bind": "/root/.ssh/known_hosts", "mode": "rw"},
               abspath(settings.ssh_key_path): {"bind": "/root/.ssh/id_rsa", "mode": "ro"},
               local_volume: {"bind": "{}".format(mounted_volume), "mode": "rw"}}

    remote_path = "{}@{}:{}{}/".format(starport["user"],
                                       starport["addr"],
                                       starport['backup_location'],
                                       local_volume)
    cmd = ["rsync", "-rv", "-e", "ssh", remote_path, mounted_volume]
    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True)

    log_from_docker(container)
