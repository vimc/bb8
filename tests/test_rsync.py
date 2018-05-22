from unittest.mock import MagicMock, ANY, call
import unittest

from bin.bb8.docker_rsync import DockerRsync
from tests.mocks import mock_starport_settings, mock_settings, mock_instance_guid


# noinspection PyProtectedMember,PyMethodMayBeStatic
class TestDockerRsync(unittest.TestCase):
    def test_get_volume_args(self):
        sut = DockerRsync()
        args = sut._get_volume_args("local", "some-mode")
        assert args["local"] == {
            "bind": "/local",
            "mode": "some-mode"
        }

    def test_get_remote_dir(self):
        sut = DockerRsync()
        dir = sut._get_remote_dir("jean@paris", "target")
        assert dir == "jean@paris:target/data/"

    def test_get_host(self):
        sut = DockerRsync()
        host = sut._get_host(mock_starport_settings)
        assert host == "jean@paris"

    def test_get_target_path(self):
        sut = DockerRsync()
        path = sut._get_target_path("/location/", "/target_name/")
        assert path == "/location/target_name/"

    def test_backup_volume(self):
        # Setup
        sut = DockerRsync()
        sut._run_rsync = MagicMock()
        sut._make_remote_dir = MagicMock()
        sut._validate_instance = MagicMock()
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        sut.backup_volume(mock_settings(), "target", "local")

        # Check
        sut._run_rsync.assert_called_once_with(
            ANY, "local", "jean@paris:starport/target/data/", True)
        sut._validate_instance.assert_called_once_with("jean@paris", "target", "starport/target/meta/guid", mock_instance_guid)
        sut._get_volume_args.assert_called_once_with("local", "ro")
        sut._make_remote_dir.assert_has_calls([
            call("jean@paris", "starport/target/data"),
            call("jean@paris", "starport/target/meta"),
        ])

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
        sut.restore_volume(mock_settings(), "target", "local")

        # Check
        sut._run_rsync.assert_called_once_with(
            ANY, "jean@paris:starport/target/data/local/", "/local", False)
        sut._get_volume_args.assert_called_once_with("local", "rw")
