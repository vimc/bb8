from unittest.mock import MagicMock, ANY, call

from bin.bb8.docker_rsync import DockerRsync
from tests.mocks import mock_starport_settings, mock_settings, Dynamic, \
    mock_remote_paths


# noinspection PyProtectedMember,PyMethodMayBeStatic,PyTypeChecker
class TestDockerRsync(object):
    def test_get_volume_args(self):
        sut = DockerRsync()
        args = sut._get_volume_args("local", "some-mode")
        assert args["local"] == {
            "bind": "/local",
            "mode": "some-mode"
        }

    def test_backup_volume(self):
        # Setup
        sut = DockerRsync()
        sut._run_rsync = MagicMock()
        sut._make_remote_dir = MagicMock()
        sut._write_metadata = MagicMock()
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        metadata = {"a": 5}
        remote_paths = mock_remote_paths()
        sut.backup_volume("local", metadata, remote_paths)

        # Check
        sut._run_rsync.assert_called_once_with(
            ANY, "local", "server:some/path/datadata/", relative=True)
        sut._get_volume_args.assert_called_once_with("local", "ro")
        sut._make_remote_dir.assert_has_calls([
            call("host", "some/path/datadata/"),
            call("host", "some/path/metadata/"),
        ])
        sut._write_metadata.assert_called_once_with(metadata, remote_paths)

    def test_restore_volume(self):
        # Setup
        sut = DockerRsync()
        sut._run = MagicMock()
        sut._run_rsync = MagicMock()
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        sut.restore_volume("local", mock_remote_paths())

        # Check
        sut._run_rsync.assert_called_once_with(
            ANY, "server:some/path/datadata/local/", "/local", relative=False)
        sut._get_volume_args.assert_called_once_with("local", "rw")
