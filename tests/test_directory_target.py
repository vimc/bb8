import docker
import shutil
import os

from bin.bb8 import targets


# noinspection PyProtectedMember
class TestDirectoryTarget(object):
    """Tests for NamedVolumeTarget"""
    docker = docker.client.from_env()

    def test_properties(self):
        """Test properties of constructed directory target"""
        dir_path = "/some/dir/"
        target = targets.DirectoryTarget("mytarget", dir_path, None)
        assert target.name == "mytarget"
        assert target.path == dir_path
        assert target.id == "Directory: mytarget"
        assert target.mount_id == dir_path

    def test_exists_locally(self):
        """Directory targets always report as existent"""
        dir_path = "/doesnt/exist/"
        target = targets.DirectoryTarget("mytarget", dir_path, None)
        assert target.exists_locally()


