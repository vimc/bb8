#!/usr/bin/env python3
import logging
from datetime import date
from os import makedirs
from os.path import join, isdir
from subprocess import Popen, PIPE

from settings import load_settings, log_dir

def ensure_dir_exists(dir_path):
    if not isdir(dir_path):
        makedirs(dir_path)


def with_logging(do):
    ensure_dir_exists(log_dir)
    # Log everything to a rotating file
    filename = join(log_dir, "bb8_{}.log".format(date.today().isoformat()))
    log_format = "%(asctime)s    %(levelname)s    %(message)s"
    logging.basicConfig(filename=filename, level=logging.DEBUG, format=log_format)
    logging.info("*" * 60)
    # Also log info and higher messages to the console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s    %(message)s'))
    logging.getLogger('').addHandler(console)
    try:
        do()
    except Exception as e:
        logging.error("An error occurred:", exc_info=e)
        exit(-1)


def run_rsync(settings, path):
    cmd = ["rsync", "-r", "ssh", path, "root@{}".format(settings.starport_addr)]
    with Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            logging.info(line.strip())
        for line in p.stderr:
            logging.error(line.strip())

    if p.returncode not in [0, 1]:
        raise Exception("rsync returned error code {}".format(p.returncode))


def run():
    settings = load_settings()
    logging.info("Backing up to {}: ".format(settings.starport_addr))
    for target in settings.targets:
        logging.info("- " + target.id)

    logging.info("The following paths will be backed up:")
    paths = list(t.path for t in settings.targets)
    for path in paths:
        logging.info("- " + path)
        run_rsync(settings, path)

if __name__ == "__main__":
    print("Sending file to starport. Output will be logged to " + log_dir)
    with_logging(run)
