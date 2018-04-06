#!/usr/bin/env python3

"""
Usage:
  main.py backup
  main.py restore
  main.py init
"""
import shutil
from os.path import join

from docopt import docopt

from backup import run_backup
from logger import with_logging
from restore import run_restore
from settings import log_dir, ssh_key_path, known_hosts_path, root_path


def run():
    args = docopt(__doc__)
    if args["backup"]:
        print("Backing up targets to Starport. Output will be logged to " + log_dir)
        run_backup()
    elif args["restore"]:
        print("Restoring targets from Starport. Output will be logged to " + log_dir)
        run_restore()
    elif args["init"]:
        print("Storing ssh key and known_hosts file in volume (mounted at "
              "/bb8/etc/.ssh)")
        dest = join(root_path, ".ssh")
        shutil.copy(ssh_key_path, join(dest, "id_rsa"))
        shutil.copy(known_hosts_path, join(dest, "known_hosts"))


if __name__ == "__main__":
    with_logging(run)

