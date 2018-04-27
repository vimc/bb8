import json
from os.path import join, abspath

from .targets import DirectoryTarget, NamedVolumeTarget, TargetOptions

root_path = "/bb8/etc/"
source_config_path = join(root_path, "source-config.json")
config_path = join(root_path, "config.json")
ssh_key_path = join(root_path, "secrets/ssh_key")
host_key_path = join(root_path, "secrets/host_key")
known_hosts_path = join(root_path, "known_hosts")

log_dir = '/bb8/logs/'


class Settings:
    def __init__(self, path=config_path):
        with open(path, 'r') as f:
            config = json.load(f)

        self.starport = config["starport"]
        self.targets = list(Settings.parse_target(t) for t in config["targets"])

    @classmethod
    def parse_target(cls, data):
        t = data["type"]
        options = TargetOptions.from_data(data)
        if t == "directory":
            return DirectoryTarget(data["name"], data["path"], options)
        elif t == "named_volume":
            return NamedVolumeTarget(data["name"], data["volume"], options)
        else:
            raise Exception("Unsupported target type: " + t)


def load_settings():
    return Settings()
