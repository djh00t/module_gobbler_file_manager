import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.utils import get_aws_credentials

def mock_getenv(key, default=None):
    return {
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    }.get(key, default)

def get_mock_iam_client():
    mock_iam_client = MagicMock()
    mock_iam_client.get_user.return_value = {
        'User': {
            'UserId': 'mock-user-id',
            'Arn': 'arn:aws:iam::123456789012:user/mock-user'
        }
    }
    return mock_iam_client

def get_mock_s3_client():
    mock_s3_client = MagicMock()
    mock_s3_client.list_buckets.return_value = {
        'Buckets': []
    }
    return mock_s3_client

def get_mocked_session():
    mock_iam_client = get_mock_iam_client()
    mock_s3_client = get_mock_s3_client()

    mock_session = MagicMock()
    mock_session.client.side_effect = lambda service_name, **kwargs: mock_iam_client if service_name == 'iam' else mock_s3_client

    return mock_session

@pytest.fixture
def aws_credentials_fixture():
    return {
        'credentials': {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        }
    }

def test_environment_aws_credentials(aws_credentials_fixture):
    with patch('os.getenv', side_effect=mock_getenv):
        with patch('klingon_file_manager.utils.Session', return_value=get_mocked_session()):
            response = get_aws_credentials()
            print(f"Access Key in the test response: {response['credentials']['AWS_ACCESS_KEY_ID']}")
    assert 'credentials' in response
    assert response['credentials']['AWS_ACCESS_KEY_ID'] == 'AKIAIOSFODNN7EXAMPLE'

### 