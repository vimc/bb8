import logging
from datetime import date
from os import makedirs
from os.path import join, isdir
from subprocess import Popen, PIPE

from settings import log_dir


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


def log_from_docker(container):
    for log in container.logs(stream=True, stderr=True, stdout=False):
        logging.error(log.strip().decode("UTF-8"))
    for log in container.logs(stream=True, stderr=False, stdout=True):
        logging.info(log.strip().decode("UTF-8"))


def run_cmd_with_logging(cmd):
    with Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            logging.info(line.strip())
        for line in p.stderr:
            logging.error(line.strip())

    if p.returncode != 0:
        raise Exception("rsync returned error code {}".format(p.returncode))
