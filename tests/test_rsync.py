from unittest.mock import MagicMock, ANY

import pytest

from bin.bb8.docker_rsync import DockerRsync
from tests.mocks import mock_starport_settings, mock_settings


# noinspection PyProtectedMember,PyMethodMayBeStatic
class TestDockerRsync(object):
    def test_get_volume_args(self):
        sut = DockerRsync()
        args = sut._get_volume_args("local", "some-mode")
        assert args["local"] == {
            "bind": "/local",
            "mode": "some-mode"
        }

    def test_get_remote_dir(self):
        sut = DockerRsync()
        starport = mock_starport_settings
        dir = sut._get_remote_dir(starport)
        assert dir == "clark@metropolis:daily_planet"

    def test_backup_volume(self):
        # Setup
        sut = DockerRsync()
        sut._run_rsync = MagicMock()
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        sut.backup_volume(mock_settings(), "local")

        # Check
        sut._run_rsync.assert_called_once_with("backup", ANY, "local", ANY)
        sut._get_volume_args.assert_called_once_with("local", "ro")

    def test_restore_volume(self):
        # Setup
        sut = DockerRsync()
        sut._run_rsync = MagicMock()
        sut._get_volume_args = MagicMock(wraps=sut._get_volume_args)

        # Test
        sut.restore_volume(mock_settings(), "local", 999)

        # Check
        sut._run_rsync.assert_called_once_with("restore", ANY, ANY, "/local",
                                               999)
        sut._get_volume_args.assert_called_once_with("local", "rw")

    def test_run_rsync_fails_if_unknown_mode(self):
        sut = DockerRsync()
        v = sut._get_volume_args("vol", "ro")
        with pytest.raises(Exception):
            sut._run_rsync("bad", v, "from", "to")
