#!/usr/bin/env python3
import logging

from .remote_file_manager import RemoteFileManager
from .remote_paths import RemotePaths
from .docker_rsync import DockerRsync
from .settings import load_settings, log_dir


class RestoreTask(object):
    def __init__(self, settings_source=load_settings, rsync=DockerRsync()):
        self.settings = settings_source()
        self.rsync = rsync

    def run(self):
        logging.info("Restoring targets from Starport. Output will be logged "
                     "to {}".format(log_dir))
        starport = self.settings.starport
        logging.info("Restoring from {}: ".format(starport["addr"]))
        logging.info("Remote directory: {}".format(starport["backup_location"]))

        targets = list(t for t in self.settings.targets)
        for target in targets:
            logging.info("- " + target.id)
            if target.options.restore:
                fm = RemoteFileManager(RemotePaths(target.name, starport))
                self.restore_target(target, fm)
            else:
                logging.info("  (Skipping restoring {} - "
                             "restore is false in config)".format(target.name))

    def restore_target(self, target, fm: RemoteFileManager):
        target.before_restore()
        self.rsync.restore_volume(target.mount_id, fm.get_rsync_path())


def run_restore():
    RestoreTask().run()
