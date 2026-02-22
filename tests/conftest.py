import pytest

@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    import tempfile
    import shutil
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir)

@pytest.fixture
def mock_wav_file():
    """Create a mock WAV file object"""
    from unittest.mock import MagicMock
    mock_file = MagicMock()
    mock_file.filename = "test.wav"
    mock_file.save = lambda path: open(path, 'wb').write(b"RIFF...fake wav data")
    return mock_file

@pytest.fixture
def mock_empty_file():
    """Create a mock empty file object"""
    from unittest.mock import MagicMock
    mock_file = MagicMock()
    mock_file.filename = ""
    return mock_file