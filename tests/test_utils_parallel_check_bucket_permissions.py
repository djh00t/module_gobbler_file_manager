"""
# Parallel Check Bucket Permissions Test Module
Test module for AWS utilities in the klingon_file_manager

This module contains tests for utility functions in the `klingon_file_manager.utils` module that handle AWS operations.

Functions tested:
- `klingon_file_manager.utils.parallel_check_bucket_permissions`

Functions in this test module:
- `test_parallel_check_bucket_permissions`

"""
import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.utils import get_aws_credentials, parallel_check_bucket_permissions, check_bucket_permissions
from botocore.exceptions import NoCredentialsError, ClientError


@patch('klingon_file_manager.utils.check_bucket_permissions')
def test_parallel_check_bucket_permissions(mock_check):
    """
    # Test Parallel Check Bucket Permissions
    
    Ensures that `klingon_file_manager.utils.parallel_check_bucket_permissions` correctly identifies and returns the permissions for multiple S3 buckets concurrently.

    The test mocks the `check_bucket_permissions` function to simulate varying permissions across two different buckets, and then compares the results against expected values.
    """
    mock_s3_client = MagicMock()
    mock_check.side_effect = lambda bucket_name, s3_client: {
        'bucket1': {
            'ListBucket': True,
            'GetBucketAcl': True,
            'PutObject': True,
            'DeleteObject': True
        },
        'bucket2': {
            'ListBucket': True,
            'GetBucketAcl': True,
            'PutObject': False,
            'DeleteObject': False
        }
    }.get(bucket_name, {})

    result = parallel_check_bucket_permissions(['bucket1', 'bucket2'], mock_s3_client)
    expected = {
        'bucket1': {
            'ListBucket': True,
            'GetBucketAcl': True,
            'PutObject': True,
            'DeleteObject': True
        },
        'bucket2': {
            'ListBucket': True,
            'GetBucketAcl': True,
            'PutObject': False,
            'DeleteObject': False
        }
    }
    assert result == expected
