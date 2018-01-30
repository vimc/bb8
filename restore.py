#!/usr/bin/env python3
import logging
from os.path import abspath
import docker

from logger import with_logging, run_cmd_with_logging
from settings import load_settings, log_dir, docker_ssh_key_path
from docker_rsync import run_rsync_from_container

client = docker.from_env()


def rsync_from_starport(ssh_key_path, target_path, starport):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    args = ["rsync", "-rv", "-e", "ssh -o IdentityFile={} -o IdentitiesOnly=yes".format(ssh_key_path),
            "{}@{}:{}".format(starport["user"], starport["addr"], starport["backup_location"]), target_path]
    print(args)
    return args


def run_rsync(settings, path):
    starport = settings.starport
    cmd = rsync_from_starport(abspath(settings.ssh_key_path), path, starport)
    run_cmd_with_logging(cmd)


def run_backup():
    settings = load_settings()
    logging.info("Backing up to {}: ".format(settings.starport["addr"]))

    logging.info("The following directories are being restored:")
    paths = list(t.path for t in settings.directory_targets)
    for path in paths:
        logging.info("- " + path)
        run_rsync(settings, path)

    logging.info("The following named volumes are being restored:")
    names = list(t.name for t in settings.volume_targets)
    for name in names:
        logging.info("- " + name)
        cmd = rsync_from_starport(docker_ssh_key_path, name, settings.starport)
        run_rsync_from_container(settings, name, cmd)


if __name__ == "__main__":
    print("Backing up targets to Starport. Output will be logged to " + log_dir)
    with_logging(run_backup)
