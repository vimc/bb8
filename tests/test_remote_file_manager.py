from unittest.mock import MagicMock, call

from bin.bb8.remote_file_manager import RemoteFileManager
from tests.mocks import Dynamic


# noinspection PyTypeChecker
class TestRemoteFileManager(object):
    def test_get_metadata_when_no_metadata_exists(self):
        # Setup
        paths = Dynamic("paths", metadata_file="/some/path")
        sut = RemoteFileManager(paths)
        sut.run_remote_cmd = lambda x: ""

        # Test
        assert sut.get_metadata() is None

    def test_get_metadata_when_metadata_exists(self):
        # Setup
        paths = Dynamic("paths", metadata_file="/some/path")
        sut = RemoteFileManager(paths)
        sut.run_remote_cmd = lambda x: '{ "test": "value" }'

        # Test
        assert sut.get_metadata() == {"test": "value"}

    def test_write_metadata(self):
        # Setup
        paths = Dynamic("paths")
        paths.metadata_file = "/some/file.json"
        sut = RemoteFileManager(paths)
        sut.run_remote_cmd = MagicMock()

        # Test
        sut.write_metadata({"test": "value"})

        # Check
        sut.run_remote_cmd.assert_called_with(
            'echo \'{"test": "value"}\' > /some/file.json'
        )

    def test_create_directories(self):
        # Setup
        paths = Dynamic("paths")
        paths.data = "/path/to/data/"
        paths.meta = "/path/to/meta/"
        sut = RemoteFileManager(paths)
        sut._make_remote_dir = MagicMock()

        # Test
        sut.create_directories()

        # Check
        sut._make_remote_dir.assert_has_calls([
            call("/path/to/data/"),
            call("/path/to/meta/"),
        ])

    def test_get_rsync_path_calls_through(self):
        paths = Dynamic("paths", rsync_path="/some/path")
        sut = RemoteFileManager(paths)
        assert sut.get_rsync_path() == "/some/path"
