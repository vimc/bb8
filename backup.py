#!/usr/bin/env python3
import logging
from datetime import date
from os import makedirs
from os.path import join, isdir, abspath
from subprocess import Popen, PIPE
import docker

from settings import load_settings, log_dir

client = docker.from_env()


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


def rsync_cmd(ssh_key_path, known_hosts_path, target_path, starport):
    # rsync options:
    # -v = verbose - give info about what files are being transferred and a brief summary at the end
    # -r = copy directories recursively
    # -e = specify remote shell program explicitly (i.e. ssh as opposed to the default rsh)
    ssh_cmd = "ssh -o IdentityFile={} -o IdentitiesOnly=yes -o UserKnownHostsFile={}" \
        .format(ssh_key_path, known_hosts_path)
    destination_path = "{}@{}:{}".format(starport["user"],
                                         starport["addr"],
                                         starport["backup_location"])
    args = ["rsync", "-rv", "-e", ssh_cmd, target_path, destination_path]
    print(args)
    return args


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
    cmd = rsync_cmd(abspath(settings.ssh_key_path), abspath(settings.known_hosts_path), path, starport)
    run_cmd_with_logging(cmd)


def run_rsync_from_container(settings, source_volume):
    starport = settings.starport
    docker_ssh_key_path = "/etc/bb8/id_rsa"
    docker_known_hosts_path="/root/.ssh/known_hosts"

    cmd = rsync_cmd(docker_ssh_key_path, docker_known_hosts_path, source_volume, starport)
    volumes = {abspath(settings.known_hosts_path): {"bind": "/root/.ssh/known_hosts", "mode": "ro"},
               abspath(settings.ssh_key_path): {"bind": docker_ssh_key_path, "mode": "ro"},
               source_volume: {"bind": "/{}".format(source_volume), "mode": "ro"}}

    container = client.containers.run("instrumentisto/rsync-ssh", command=cmd, volumes=volumes,
                                      detach=True)

    for log in container.logs(stream=True, stderr=True, stdout=False):
        logging.error(log.strip())
    for log in container.logs(stream=True, stderr=False, stdout=True):
        logging.info(log.strip())


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
