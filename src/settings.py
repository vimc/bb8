import json
from os.path import join, isfile

from targets import DirectoryTarget

root_path = "/etc/montagu/bb8"
config_path = join(root_path, "config.json")
secrets_path = join(root_path, "secrets.json")

log_dir = '/var/log/bb8'

class Settings:
    def __init__(self):
        with open(config_path, 'r') as f:
            config = json.load(f)
        if isfile(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
        else:
            secrets = {}

        self.starport_addr = config["starport_addr"]
        self.secrets = secrets
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
