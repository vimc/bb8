#!/usr/bin/env python3
import logging
from os.path import abspath
import docker

from logger import with_logging, run_cmd_with_logging
from settings import load_settings, log_dir, docker_ssh_key_path, docker_known_hosts_path
from docker_rsync import run_rsync_from_container

client = docker.from_env()


def rsync_from_starport(ssh_key_path, known_hosts_path, target_path, starport):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    ssh_cmd = "ssh -o IdentityFile={} -o IdentitiesOnly=yes -o UserKnownHostsFile={}" \
        .format(ssh_key_path, known_hosts_path)
    source_path = "{}@{}:{}".format(starport["user"],
                                    starport["addr"],
                                    starport["backup_location"])
    args = ["rsync", "-rv", "-e", ssh_cmd, source_path, target_path]
    return args


def run_rsync(settings, path):
    starport = settings.starport
    cmd = rsync_from_starport(abspath(settings.known_hosts_path), abspath(settings.ssh_key_path), path, starport)
    run_cmd_with_logging(cmd)


def run_restore():
    settings = load_settings()
    logging.info("Backing up to {}: ".format(settings.starport["addr"]))

    logging.info("The following directories are being restored:")
    targets = list(t for t in settings.directory_targets)
    for target in targets:
        path = target.path
        logging.info("- " + path)
        target.before_restore()
        run_rsync(settings, path)

    logging.info("The following named volumes are being restored:")
    targets = list(t for t in settings.volume_targets)
    for target in targets:
        name = target.name
        logging.info("- " + name)
        target.before_restore()
        cmd = rsync_from_starport(docker_ssh_key_path, docker_known_hosts_path, name, settings.starport)
        run_rsync_from_container(settings, name, cmd)


if __name__ == "__main__":
    print("Restoring targets from Starport. Output will be logged to " + log_dir)
    with_logging(run_restore)
