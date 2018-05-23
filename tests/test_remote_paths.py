from bin.bb8.remote_paths import RemotePaths
from tests.mocks import mock_starport_settings


class TestRemotePaths(object):
    def test_get_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        assert sut.host == "jean@paris"

    def test_get_data_path_without_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        data_path = sut.data()
        assert data_path == "starport/target/data/"

    def test_get_meta_path_without_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        meta_path = sut.meta()
        assert meta_path == "starport/target/meta/"

    def test_get_data_path_with_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        data_path = sut.data(include_host=True)
        assert data_path == "jean@paris:starport/target/data/"

    def test_get_meta_path_with_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        meta_path = sut.meta(include_host=True)
        assert meta_path == "jean@paris:starport/target/meta/"

    def test_get_metadata_file(self):
        sut = RemotePaths("target", mock_starport_settings)
        metadata_file = sut.metadata_file(include_host=True)
        assert metadata_file == "jean@paris:starport/target/meta/metadata.json"

    def test_rsync_path_is_data_path_with_host(self):
        sut = RemotePaths("target", mock_starport_settings)
        assert sut.rsync_path() == sut.data(include_host=True)
