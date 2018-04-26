from unittest.mock import MagicMock, call

from bin.bb8.restore import run_restore
from bin.bb8.backup import run_backup


class Dynamic(object):
    def __init__(self, label, **kwargs):
        self.label = label
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return str(self.label)


def mock_target(id, backup=True, restore=True, **kwargs):
    return Dynamic(id, id=id, mount_id="mount-{}".format(id),
                   name="name-{}".format(id),
                   options=Dynamic("opt", backup=backup, restore=restore),
                   **kwargs)


def test_backup_is_only_called_for_targets_with_backup_set_to_true():
    # Setup
    targets = [
        mock_target("a", backup=True),
        mock_target("b", backup=False),
        mock_target("c", backup=True)
    ]
    starport = {"addr": "fake.starport.address"}
    settings = Dynamic("settings", starport=starport, targets=targets)
    rsync = Dynamic("rsync", backup_volume=MagicMock())

    # Test
    run_backup(lambda: settings, rsync)

    # Check
    rsync.backup_volume.assert_has_calls([
        call(settings, "mount-a"),
        call(settings, "mount-c"),
    ])


def test_restore_is_only_called_for_targets_with_restore_set_to_true():
    # Setup
    targets = [
        mock_target("a", restore=True, before_restore=MagicMock()),
        mock_target("b", restore=False, before_restore=MagicMock()),
        mock_target("c", restore=True, before_restore=MagicMock())
    ]
    starport = {
        "addr": "fake.starport.address",
        "backup_location": "fake_remote_directory"
    }
    settings = Dynamic("settings", starport=starport, targets=targets)
    rsync = Dynamic("rsync", restore_volume=MagicMock())

    # Test
    run_restore(lambda: settings, rsync)

    # Check
    rsync.restore_volume.assert_has_calls([
        call(settings, "mount-a"),
        call(settings, "mount-c"),
    ])
    assert targets[0].before_restore.call_count == 1
    assert targets[1].before_restore.call_count == 0
    assert targets[2].before_restore.call_count == 1
