#!/usr/bin/env python3
import logging
import docker

from logger import with_logging
from settings import load_settings, log_dir
from docker_rsync import backup_volume

client = docker.from_env()


def run_backup():
    settings = load_settings()
    starport = settings.starport
    logging.info("Backing up to {}: ".format(starport["addr"]))

    logging.info("The following directories are being backed up:")
    paths = list(t.path for t in settings.directory_targets)
    for path in paths:
        logging.info("- " + path)
        backup_volume(settings, path)

    logging.info("The following named volumes are being backed up:")
    names = list(t.name for t in settings.volume_targets)
    for name in names:
        logging.info("- " + name)
        backup_volume(settings, name)


if __name__ == "__main__":
    print("Backing up targets to Starport. Output will be logged to " + log_dir)
    with_logging(run_backup)
