#!/usr/bin/env python3
import logging

import docker

from docker_rsync import backup_volume
from settings import load_settings

client = docker.from_env()


def run_backup():
    settings = load_settings()
    starport = settings.starport
    logging.info("Backing up to {}: ".format(starport["addr"]))

    targets = list(t for t in settings.targets)
    for target in targets:
        logging.info("- " + target.id)
        if target.options.backup:
            backup_volume(settings, target.mount_id)
        else:
            template = "  (Skipping backing up {} - backup is false in config)"
            logging.info(template.format(target.name))
