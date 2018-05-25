from datetime import datetime
from unittest.mock import MagicMock, call, ANY

from bin.bb8.backup import BackupTask
from bin.bb8.restore import RestoreTask
from tests.mocks import mock_target, mock_settings, Dynamic, mock_instance_guid


def test_backup_target_is_only_called_for_targets_with_backup_set_to_true():
    # Setup
    targets = [
        mock_target("a", backup=True),
        mock_target("b", backup=False),
        mock_target("c", backup=True)
    ]
    settings = mock_settings(targets)
    sut = BackupTask(lambda: settings)
    sut.backup_target = MagicMock()

    # Test
    sut.run()

    # Check
    sut.backup_target.assert_has_calls([
        call(targets[0], ANY, settings),
        call(targets[2], ANY, settings),
    ])


def test_backup_target():
    # Setup
    rsync = Dynamic("rsync", backup_volume=MagicMock())
    fm = Dynamic("fm",
                 create_directories=MagicMock(),
                 write_metadata=MagicMock(),
                 get_rsync_path=lambda: "/some/path",
                 validate_instance=MagicMock())
    sut = BackupTask(lambda: {}, rsync)

    # Test
    target = mock_target("a")
    sut.backup_target(target, fm, mock_settings([target]))

    # Check
    fm.create_directories.assert_called_once()
    fm.validate_instance.assert_called_once_with(mock_instance_guid)
    rsync.backup_volume.assert_called_once_with("mount-a", "/some/path")
    fm.write_metadata.assert_called_once()


def metadata_includes_current_time():
    before = datetime.now()
    settings = mock_settings()
    meta = BackupTask().make_metadata(settings)
    last_backup = meta["last_backup"]
    after = datetime.now()
    assert before <= last_backup <= after


def metadata_includes_instance_guid():
    settings = mock_settings()
    meta = BackupTask().make_metadata(settings)
    assert  meta["instance_guid"] == mock_instance_guid


def test_restore_target_is_only_called_for_targets_with_restore_set_to_true():
    # Setup
    targets = [
        mock_target("a", restore=True),
        mock_target("b", restore=False),
        mock_target("c", restore=True)
    ]
    settings = mock_settings(targets)
    sut = RestoreTask(lambda: settings)
    sut.restore_target = MagicMock()

    # Test
    sut.run()

    # Check
    sut.restore_target.assert_has_calls([
        call(targets[0], ANY, settings),
        call(targets[2], ANY, settings),
    ])


def test_restore_target():
    # Setup
    target = mock_target("a", before_restore=MagicMock())
    rsync = Dynamic("rsync", restore_volume=MagicMock())
    fm = Dynamic("fm",
                 get_rsync_path=lambda: "/some/path",
                 validate_instance=MagicMock())
    sut = RestoreTask(lambda: {}, rsync=rsync)

    # Test
    sut.restore_target(target, fm, mock_settings([target]))

    # Check
    fm.validate_instance.assert_called_once_with(mock_instance_guid)
    target.before_restore.assert_called_once()
    rsync.restore_volume.assert_called_with("mount-a", "/some/path")
