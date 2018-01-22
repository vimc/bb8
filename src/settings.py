import json
import os
from os.path import join, isfile
from subprocess import check_output

from targets import DirectoryTarget

root_path = "./etc/"
config_path = join(root_path, "config.json")
ssh_path = join(root_path, "id_rsa")

log_dir = './log/'


class Settings:
    def __init__(self):
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.starport_addr = config["starport_addr"]
        self.starport_user = config["starport_user"]
        self.starport_backup_location = config["starport_backup_location"]
        self.ssh_key = ssh_path
        self.targets = list(Settings.parse_target(t) for t in config["targets"])

    @classmethod
    def parse_target(cls, data):
        t = data["type"]
        if t == "directory":
            return DirectoryTarget(data["path"])
        else:
            raise Exception("Unsupported target type: " + t)


def load_settings():
    return Settings()


def get_secret(name):
    path = "secret/{}".format(name)
    return check_output(["vault", "read", "-field=value", path]).decode('utf-8')


def save_private_key():
    if not isfile(ssh_path):
        ssh_key = get_secret("annex/id_rsa")
        with open(ssh_path, 'a'):  # Create file if does not exist
            pass
        os.chmod(ssh_path, 0o600)
        with open(ssh_path, 'w') as f:
            f.write(ssh_key)
