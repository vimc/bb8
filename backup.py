#!/usr/bin/env python3
import logging
from datetime import date
from os import makedirs
from os.path import join, isdir, abspath
from subprocess import Popen, PIPE
import docker

from logger import with_logging, run_cmd_with_logging
from settings import load_settings, log_dir, docker_ssh_key_path, docker_known_hosts_path
from docker_rsync import backup_volume

client = docker.from_env()


def ensure_dir_exists(dir_path):
    if not isdir(dir_path):
        makedirs(dir_path)


def rsync_cmd(ssh_key_path, known_hosts_path, target_path, starport):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    ssh_cmd = "ssh -o IdentityFile={} -o IdentitiesOnly=yes -o UserKnownHostsFile={}" \
        .format(ssh_key_path, known_hosts_path)
    destination_path = "{}@{}:{}".format(starport["user"],
                                         starport["addr"],
                                         starport["backup_location"])
    args = ["rsync", "-rv", "-e", ssh_cmd, "--relative", target_path, destination_path]
    return args


def run_rsync(settings, path):
    starport = settings.starport
    cmd = rsync_cmd(abspath(settings.ssh_key_path), abspath(settings.known_hosts_path), path, starport)
    run_cmd_with_logging(cmd)


def run_backup():
    settings = load_settings()
    logging.info("Backing up to {}: ".format(settings.starport["addr"]))

    logging.info("The following directories are being backed up:")
    paths = list(t.path for t in settings.directory_targets)
    for path in paths:
        logging.info("- " + path)
        run_rsync(settings, path)

    logging.info("The following named volumes are being backed up:")
    names = list(t.name for t in settings.volume_targets)
    for name in names:
        logging.info("- " + name)
        cmd = rsync_cmd(docker_ssh_key_path, docker_known_hosts_path, name, settings.starport)
        backup_volume(settings, name, cmd)


if __name__ == "__main__":
    print("Backing up targets to Starport. Output will be logged to " + log_dir)
    with_logging(run_backup)
