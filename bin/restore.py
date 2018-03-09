#!/usr/bin/env python3
import logging

import docker

from docker_rsync import restore_volume
from settings import load_settings


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
        restore_volume(settings, target.mount_id)
