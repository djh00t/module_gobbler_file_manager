"""
Module: Test module for AWS utilities in the klingon_file_manager

This module contains tests for utility functions in the `klingon_file_manager.utils` module that handle AWS operations.

Functions tested:
- get_aws_credentials
- parallel_check_bucket_permissions
- check_bucket_permissions
- get_mime_type

The module also contains various mock and helper functions to assist in testing.

Functions in this test module:
- MockClientError
- NoSuchBucketException
- mock_getenv
- get_mock_iam_client
- mock_s3_list_buckets
- get_mock_s3_client
- get_mocked_session
- aws_credentials_fixture
- ... (and other test functions)
"""

import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.utils import get_aws_credentials, parallel_check_bucket_permissions, check_bucket_permissions, get_mime_type
from botocore.exceptions import NoCredentialsError, ClientError

class MockClientError(Exception):
    """Mock class for ClientError exceptions."""
    def __init__(self, error_code):
        self.response = {'Error': {'Code': error_code}}

# Define a custom exception class for NoSuchBucket
class NoSuchBucketException(Exception):
    """Mock class for NoSuchBucket exceptions."""
    pass

def mock_getenv(key, default=None):
    """Mock function for os.getenv to simulate environment variable retrieval."""
    print("mock_getenv called")
    return {
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    }.get(key, default)

def get_mock_iam_client():
    """Returns a mock IAM client with predefined behaviors."""
    print("get_mock_iam_client called")
    mock_iam_client = MagicMock()
    mock_iam_client.get_user.return_value = {
        'User': {
            'UserId': 'mock-user-id',
            'Arn': 'arn:aws:iam::123456789012:user/mock-user'
        }
    }
    return mock_iam_client

def mock_s3_list_buckets(*args, **kwargs):
    """
    Mock function to simulate the list_buckets method of an S3 client.
    
    Args:
        *args: Variable arguments.
        **kwargs: Arbitrary keyword arguments.
    
    Returns:
        dict: A dictionary containing a list of mock S3 buckets.
    """
    print("mock_s3_list_buckets called")
    return {
        'Buckets': [
            {'Name': 'bucket1'},
            {'Name': 'bucket2'}
        ]
    }

def get_mock_s3_client():
    """
    Create and return a mock S3 client with predefined behaviors.
    
    Returns:
        MagicMock: A mock S3 client.
    """
    print("get_mock_s3_client called")
    mock_s3_client = MagicMock()
    mock_s3_client.exceptions = MagicMock()
    mock_s3_client.exceptions.NoSuchBucket = NoSuchBucketException
    mock_s3_client.list_buckets.return_value = {
        'Buckets': []
    }
    # Mocking the other methods to raise NoSuchBucket exception
    mock_s3_client.put_object_acl.side_effect = mock_s3_client.exceptions.NoSuchBucket
    mock_s3_client.head_object.side_effect = mock_s3_client.exceptions.NoSuchBucket
    return mock_s3_client

def get_mocked_session(raise_client_error=False):
    """
    Create and return a mock AWS session with predefined behaviors.
    
    Args:
        raise_client_error (bool, optional): Whether to simulate an error for the IAM client's get_user method.
            Defaults to False.
    
    Returns:
        MagicMock: A mock AWS session.
    """
    print("get_mocked_session called")
    mock_iam_client = get_mock_iam_client()
    if raise_client_error:
        mock_iam_client.get_user.side_effect = ClientError({"Error": {"Code": "InvalidClientTokenId", "Message": "The security token included in the request is invalid."}}, "GetUser")
    mock_s3_client = get_mock_s3_client()

    mock_session = MagicMock()
    mock_session.client.side_effect = lambda service_name, **kwargs: mock_iam_client if service_name == 'iam' else mock_s3_client

    return mock_session


@pytest.fixture
def aws_credentials_fixture():
    """
    Pytest fixture to provide mock AWS credentials.
    
    Returns:
        dict: A dictionary containing mock AWS credentials.
    """
    print("aws_credentials_fixture called")
    return {
        'credentials': {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        }
    }

def test_environment_aws_credentials(aws_credentials_fixture):
    """
    Test AWS credentials retrieval from environment variables.
    
    Args:
        aws_credentials_fixture (dict): Mock AWS credentials provided by the aws_credentials_fixture.
    """
    with patch('os.getenv', side_effect=mock_getenv):
        with patch('klingon_file_manager.utils.Session', return_value=get_mocked_session()):
            response = get_aws_credentials()
            print(f"Access Key in the test response: {response['credentials']['AWS_ACCESS_KEY_ID']}")
    assert 'credentials' in response
    assert response['credentials']['AWS_ACCESS_KEY_ID'] == 'AKIAIOSFODNN7EXAMPLE'

def test_missing_aws_access_key():
    """
    Test AWS credentials retrieval when AWS_ACCESS_KEY_ID is missing.
    """
    # Define a mock getenv that doesn't return AWS_ACCESS_KEY_ID
    def mock_getenv_without_access_key(key, default=None):
        return {
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        }.get(key, default)

    with patch('os.getenv', side_effect=mock_getenv_without_access_key):
        with patch('klingon_file_manager.utils.Session', return_value=get_mocked_session()):
            response = get_aws_credentials()
            
    assert response['status'] == 424
    assert response['message'] == 'Failed Dependency - Missing or Incomplete AWS credentials in .env or environment'

def test_missing_aws_secret_access_key():
    """
    Test AWS credentials retrieval when AWS_SECRET_ACCESS_KEY is missing.
    """
    # Define a mock getenv that doesn't return AWS_SECRET_ACCESS_KEY
    def mock_getenv_without_secret_key(key, default=None):
        return {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE'
        }.get(key, default)

    with patch('os.getenv', side_effect=mock_getenv_without_secret_key):
        with patch('klingon_file_manager.utils.Session', return_value=get_mocked_session()):
            response = get_aws_credentials()
            
    assert response['status'] == 424
    assert response['message'] == 'Failed Dependency - Missing or Incomplete AWS credentials in .env or environment'


def test_invalid_aws_credentials():
    """
    Test AWS credentials retrieval when provided with invalid credentials.
    """
    # Define a mock getenv that returns invalid AWS credentials
    def mock_getenv_with_invalid_credentials(key, default=None):
        return {
            'AWS_ACCESS_KEY_ID': 'INVALID_AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'INVALID_wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        }.get(key, default)

    # Mock the boto3 session to raise an exception for invalid credentials
    def mock_session_raises_no_credentials_error(*args, **kwargs):
        raise NoCredentialsError()

    with patch('os.getenv', side_effect=mock_getenv_with_invalid_credentials):
        with patch('klingon_file_manager.utils.Session', side_effect=mock_session_raises_no_credentials_error):
            response = get_aws_credentials()
            
    assert response['status'] == 403
    assert response['message'] == 'Access Denied - AWS credentials are invalid'

def test_missing_aws_secret_key():
    """
    Test AWS credentials retrieval when AWS_SECRET_ACCESS_KEY is missing but AWS_ACCESS_KEY_ID is provided.
    """
    # Define a mock getenv that doesn't return AWS_SECRET_ACCESS_KEY but returns AWS_ACCESS_KEY_ID
    def mock_getenv_without_secret_key(key, default=None):
        return {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE'
        }.get(key, default)

    with patch('os.getenv', side_effect=mock_getenv_without_secret_key):
        response = get_aws_credentials()
        
    assert response['status'] == 424
    assert response['message'] == 'Failed Dependency - Missing or Incomplete AWS credentials in .env or environment'

def test_invalid_iam_aws_credentials():
    """
    Test AWS credentials retrieval when provided with invalid IAM credentials.
    """
    # Define a mock getenv that returns invalid AWS credentials
    def mock_getenv_with_invalid_credentials(key, default=None):
        return {
            'AWS_ACCESS_KEY_ID': 'INVALID_AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'INVALID_wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        }.get(key, default)

    # Mock the get_user method of the IAM client to raise a ClientError for invalid IAM credentials
    def mock_iam_get_user_raises_client_error(*args, **kwargs):
        raise ClientError({"Error": {"Code": "InvalidClientTokenId", "Message": "The security token included in the request is invalid."}}, "GetUser")

    with patch('os.getenv', side_effect=mock_getenv_with_invalid_credentials):
        with patch('klingon_file_manager.utils.Session', return_value=get_mocked_session(raise_client_error=True)):
            with patch('klingon_file_manager.utils.Session.client', return_value=get_mocked_session().client('iam')):
                with patch('klingon_file_manager.utils.Session.client.get_user', side_effect=mock_iam_get_user_raises_client_error):
                    response = get_aws_credentials()
                    
    assert response['status'] == 403

def test_missing_aws_credentials():
    """
    Test AWS credentials retrieval when both AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are missing.
    """
    # Define a mock getenv that returns None for both AWS credentials
    def mock_getenv_no_credentials(key, default=None):
        return {
            'AWS_ACCESS_KEY_ID': None,
            'AWS_SECRET_ACCESS_KEY': None
        }.get(key, default)
    
    with patch('os.getenv', side_effect=mock_getenv_no_credentials):
        response = get_aws_credentials()
        
    assert response['status'] == 424
    assert response['message'] == 'Failed Dependency - Missing or Incomplete AWS credentials in .env or environment'

def test_valid_aws_credentials_with_s3_access():
    """
    Test the retrieval of valid AWS credentials and their usage for S3 access.

    The test involves mocking various functions and methods related to AWS and S3, including:
    - Mocking environment variables for AWS credentials.
    - Mocking S3 methods for listing objects, getting bucket ACL, putting objects, and deleting objects.
    - Mocking parallel_check_bucket_permissions.

    The expected result is that AWS credentials are retrieved successfully, and certain S3 operations are tested.

    """
    # Define a mock getenv that returns valid AWS credentials
    def mock_getenv_valid_credentials(key, default=None):
        return {
            'AWS_ACCESS_KEY_ID': 'VALID_AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'VALID_wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
        }.get(key, default)

    # Mock S3 methods for different scenarios
    def mock_s3_list_objects_v2(Bucket, MaxKeys):
        if Bucket == 'bucket1':
            return {'Contents': []}
        raise s3_client.exceptions.NoSuchBucket()

    def mock_s3_get_bucket_acl(Bucket):
        if Bucket in ['bucket1', 'bucket2']:
            return {}
        raise s3_client.exceptions.NoSuchBucket()

    def mock_s3_put_object(Bucket, Key, Body):
        if Bucket in ['bucket1', 'bucket2']:
            return {}
        raise s3_client.exceptions.NoSuchBucket()

    def mock_s3_delete_object(Bucket, Key):
        if Bucket in ['bucket1', 'bucket2']:
            return {}
        raise s3_client.exceptions.NoSuchBucket()


