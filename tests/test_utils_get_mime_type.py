"""
This module contains pytest test cases for various functions related to file management and AWS S3 interactions.

The functions tested in this file include:
1. test_get_mime_type_local_text_file: Tests the get_mime_type function with a local text file.
2. test_get_mime_type_existing_s3_file: Tests the get_mime_type function with an existing S3 file.
3. test_get_mime_type_existing_s3_file_with_md5_metadata: Tests retrieving metadata for an existing S3 file.
4. test_get_mime_type_nonexistent_s3_file: Tests the get_mime_type function with a nonexistent S3 file.

"""

import pytest
from klingon_file_manager import (
    timing_decorator, get_mime_type, get_aws_credentials, is_binary_file, get_s3_metadata, parallel_check_bucket_permissions
)
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Get the AWS S3 bucket name from the environment variable
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

# Test with a local text file
def test_get_mime_type_local_text_file():
    """
    Test function to get the MIME type of a local text file.

    This test creates a temporary text file and checks if the MIME type
    is correctly identified as "text/plain".

    """
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(b"Hello, world!")
        file_path = temp_file.name
        print(f"file_path: {file_path}")

    result = get_mime_type(file_path)
    assert result['status'] == 200
    assert result['mime_type'] == "text/plain"

# Test with an S3 file using the AWS_S3_BUCKET_NAME environment variable
def test_get_mime_type_existing_s3_file():
    """
    Test function to get the MIME type of an existing S3 file.

    This test checks if the MIME type of an existing S3 file is correctly identified.

    """
    if AWS_S3_BUCKET_NAME:
        # Define the S3 URL
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/development/unit-tests/UNITTEST_20230705_035512_61355551234_1234.wav"

        # Call the get_mime_type function
        result = get_mime_type(s3_url)
        assert result['status'] == 200
        assert result['mime_type'] == "audio/x-wav"


def test_get_mime_type_existing_s3_file_with_md5_metadata():
    """
    Test function to retrieve metadata for an existing S3 file.

    This test retrieves metadata for an existing S3 file and checks if the MD5 value
    and MIME type are correct.

    """
    if AWS_S3_BUCKET_NAME:
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/development/unit-tests/audio-test.wav"
        metadata = get_s3_metadata(s3_url)
        # Retrieve md5 value from Metadata key in metadata dictionary
        md5_check = metadata.get("Metadata").get("md5")
        # Retrieve mime_type value from metadata dictionary
        mime_type = metadata.get("mime_type")

        print(f"md5: {md5_check}")
        print(f"mime_type: {mime_type}")
        assert md5_check == "f63bbe640a48144acd9b608b5eba4596"

# Test with an S3 file that doesn't exist using the AWS_S3_BUCKET_NAME environment variable
def test_get_mime_type_nonexistent_s3_file():
    """
    Test function to get the MIME type of a nonexistent S3 file.

    This test checks if a nonexistent S3 file correctly returns a status of 404.

    """
    if AWS_S3_BUCKET_NAME:
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/tests/nonexistent-file.jpg"
        mime_type = get_mime_type(s3_url)
        # Assert that there will be a status=404 error returned in the
        # mime_type dictionary
        assert mime_type['status'] == 404

def test_get_mime_type_invalid_file_path_blank():
    """
    Test function to check the handling of an invalid file_path argument.

    This test checks if the function handles an invalid file_path correctly,
    such as an empty string or a non-existent local file path.

    """
    result = get_mime_type('')
    assert result['status'] == 500
    assert result['message'] == 'Internal Server Error'
    assert result['mime_type'] is None


def test_get_mime_type_invalid_file_path_noexist():
    """
    Test function to check the handling of an invalid file_path argument.

    This test checks if the function handles an invalid file_path correctly,
    such as an empty string or a non-existent local file path.

    """
    result = get_mime_type('nonexistent-file.txt')
    assert result['status'] == 404
    assert result['message'] == 'Not Found - The file you have requested does not exist'
    assert result['mime_type'] is None

def test_get_mime_type_s3_object_not_found():
    """
    Test function to check the handling of a non-existent S3 object.

    This test simulates the case where an S3 object does not exist,
    and the function should return a status of 404.

    """
    s3_url = f"s3://{AWS_S3_BUCKET_NAME}/nonexistent-object.jpg"
    result = get_mime_type(s3_url)
    print(f"result: {result}")
    assert result['status'] == 404
    assert result['message'] == 'Not Found - The S3 file you have requested does not exist'
    assert result['mime_type'] is None
