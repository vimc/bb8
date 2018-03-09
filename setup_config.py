#!/usr/bin/env python3
"""
Usage:
  setup_config.py config_path TARGET ...
"""

from docopt import docopt
import json

from settings import root_path


def check_user_input(config, desired_targets):
    possible_targets = set(x.name for x in config["targets"])
    if not desired_targets:
        print("No targets supplied. Options: {}".format(possible_targets))
        exit(-1)

    unknown_targets = possible_targets - set(desired_targets)
    if unknown_targets:
        print("Unknown targets: {}".format(unknown_targets))
        print("Possible targets are: {}".format(possible_targets))
        exit(-2)


if __name__ == "__main__":
    args = docopt(__doc__)
    if "config_path" not in args:
        print(__doc__)
        exit(-1)

    desired_targets = args["TARGET"]
    with open(args["config_path"]) as f:
        config = json.load(f)

    check_user_input(config, desired_targets)
    machine_targets = list(x for x in config["targets"] if x["name"] in desired_targets)

    machine_config = {
        'starport': config["starport"],
        'targets': machine_targets
    }
    with open(root_path, 'w') as f:
        json.dump(machine_config, f, indent=4)
