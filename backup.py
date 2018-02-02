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

    targets = list(t for t in settings.targets)
    for target in targets:
        logging.info("- " + target.id)
        backup_volume(settings, target.name)


if __name__ == "__main__":
    print("Backing up targets to Starport. Output will be logged to " + log_dir)
    with_logging(run_backup)
