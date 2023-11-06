import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.utils import get_aws_credentials, parallel_check_bucket_permissions, check_bucket_permissions
from botocore.exceptions import NoCredentialsError, ClientError


@patch('klingon_file_manager.utils.check_bucket_permissions')
def test_parallel_check_bucket_permissions(mock_check):
    """
    Test the parallel checking of bucket permissions.

    This function tests the parallel_check_bucket_permissions function by mocking the check_bucket_permissions
    function and providing different permissions for two buckets.

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
