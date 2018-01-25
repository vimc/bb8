#!/usr/bin/env python3
import logging
from datetime import date
from os import makedirs
from os.path import join, isdir, abspath, expanduser
from subprocess import Popen, PIPE

from settings import load_settings, log_dir
from subprocess import run


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


def rsync_cmd(ssh_key_path, target_path, starport):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    return ["rsync", "-rve", "ssh -i {}".format(ssh_key_path), target_path,
            "{}@{}:{}".format(starport["user"], starport["addr"], starport["backup_location"])]


def run_cmd_with_logging(cmd):
    with Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            logging.info(line.strip())
        for line in p.stderr:
            logging.error(line.strip())

    if p.returncode != 0:
        raise Exception("rsync returned error code {}".format(p.returncode))


def run_rsync(settings, path):
    starport = settings.starport
    cmd = rsync_cmd(settings.ssh_key_path, path, starport)
    run_cmd_with_logging(cmd)


def run_rsync_from_container(settings, source_volume):
    starport = settings.starport
    docker_ssh_key_path = "/etc/id_rsa"

    cmd = ["docker", "run", "--rm", "-i", "-t",
           "-v", "{}:/{}".format(source_volume, source_volume),
           "-v", "{}:{}".format(expanduser("~/.ssh/known_hosts"), "/root/.ssh/known_hosts"),
           "-v", "{}:{}".format(abspath(settings.ssh_key_path), docker_ssh_key_path),
           "instrumentisto/rsync-ssh"]

    cmd.extend(rsync_cmd(docker_ssh_key_path, source_volume, starport))
    run_cmd_with_logging(cmd)


def run_backup():
    settings = load_settings()
    logging.info("Backing up to {}: ".format(settings.starport["addr"]))

    logging.info("The following directories are being backed up:")
    paths = list(t.path for t in settings.directory_targets)
    for path in paths:
        logging.info("- " + path)
        run_rsync(settings, path)

    logging.info("The following named volumes are being backed up:")
    names = list(t.name for t in settings.volume_targets)
    for name in names:
        logging.info("- " + name)
        run_rsync_from_container(settings, name)


if __name__ == "__main__":
    print("Backing up targets to Starport. Output will be logged to " + log_dir)
    with_logging(run_backup)
