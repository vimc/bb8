import json
import os
from os.path import join, isfile
from subprocess import check_output

from targets import DirectoryTarget, NamedVolumeTarget

root_path = "./etc/"
config_path = join(root_path, "config.json")
ssh_key_path = join(root_path, "id_rsa")
known_hosts_path = join(root_path, "known_hosts")

log_dir = './log/'


class Settings:
    def __init__(self):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.starport = config["starport"]
        self.ssh_key_path = ssh_key_path
        self.known_hosts_path = known_hosts_path
        self.directory_targets = list(Settings.parse_directory_target(t) for t in config["directory_targets"])
        self.volume_targets = list(Settings.parse_volume_target(t) for t in config["volume_targets"])

    @classmethod
    def parse_directory_target(cls, data):
        p = data["path"]
        if p is not None:
            return DirectoryTarget(p)
        else:
            raise Exception("Directory targets must have a path specified")

    @classmethod
    def parse_volume_target(cls, data):
        n = data["name"]
        if n is not None:
            return NamedVolumeTarget(n)
        else:
            raise Exception("Named volume targets must have a name specified")


def load_settings():
    return Settings()


def get_secret(name):
    path = "secret/{}".format(name)
    return check_output(["vault", "read", "-field=value", path]).decode('utf-8')


def save_private_key():
    if not isfile(ssh_key_path):
        ssh_key = get_secret("annex/id_rsa")
        with open(ssh_key_path, 'a'):  # Create file if does not exist
            pass
        os.chmod(ssh_key_path, 0o600)
        with open(ssh_key_path, 'w') as f:
            f.write(ssh_key)


def save_host_key():
    host_key = get_secret("annex/host_key")
    settings = load_settings()
    starport = settings.starport
    with open(known_hosts_path, 'a'):  # Create file if does not exist
        pass
    with open(known_hosts_path, 'a') as f:
        f.write("{},{} {}".format(starport["ip"], starport["addr"], host_key))
