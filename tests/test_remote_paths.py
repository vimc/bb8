from bin.bb8.remote_paths import RemotePaths
from tests.mocks import mock_starport_settings


class TestRemotePaths(object):
    def test_get_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        assert sut.host == "jean@paris"

    def test_get_data_path(self):
        sut = RemotePaths("target", mock_starport_settings)
        assert sut.data == "starport/target/data/"

    def test_get_meta_path(self):
        sut = RemotePaths("target", mock_starport_settings)
        assert sut.meta == "starport/target/meta/"

    def test_get_metadata_file(self):
        sut = RemotePaths("target", mock_starport_settings)
        path = sut.metadata_file
        assert path == "starport/target/meta/metadata.json"

    def test_rsync_path_is_data_path_with_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        expected = "jean@paris:" + sut.data
        assert sut.rsync_path == expected
