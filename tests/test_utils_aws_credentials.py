# test_utils_aws_credentials.py
"""
# AWS Credentials
Test module for AWS utilities in the klingon_file_manager

This module contains tests for utility functions in the `klingon_file_manager.utils` module that handle AWS operations.

Functions tested:
- `klingon_file_manager.utils.get_aws_credentials`

The module also contains various mock and helper functions to assist in testing.

Functions in this test module:
- `test_environment_aws_credentials`
- `test_missing_aws_access_key`
- `test_missing_aws_secret_access_key`
- `test_invalid_aws_credentials`
- `test_missing_aws_secret_key`
- `test_invalid_iam_aws_credentials`
- `test_missing_aws_credentials`
- `test_valid_aws_credentials_with_s3_access`

"""
import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.utils import get_aws_credentials
from botocore.exceptions import NoCredentialsError, ClientError


# Define a custom exception class for NoSuchBucket
class NoSuchBucketException(Exception):
    """
    # No Such Bucket Exception
    A custom exception class to simulate the `NoSuchBucket` error that may be
    encountered when interacting with AWS S3 services.
    """
    pass

def mock_getenv(key, default=None):
    """
    # Mock Get Environment Variable
    A mock function to replace `os.getenv`. It simulates the retrieval of
    environment variables, specifically returning predetermined AWS
    credentials. 
    """
    print("mock_getenv called")
    return {
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    }.get(key, default)

def get_mock_iam_client():
    """
    # Get Mock IAM Client
    Creates a mock IAM client that simulates the response of AWS IAM's
    `get_user` method, returning a fixed user ID and ARN.
    """
    print("get_mock_iam_client called")
    mock_iam_client = MagicMock()
    mock_iam_client.get_user.return_value = {
        'User': {
            'UserId': 'mock-user-id',
            'Arn': 'arn:aws:iam::123456789012:user/mock-user'
        }
    }
    return mock_iam_client

def get_mock_s3_client():
    """
    # Get Mock S3 Client
    Generates a mock S3 client that predefines behaviors for S3 service
    interactions, such as listing buckets and handling exceptions like
    `NoSuchBucket`.
    
    Returns:
        MagicMock: A mock AWS session.
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
    # Get Mocked Session
    Produces a mock AWS session, optionally simulating an error for the IAM client's `get_user` method to test error handling in credential retrieval.
    
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
    # AWS Credentials Fixture
    A Pytest fixture that provides a set of mock AWS credentials for use in
    tests, ensuring consistency across multiple test functions.
    
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
    # Test Environment AWS Credentials
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
    # Test Missing AWS Access Key
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
    # Test Missing AWS Secret Access Key
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
    # Test Invalid AWS Credentials
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
    # Test Missing AWS Secret Key
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
    # Test Invalid IAM AWS Credentials
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
    # Test Missing AWS Credentials
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
    # Test Valid AWS Credentials with S3 Access
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


