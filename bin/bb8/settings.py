import json
from os.path import join, isfile

from .targets import DirectoryTarget, NamedVolumeTarget, TargetOptions

root_path = "/bb8/etc/"
source_config_path = join(root_path, "source-config.json")
config_path = join(root_path, "config.json")
ssh_key_path = join(root_path, "secrets/ssh_key")
host_key_path = join(root_path, "secrets/host_key")
known_hosts_path = join(root_path, "known_hosts")
machine_id_path = join(root_path, "machine-id")

log_dir = '/bb8/logs/'


class Settings:
    def __init__(self, path=config_path):
        with open(path, 'r') as f:
            config = json.load(f)

        self.starport = config["starport"]
        self.targets = list(Settings.parse_target(t) for t in config["targets"])

        if isfile(machine_id_path):
            with open(machine_id_path, 'r') as f:
                self.instance_guid = f.read().replace('\n', '')
        else:
            self.instance_guid = None

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
