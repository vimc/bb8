#!/usr/bin/env python3
import logging

import docker

from .docker_rsync import DockerRsync
from .settings import load_settings, log_dir

client = docker.from_env()


def run_backup(settings_source=load_settings, rsync=DockerRsync()):
    logging.info("Backing up targets to Starport. Output will be logged "
                 "to {}".format(log_dir))
    settings = settings_source()
    starport = settings.starport
    logging.info("Backing up to {}: ".format(starport["addr"]))

    targets = list(t for t in settings.targets)
    for target in targets:
        logging.info("- " + target.id)
        if target.options.backup:
            rsync.backup_volume(settings, target.mount_id)
        else:
            template = "  (Skipping backing up {} - backup is false in config)"
            logging.info(template.format(target.name))
