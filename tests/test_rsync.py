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
        sut._validate_instance = MagicMock()
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        sut.backup_volume("local", "host:remote/path/")

        # Check
        sut._run_rsync.assert_called_once_with(
            ANY, "local", "host:remote/path/", relative=True)
        sut._validate_instance.assert_called_once_with("jean@paris", "target", "starport/target/meta/guid", mock_instance_guid)
        sut._get_volume_args.assert_called_once_with("local", "ro")

    def test_validate_instance_saves_instance_if_non_existent(self):
        # Setup
        sut = DockerRsync()
        sut._run = MagicMock(return_value='')
        sut._save_instance_guid = MagicMock()

        # Test
        sut._validate_instance("host", "target", "starport/target/meta/guid", "1234")

        # Check
        sut._save_instance_guid.assert_called_once_with(
            "host", "starport/target/meta/guid", "1234")

    def test_validate_instance_raises_exception_if_mismatched(self):
        # Setup
        sut = DockerRsync()
        sut._run = MagicMock(return_value='5678')
        sut._save_instance_guid = MagicMock()

        # Test
        with self.assertRaises(Exception) as cm:
            sut._validate_instance("host", "target", "starport/target/meta/guid", "1234")
        self.assertEqual("This target has been backed up by a different instance of bb8: target", str(cm.exception))

    def test_validate_instance_passes_if_matched(self):
        # Setup
        sut = DockerRsync()
        sut._run = MagicMock(return_value='1234')
        sut._save_instance_guid = MagicMock()

        # Test
        sut._validate_instance("host", "target", "starport/target/meta/guid", "1234")

        # Check
        sut._save_instance_guid.assert_not_called()

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
