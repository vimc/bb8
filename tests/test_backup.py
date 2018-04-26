from unittest.mock import MagicMock

from bin.bb8.backup import run_backup


class Dynamic(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def test_backup_is_only_called_for_targets_with_backup_set_to_true():
    targets = [
        Dynamic(id="a", mount_id="mount-a",
                name="name-a", options=Dynamic(backup=True)),
        Dynamic(id="b", mount_id="mount-b",
                name="name-b", options=Dynamic(backup=False)),
    ]
    starport = {"addr": "fake.starport.address"}
    settings = Dynamic(starport=starport, targets=targets)
    rsync = Dynamic(backup_volume=MagicMock())
    run_backup(settings, rsync)
    rsync.backup_volume.assert_called_once_with(settings, "mount-a")
