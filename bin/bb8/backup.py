#!/usr/bin/env python3
from datetime import datetime
import logging

import docker
from tzlocal import get_localzone

from .remote_file_manager import RemoteFileManager
from .remote_paths import RemotePaths
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
            fm = RemoteFileManager(RemotePaths(target.name, starport))
            backup_target(target, fm, rsync)
        else:
            template = "  (Skipping backing up {} - backup is false in config)"
            logging.info(template.format(target.name))


def backup_target(target, fm: RemoteFileManager, rsync: DockerRsync):
    fm.create_directories()
    rsync.backup_volume(target.mount_id, fm.paths.rsync_path())
    fm.write_metadata(make_metadata())


def make_metadata():
    return {
        "last_backup": datetime.now().astimezone(get_localzone()).isoformat()
    }
