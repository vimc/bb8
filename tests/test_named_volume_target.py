import docker

from bin.bb8 import targets


# noinspection PyProtectedMember
class TestNamedVolumeTarget(object):
    """Tests for NamedVolumeTarget"""
    docker = docker.client.from_env()
    dummy_volume_name = "bb8_test_volume"

    @classmethod
    def setup_class(cls):
        cls.remove_test_volume_if_exists()

    @classmethod
    def teardown_class(cls):
        cls.remove_test_volume_if_exists()

    def test_properties(self):
        """Test properties of constructed volume target"""
        vol = targets.NamedVolumeTarget("mytarget", self.dummy_volume_name, None)
        assert vol.name == "mytarget"
        assert vol.volume == self.dummy_volume_name
        assert vol.id == "Named volume: mytarget"
        assert vol.mount_id == self.dummy_volume_name

    def test_creation(self):
        """Test creation of volume"""
        vol = targets.NamedVolumeTarget("mytarget", self.dummy_volume_name, None)
        assert not vol._volume_exists()
        vol.before_restore()
        assert vol._volume_exists()

    def test_exists_locally(self):
        """Test local existence of volume"""
        self.remove_test_volume_if_exists()
        vol = targets.NamedVolumeTarget("mytarget", self.dummy_volume_name, None)
        assert not vol.files_exist_locally()
        vol.before_restore()
        assert vol.files_exist_locally()

    @classmethod
    def remove_test_volume_if_exists(cls):
        try:
            vol = cls.docker.volumes.get(cls.dummy_volume_name)
            vol.remove()
            print("Removed test volume {}".format(cls.dummy_volume_name))
        except docker.errors.NotFound:
            pass
