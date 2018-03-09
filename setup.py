#!/usr/bin/env python3
from os import mkdir
from os.path import isfile, isdir

from settings import config_path, root_path, save_private_key, save_host_key

if __name__ == "__main__":
    if not isdir(root_path):
        mkdir(root_path)
    if not isfile(config_path):
        print("Missing config files in {}.".format(root_path))
        print("First run setup_config.py SOURCE_CONFIG_PATH TARGET ...")
        exit(-1)

    print("Obtaining secrets from the vault. If you are not authenticated with the vault, this will fail.")
    save_private_key()
    save_host_key()
