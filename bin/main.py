#!/usr/bin/env python3

"""
Usage:
  bb8 backup
  bb8 restore
  bb8 init
  bb8 status [--json] [TARGET...]
  bb8 log list [--limit=<number>]
  bb8 log show [VERSION]

Options:
  --limit=<number>     How many log files to return [default: 10]
"""
import logging
import shutil
from os.path import join

from bb8.backup import run_backup
from bb8.inspect_logs import inspect_logs
from bb8.logger import with_logging
from bb8.restore import run_restore
from bb8.settings import ssh_key_path, known_hosts_path, root_path
from docopt import docopt

from bb8.status import print_status


def init():
    logging.info("Storing ssh key and known_hosts file in volume (mounted "
                 "at /bb8/etc/.ssh)")
    dest = join(root_path, ".ssh")
    shutil.copy(ssh_key_path, join(dest, "id_rsa"))
    shutil.copy(known_hosts_path, join(dest, "known_hosts"))
    logging.info("Saved secrets to secrets volume")


def run():
    args = docopt(__doc__)
    if args["backup"]:
        with_logging(run_backup)
    elif args["restore"]:
        with_logging(run_restore)
    elif args["init"]:
        with_logging(init)
    elif args["status"]:
        print_status(args)
    elif args["log"]:
        inspect_logs(args)


if __name__ == "__main__":
    run()
