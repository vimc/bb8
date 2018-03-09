#!/usr/bin/env python3
import logging

from logger import with_logging
from settings import load_settings, log_dir
from docker_rsync import restore_volume


def run_restore():
    settings = load_settings()
    starport = settings.starport
    logging.info("Restoring from {}: ".format(starport["addr"]))

    targets = list(t for t in settings.targets)
    for target in targets:
        logging.info("- " + target.id)
        target.before_restore()
        restore_volume(settings, target.name)


if __name__ == "__main__":
    print("Restoring targets from Starport. Output will be logged to " + log_dir)
    with_logging(run_restore)
