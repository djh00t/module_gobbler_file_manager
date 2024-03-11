"""
# Check Bucket Permissions Test Module
Test module for AWS utilities in the klingon_file_manager

This module contains tests for utility functions in the `klingon_file_manager.utils` module that handle AWS operations.

Functions tested:
- `klingon_file_manager.utils.check_bucket_permissions`

Functions in this test module:
- `test_check_bucket_permissions_no_such_bucket_list_objects`
- `test_check_bucket_permissions_no_such_bucket_get_bucket_acl`
- `test_check_bucket_permissions_no_such_bucket_put_delete_object`
- `test_check_bucket_permissions_all_valid`
- `test_check_bucket_permissions_mixed_permissions`

"""
import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.utils import get_aws_credentials, parallel_check_bucket_permissions, check_bucket_permissions, get_mime_type
from botocore.exceptions import NoCredentialsError, ClientError

# Define a custom exception class for NoSuchBucket
class NoSuchBucketException(Exception):
    """
    # NoSuchBucket Exception
    Mock class for NoSuchBucket exceptions.
    """
    pass

def get_mock_s3_client():
    """
    # Get Mock S3 Client
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

# Mock parallel_check_bucket_permissions
def mock_parallel_check_bucket_permissions(*args, **kwargs):
    """
    # Mock Parallel Check Bucket Permissions
    Mock function to simulate the parallel checking of S3 bucket permissions.

    This mock assumes all permissions (DeleteObject, GetBucketAcl, ListBucket, PutObject) are granted
    for 'bucket1' and 'bucket2'. It returns a dictionary with these permissions set to True.

    Args:
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        dict: A dictionary containing the permissions for 'bucket1' and 'bucket2'.
    """
    return {
        'bucket1': {
            'DeleteObject': True,
            'GetBucketAcl': True,
            'ListBucket': True,
            'PutObject': True
        },
        'bucket2': {
            'DeleteObject': True,
            'GetBucketAcl': True,
            'ListBucket': True,
            'PutObject': True
        }
    }
    
    # Perform the actual testing with the mocked functions
    with patch('klingon_file_manager.utils.parallel_check_bucket_permissions', side_effect=mock_parallel_check_bucket_permissions):
        with patch('os.getenv', side_effect=mock_getenv_valid_credentials):
            with patch('klingon_file_manager.utils.Session', return_value=get_mocked_session()):
                with patch('klingon_file_manager.utils.Session.client', side_effect=lambda service_name, **kwargs: get_mock_iam_client() if service_name == 'iam' else get_mock_s3_client()):
                    with patch("boto3.client", return_value=get_mock_s3_client()):
                        with patch("klingon_file_manager.utils.Session.client.list_objects_v2", side_effect=mock_s3_list_objects_v2):
                            with patch("klingon_file_manager.utils.Session.client.get_bucket_acl", side_effect=mock_s3_get_bucket_acl):
                                with patch("klingon_file_manager.utils.Session.client.put_object", side_effect=mock_s3_put_object):
                                    with patch("klingon_file_manager.utils.Session.client.delete_object", side_effect=mock_s3_delete_object):
                                        response = get_aws_credentials()

    # Assertions to check the results
    assert response['status'] == 200
    assert response['message'] == 'AWS credentials retrieved successfully.'
    assert response['credentials']['AWS_ACCESS_KEY_ID'] == 'VALID_AKIAIOSFODNN7EXAMPLE'
    assert response['credentials']['AWS_SECRET_ACCESS_KEY'] == 'VALID_wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    print(response)
    assert 'bucket1' in response['access']




def test_check_bucket_permissions_no_such_bucket_list_objects():
    """
    # Test Check Bucket Permissions: No Such Bucket for List Objects
    Test function to check bucket permissions when the specified bucket does not exist.
    This test focuses on the 'list_objects_v2' operation.

    The function tests the scenario where a ClientError is raised for a nonexistent bucket
    during the list_objects_v2 operation, ensuring that the permissions are reported as False.
    """
    # Create a mock S3 client object
    mock_s3_client = MagicMock()
    
    # Define an error response for the mock S3 client
    error_response = {'Error': {'Code': 'NoSuchBucket', 'Message': 'The specified bucket does not exist'}}
    
    # Set the side effect of the mock S3 client to raise a ClientError with the error response
    mock_s3_client.list_objects_v2.side_effect = ClientError(error_response, 'list_objects_v2')

    # Call the check_bucket_permissions function with a nonexistent bucket name and the mock S3 client
    permissions = check_bucket_permissions('nonexistent-bucket', mock_s3_client)

    # Print the permissions returned by the check_bucket_permissions function
    print(f"Permissions returned: {permissions}")

    # Expected permissions:
    expected = {
        'ListBucket': False, 
        'GetBucketAcl': False, 
        'PutObject': False, 
        'DeleteObject': False
    }

    # Assert that the permissions returned by the check_bucket_permissions
    # function match the expected permissions
    assert permissions == expected


def test_check_bucket_permissions_no_such_bucket_get_bucket_acl():
    """
    # Test Check Bucket Permissions: No Such Bucket for Get Bucket ACL
    Test function to check bucket permissions when the specified bucket does not exist.
    This test focuses on the 'get_bucket_acl' operation.

    The function tests the scenario where a ClientError is raised for a nonexistent bucket
    during the get_bucket_acl operation, ensuring that the permissions are reported as False.
    """
    # Create a mock S3 client object
    mock_s3_client = MagicMock()
    
    # Define an error response for the mock S3 client
    error_response = {'Error': {'Code': 'NoSuchBucket', 'Message': 'The specified bucket does not exist'}}
    
    # Set the side effect of the mock S3 client to raise a ClientError with the error response
    mock_s3_client.get_bucket_acl.side_effect = ClientError(error_response, 'get_bucket_acl')

    # Call the check_bucket_permissions function with a nonexistent bucket name and the mock S3 client
    permissions = check_bucket_permissions('nonexistent-bucket', mock_s3_client)

    # Print the permissions returned by the check_bucket_permissions function
    print(f"Permissions returned: {permissions}")

    # Expected permissions:
    expected = {
        'ListBucket': False, 
        'GetBucketAcl': False, 
        'PutObject': False, 
        'DeleteObject': False
    }

    # Assert that the permissions returned by the check_bucket_permissions
    # function match the expected permissions
    assert permissions == expected


def test_check_bucket_permissions_no_such_bucket_put_delete_object():
    """
    # Test Check Bucket Permissions: No Such Bucket for Put/Delete Object
    Test function to check bucket permissions when the specified bucket does not exist.
    This test focuses on the 'put_object' and 'delete_object' operations.

    The function tests the scenario where a ClientError is raised for a nonexistent bucket
    during put_object and delete_object operations, ensuring that the permissions are reported as False.
    """
    # Create a mock S3 client object
    mock_s3_client = MagicMock()
    
    # Define an error response for the mock S3 client
    error_response = {'Error': {'Code': 'NoSuchBucket', 'Message': 'The specified bucket does not exist'}}
    
    # Set the side effect of the mock S3 client to raise a ClientError with the error response
    mock_s3_client.delete_object.side_effect = ClientError(error_response, 'delete_object')

    # Call the check_bucket_permissions function with a nonexistent bucket name and the mock S3 client
    permissions = check_bucket_permissions('nonexistent-bucket', mock_s3_client)

    # Print the permissions returned by the check_bucket_permissions function
    print(f"Permissions returned: {permissions}")

    # Expected permissions:
    expected = {
        'ListBucket': False, 
        'GetBucketAcl': False, 
        'PutObject': False, 
        'DeleteObject': False
    }

    # Assert that the permissions returned by the check_bucket_permissions
    # function match the expected permissions
    assert permissions == expected

def test_check_bucket_permissions_all_valid():
    """
    # Test Check Bucket Permissions: All Valid
    Test function to check bucket permissions for a valid bucket with all permissions granted.

    This test ensures that when all S3 operations succeed without raising exceptions,
    the check_bucket_permissions function correctly reports all permissions as true.
    """
    mock_s3_client = get_mock_s3_client()
    print(f"mock_s3_client: {mock_s3_client}")

    # Mocking responses to simulate a valid bucket with all permissions
    mock_s3_client.list_objects_v2.return_value = {'Contents': []}
    mock_s3_client.get_bucket_acl.return_value = {}
    mock_s3_client.put_object.return_value = {}
    mock_s3_client.delete_object.return_value = {}

    # Ensure that no exceptions are raised for the put and delete operations
    mock_s3_client.put_object.side_effect = None
    mock_s3_client.delete_object.side_effect = None

    permissions = check_bucket_permissions('valid-bucket', mock_s3_client)
    print(f"Permissions returned: {permissions}")

    assert permissions['ListBucket']
    assert permissions['GetBucketAcl']
    assert permissions['PutObject']
    assert permissions['DeleteObject']


def test_check_bucket_permissions_mixed_permissions():
    """
    # Test Check Bucket Permissions: Mixed Permissions
    Test function to check bucket permissions for a bucket with mixed permissions.

    This test simulates a bucket where ListBucket and GetBucketAcl operations succeed,
    but PutObject and DeleteObject operations are denied, checking that the permissions
    are correctly identified as a mix of True and False.
    """
    # Create a mock S3 client object
    mock_s3_client = MagicMock()

    # Define an error response for the mock S3 client
    error_response_access_denied = {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}}

    # Mock the methods of the S3 client to simulate the desired behavior

    # Simulate successful ListBucket and GetBucketAcl permissions
    mock_s3_client.list_objects_v2.return_value = {'Contents': []}
    mock_s3_client.get_bucket_acl.return_value = {}

    # Simulate failed PutObject and DeleteObject permissions by raising ClientErrors with AccessDenied
    mock_s3_client.put_object.side_effect = ClientError(error_response_access_denied, 'put_object')
    mock_s3_client.delete_object.side_effect = ClientError(error_response_access_denied, 'delete_object')

    # Call the check_bucket_permissions function with a bucket name and the mock S3 client
    permissions = check_bucket_permissions('mixed-permissions-bucket', mock_s3_client)

    # Print the permissions returned by the check_bucket_permissions function
    print(f"Permissions returned: {permissions}")

    # Expected permissions:
    expected = {
        'ListBucket': True,
        'GetBucketAcl': True,
        'PutObject': False,
        'DeleteObject': False
    }

    # Assert that the permissions returned by the check_bucket_permissions
    # function match the expected permissions
    assert permissions == expected