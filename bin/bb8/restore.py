#!/usr/bin/env python3
import logging

from .docker_rsync import DockerRsync
from .settings import load_settings, log_dir


def run_restore(settings_source=load_settings, rsync=DockerRsync()):
    logging.info("Restoring targets from Starport. Output will be logged "
                 "to {}".format(log_dir))
    settings = settings_source()
    starport = settings.starport
    logging.info("Restoring from {}: ".format(starport["addr"]))
    logging.info("Remote directory: {}".format(starport["backup_location"]))

    targets = list(t for t in settings.targets)
    for target in targets:
        logging.info("- " + target.id)
        if target.options.restore:
            target.before_restore()
            rsync.restore_volume(settings, target.name, target.mount_id)
        else:
            template = "  (Skipping restoring {} - restore is false in config)"
            logging.info(template.format(target.name))
