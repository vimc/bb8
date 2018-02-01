#!/usr/bin/env python3
from os.path import abspath
import docker

from logger import log_from_docker
from settings import docker_ssh_key_path

client = docker.from_env()


def backup_volume(settings, target_volume, cmd):
    volumes = {abspath(settings.known_hosts_path): {"bind": "/root/.ssh/known_hosts", "mode": "ro"},
               abspath(settings.ssh_key_path): {"bind": docker_ssh_key_path, "mode": "ro"},
               target_volume: {"bind": "/{}".format(target_volume), "mode": "ro"}}

    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True)

    log_from_docker(container)


def restore_volume(settings, target_volume, cmd):
    volumes = {abspath(settings.known_hosts_path): {"bind": "/root/.ssh/known_hosts", "mode": "ro"},
               abspath(settings.ssh_key_path): {"bind": docker_ssh_key_path, "mode": "ro"},
               target_volume: {"bind": "/{}".format(target_volume), "mode": "rw"}}

    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True)

    log_from_docker(container)
