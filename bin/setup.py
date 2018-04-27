#!/usr/bin/env python3
"""
Usage:
  setup.py [TARGET ...]
"""

from docopt import docopt

from bb8.settings import *


def check_user_input(config, desired_targets):
    possible_targets = set(x["name"] for x in config["targets"])
    if not desired_targets:
        print("No targets supplied. Options: {}".format(possible_targets))
        exit(-1)

    unknown_targets = set(desired_targets) - possible_targets
    if unknown_targets:
        print("Unknown targets: {}".format(unknown_targets))
        print("Possible targets are: {}".format(possible_targets))
        exit(-2)


def setup_targets():
    args = docopt(__doc__)
    desired_targets = args["TARGET"]
    with open(source_config_path) as f:
        config = json.load(f)
    check_user_input(config, desired_targets)
    machine_targets = list(x for x in config["targets"] if x["name"] in desired_targets)
    machine_config = {
        'starport': config["starport"],
        'targets': machine_targets
    }
    with open(config_path, 'w') as f:
        json.dump(machine_config, f, indent=4)

    print("bb8 setup with these targets: {}".format(", ".join(desired_targets)))


def setup_known_hosts():
    settings = load_settings()
    starport = settings.starport
    with open(host_key_path, 'r') as f:
        host_key = f.read()
    with open(known_hosts_path, 'a') as f:
        f.write("{},{} {}".format(starport["ip"], starport["addr"], host_key))
    print("Saved host key for {} to known hosts".format(starport["addr"]))


if __name__ == "__main__":
    setup_targets()
    setup_known_hosts()
