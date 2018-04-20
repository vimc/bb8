#!/usr/bin/env python3

"""
Usage:
  main.py backup
  main.py restore
  main.py init
  main.py log --list [--limit=<number>]
  main.py log [--version=<version>]

Options:
  --version=<version>  Which version of the logs to display (defaults to most
                       recent)
  --list               Show all available log files (versions)
  --limit=<number>     How many log files to return [default: 10]
"""
import logging
import shutil
from os.path import join

from docopt import docopt

from backup import run_backup
from inspect_logs import inspect_logs
from logger import with_logging
from restore import run_restore
from settings import ssh_key_path, known_hosts_path, root_path


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
    elif args["log"]:
        inspect_logs(args)


if __name__ == "__main__":
    run()
