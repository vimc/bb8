from unittest.mock import MagicMock, ANY, call
import unittest

from bin.bb8.docker_rsync import DockerRsync
from tests.mocks import mock_starport_settings, mock_settings, mock_instance_guid, mock_remote_paths


# noinspection PyProtectedMember,PyMethodMayBeStatic,PyTypeChecker
class TestDockerRsync(unittest.TestCase):
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
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        sut.backup_volume("local", "host:remote/path/")

        # Check
        sut._run_rsync.assert_called_once_with(
            ANY, "local", "host:remote/path/", relative=True)
        sut._get_volume_args.assert_called_once_with("local", "ro")

    def test_restore_volume(self):
        # Setup
        sut = DockerRsync()
        sut._run_rsync = MagicMock()
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        sut.restore_volume("local", "host:remote/path/")

        # Check
        sut._run_rsync.assert_called_once_with(
            ANY, "host:remote/path/local/", "/local", relative=False)
        sut._get_volume_args.assert_called_once_with("local", "rw")
