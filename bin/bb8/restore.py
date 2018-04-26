#!/usr/bin/env python3
import logging

from bb8.docker_rsync import DockerRsync
from bb8.settings import load_settings


def run_restore(settings=load_settings(), rsync=DockerRsync()):
    starport = settings.starport
    logging.info("Restoring from {}: ".format(starport["addr"]))
    logging.info("Remote directory: {}".format(starport["backup_location"]))

    targets = list(t for t in settings.targets)
    for target in targets:
        logging.info("- " + target.id)
        if target.options.restore:
            target.before_restore()
            rsync.restore_volume(settings, target.mount_id)
        else:
            template = "  (Skipping restoring {} - restore is false in config)"
            logging.info(template.format(target.name))
