import unittest

import docker

import targets


class TestNamedVolumeTarget(unittest.TestCase):
    """Tests for NamedVolumeTarget"""
    docker = docker.client.from_env()

    def setUp(self):
        self._dummy_volume_name = "bb8_test_volume"
        if not self.docker.ping():
            self.skipTest("docker is not available")
        self.tearDown()

    def tearDown(self):
        try:
            self.docker.volumes.get(self._dummy_volume_name).remove()
        except:
            pass

    def test_properties(self):
        """Test properties of constructed volume target"""
        vol = targets.NamedVolumeTarget("mytarget", self._dummy_volume_name)
        self.assertEqual(vol.name, "mytarget")
        self.assertEqual(vol.volume, self._dummy_volume_name)
        self.assertEqual(vol.id, "Named volume: mytarget")
        self.assertEqual(vol.mount_id, self._dummy_volume_name)

    def test_creation(self):
        """Test creation of volume"""
        vol = targets.NamedVolumeTarget("mytarget", self._dummy_volume_name)
        self.assertFalse(vol._volume_exists())
        vol.before_restore()
        self.assertTrue(vol._volume_exists())

if __name__ == '__main__':
    unittest.main()
