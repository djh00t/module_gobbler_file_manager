import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.utils import get_aws_credentials

def mock_getenv(key, default=None):
    return {
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    }.get(key, default)

# ... existing helper functions ...

def test_environment_aws_credentials(aws_credentials_fixture, monkeypatch):
    monkeypatch.setattr('os.getenv', mock_getenv)

    with patch('klingon_file_manager.utils.Session', return_value=get_mocked_session()):
        with pytest.raises(Exception) as e:
            get_aws_credentials()

    assert str(e.value) == 'Missing AWS_ACCESS_KEY_ID in environment variables'
