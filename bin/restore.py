#!/usr/bin/env python3
import logging

from logger import with_logging
from settings import load_settings, log_dir
from docker_rsync import restore_volume
import docker


def run_restore():
    settings = load_settings()
    starport = settings.starport
    logging.info("Restoring from {}: ".format(starport["addr"]))
    logging.info("Remote directory: {}".format(starport["backup_location"]))

    targets = list(t for t in settings.targets)
    docker_client = docker.client.from_env()
    for target in targets:
        logging.info("- " + target.id)
        target.before_restore(docker_client)
        restore_volume(settings, target.name, target.mount_id)


if __name__ == "__main__":
    with_logging(run_restore)
