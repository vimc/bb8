import os

from bin.bb8.settings import Settings
from bin.bb8.targets import NamedVolumeTarget, TargetOptions, DirectoryTarget

json = """{
    "starport": {
        "addr": "the moon",
        "ip": "127.0.0.1",
        "user": "astronaut",
        "backup_location": "houston"
    },
    "targets": [
        {
            "name": "target_1",
            "type": "named_volume",
            "volume": "volume_name"
        },
        {
            "name": "target_2",
            "type": "directory",
            "path": "/some/path",
            "backup": false,
            "restore": false,
            "user": 123
        }
    ]
}"""


def test_can_parse_settings():
    s = Settings('test.json')
    assert s.starport == {
        "addr": "the moon",
        "ip": "127.0.0.1",
        "user": "astronaut",
        "backup_location": "houston"
    }
    assert s.targets[0] == NamedVolumeTarget("target_1", "volume_name",
                                             TargetOptions(True, True, "root"))
    assert s.targets[1] == DirectoryTarget("target_2", "/some/path",
                                           TargetOptions(False, False, 123))


def setup_module(module):
    with open('test.json', 'w') as f:
        f.write(json)


def teardown_module(module):
    os.remove('test.json')
