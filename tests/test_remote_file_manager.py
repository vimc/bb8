from unittest.mock import MagicMock, call

import pytest

from bin.bb8.remote_file_manager import RemoteFileManager, default_metadata
from tests.mocks import Dynamic


# noinspection PyTypeChecker
class TestRemoteFileManager(object):
    def test_get_metadata_when_no_metadata_exists(self):
        # Setup
        paths = Dynamic("paths", metadata_file="/some/path")
        sut = RemoteFileManager(paths)
        sut.run_remote_cmd = lambda x: ""

        # Test
        assert sut.get_metadata() == default_metadata()

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

    def test_validate_instance_raises_exception_if_mismatched(self):
        # Setup
        sut = RemoteFileManager(Dynamic("paths"))
        sut.get_metadata = lambda: {
            "instance_guid": "foreign_guid"
        }

        # Test
        expected_message = "This target has been backed up by a different " \
                           "instance of bb8: target"
        with pytest.raises(Exception, message=expected_message):
            sut.validate_instance("local_guid")

    def test_validate_instance_passes_if_matched(self):
        sut = RemoteFileManager(Dynamic("paths"))
        sut.get_metadata = lambda: {
            "instance_guid": "local_guid"
        }
        # Does not throw
        sut.validate_instance("local_guid")
