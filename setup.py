#!/usr/bin/env python3
from os.path import isfile, isdir, join
from os import listdir, mkdir
from shutil import copy

from settings import config_path, root_path, save_private_key, save_host_key


def get_user_config_choice():
    options = listdir(configs_source)
    prompt = "Please choose which config to use ({})? ".format(", ".join(options))
    choice = None
    path = None
    while not choice:
        choice = input(prompt).strip()
        if choice:
            path = join(configs_source, choice, 'config.json')
            if not isfile(path):
                choice = None
                print("'{}' does not exist".format(path))
    return path


if __name__ == "__main__":
    if not isdir(root_path):
        mkdir(root_path)
    if not isfile(config_path):
        configs_source = './configs'
        print("Missing config files in {}.".format(root_path))
        path = get_user_config_choice()
        print("Copying {} to {}".format(path, root_path))
        copy(path, root_path)

    print("Obtaining secrets from the vault. If you are not authenticated with the vault, this will fail.")
    save_private_key()
    save_host_key()
