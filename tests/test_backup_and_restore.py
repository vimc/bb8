from unittest.mock import MagicMock, call

from bin.bb8.restore import run_restore
from bin.bb8.backup import run_backup
from tests.mocks import mock_target, mock_settings, Dynamic


def test_backup_is_only_called_for_targets_with_backup_set_to_true():
    # Setup
    targets = [
        mock_target("a", backup=True),
        mock_target("b", backup=False),
        mock_target("c", backup=True)
    ]
    settings = mock_settings(targets)
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
        mock_target("c", restore=True, before_restore=MagicMock(), user="test")
    ]
    settings = mock_settings(targets)
    rsync = Dynamic("rsync", restore_volume=MagicMock())

    # Test
    run_restore(lambda: settings, rsync)

    # Check
    rsync.restore_volume.assert_has_calls([
        call(settings, "mount-a", "root"),
        call(settings, "mount-c", "test"),
    ])
    assert targets[0].before_restore.call_count == 1
    assert targets[1].before_restore.call_count == 0
    assert targets[2].before_restore.call_count == 1
