#!/usr/bin/env python3
import logging
from os.path import isdir
from os import makedirs

from logger import with_logging
from settings import load_settings, log_dir
from docker_rsync import restore_volume


def run_restore():
    settings = load_settings()
    starport = settings.starport
    logging.info("Restoring from {}: ".format(settings.starport["addr"]))

    logging.info("The following directories are being restored:")
    targets = list(t for t in settings.directory_targets)
    for target in targets:
        path = target.path
        logging.info("- " + path)
        restore_volume(settings, path, starport)

    logging.info("The following named volumes are being restored:")
    targets = list(t for t in settings.volume_targets)
    for target in targets:
        name = target.name
        logging.info("- " + name)
        target.before_restore()
        restore_volume(settings, name, starport)


if __name__ == "__main__":
    print("Restoring targets from Starport. Output will be logged to " + log_dir)
    with_logging(run_restore)
