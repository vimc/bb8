import docker
import shutil
import os

from bin.bb8 import targets


# noinspection PyProtectedMember
class TestDirectoryTarget(object):
    """Tests for NamedVolumeTarget"""
    docker = docker.client.from_env()
    dummy_dir_name = "/doesnt/exist"

    @classmethod
    def setup_class(cls):
        cls.remove_test_dir_if_exists()

    @classmethod
    def teardown_class(cls):
        cls.remove_test_dir_if_exists()

    def test_properties(self):
        """Test properties of constructed directory target"""
        target = targets.DirectoryTarget("mytarget", self.dummy_dir_name, None)
        assert target.name == "mytarget"
        assert target.path == self.dummy_dir_name
        assert target.id == "Directory: mytarget"
        assert target.mount_id == self.dummy_dir_name

    def test_exists_locally(self):
        """Test whether directory target has files in"""
        target = targets.DirectoryTarget("mytarget", self.dummy_dir_name, None)
        assert not target.files_exist_locally()

        target = targets.DirectoryTarget("mytarget", "/etc", None)
        assert target.files_exist_locally()

    @classmethod
    def remove_test_dir_if_exists(cls):
        if os.path.exists(cls.dummy_dir_name):
            shutil.rmtree(cls.dummy_dir_name)
