#!/usr/bin/env python3
from datetime import datetime
import logging

import docker
from tzlocal import get_localzone

from .remote_file_manager import RemoteFileManager
from .remote_paths import RemotePaths
from .docker_rsync import DockerRsync
from .settings import load_settings, log_dir, Settings

client = docker.from_env()


class BackupTask(object):
    def __init__(self, settings_source=load_settings, rsync=DockerRsync()):
        self.settings = settings_source()
        self.rsync = rsync

    def run(self):
        logging.info("Backing up targets to Starport. Output will be logged "
                     "to {}".format(log_dir))
        starport = self.settings.starport
        logging.info("Backing up to {}: ".format(starport["addr"]))

        targets = list(t for t in self.settings.targets)
        for target in targets:
            logging.info("- " + target.id)
            if target.options.backup:
                fm = RemoteFileManager(RemotePaths(target.name, starport))
                self.backup_target(target, fm, self.settings)
            else:
                logging.info("  (Skipping backing up {} - "
                             "backup is false in config)".format(target.name))

    def backup_target(self, target, fm: RemoteFileManager, settings: Settings):
        fm.create_directories()
        fm.validate_instance(settings.instance_guid)
        self.rsync.backup_volume(target.mount_id, fm.get_rsync_path())
        fm.write_metadata(self.make_metadata(settings))

    def make_metadata(self, settings: Settings):
        now = datetime.now().astimezone(get_localzone()).isoformat()
        return {
            "last_backup": now,
            "instance_guid": settings.instance_guid
        }


def run_backup():
    BackupTask().run()