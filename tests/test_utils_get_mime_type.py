"""
# Get MIME Type Utility Function Tests
Test module for AWS utilities in the klingon_file_manager

This module contains tests for utility functions in the `klingon_file_manager.utils` module that handle AWS operations.

Functions tested:
- `klingon_file_manager.utils.get_mime_type`
- `klingon_file_manager.utils.get_s3_metadata`

Functions in this test module:
- `test_get_mime_type_local_text_file`
- `test_get_mime_type_existing_s3_file`
- `test_get_mime_type_existing_s3_file_with_md5_metadata`
- `test_get_mime_type_nonexistent_s3_file`
- `test_get_mime_type_invalid_file_path_blank`
- `test_get_mime_type_invalid_file_path_noexist`
- `test_get_mime_type_s3_object_not_found`

"""

import pytest
from klingon_file_manager import (
    timing_decorator, get_mime_type, get_aws_credentials, is_binary_file, get_s3_metadata, parallel_check_bucket_permissions
)
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

## Define Constants
# Get the AWS S3 bucket name from the environment variable
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
""" The AWS S3 bucket name to use for testing. @private"""

# Test Audio File
test_audio = 's3://{AWS_S3_BUCKET_NAME}/development/unit-tests/do-not-delete/UNITTEST_20230705_035512_61355551234_1234.wav'
test_audio_md5 = 'f63bbe640a48144acd9b608b5eba4596'

# Test Text File
test_text = b"Hello, world!"
test_text_md5 = '6cd3556deb0da54bca060b4c39479839'


# Test with a local text file
def test_get_mime_type_local_text_file():
    """
    # Test Get MIME Type: Local Text File
    Test the `klingon_file_manager.utils.get_mime_type` function with a local text file to ensure it correctly identifies
    the MIME type as "text/plain".

    This involves creating a temporary text file, invoking the function, and asserting the
    expected MIME type in the response.
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
    # Test Get MIME Type: Existing S3 File
    Validates that the `klingon_file_manager.utils.get_mime_type` function can accurately determine the MIME type of an
    existing file stored in an S3 bucket.

    The test relies on the AWS_S3_BUCKET_NAME environment variable to construct the S3 URL,
    then checks the returned MIME type against an expected value.
    """
    if AWS_S3_BUCKET_NAME:
        # Define the S3 URL
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/development/unit-tests/do-not-delete/UNITTEST_20230705_035512_61355551234_1234.wav"

        # Call the get_mime_type function
        result = get_mime_type(s3_url)
        assert result['status'] == 200
        assert result['mime_type'] == "audio/x-wav"


def test_get_mime_type_existing_s3_file_with_md5_metadata():
    """
    # Test Get MIME Type: Existing S3 File with MD5 Metadata
    Confirms that `klingon_file_manager.utils.get_s3_metadata` can retrieve the correct metadata for an S3 file, focusing
    on the MD5 checksum and MIME type.

    It uses the AWS_S3_BUCKET_NAME environment variable to access the S3 file and asserts that
    the retrieved metadata matches the expected values.
    """
    if AWS_S3_BUCKET_NAME:
        path = f"s3://{AWS_S3_BUCKET_NAME}/development/unit-tests/do-not-delete/UNITTEST_20230705_035512_61355551234_1234.wav"
        print(f"path: {path}")
        metadata = get_s3_metadata(path)
        # Retrieve md5 value from Metadata key in metadata dictionary
        print(f"metadata: {metadata}")
        md5_check = metadata['md5']
        # Retrieve mime_type value from metadata dictionary
        mime_type = metadata.get("mime_type")

        print(f"md5: {md5_check}")
        print(f"mime_type: {mime_type}")
        assert md5_check == "f63bbe640a48144acd9b608b5eba4596", f"MD5 metadata does not match the expected value. Expected: 'f63bbe640a48144acd9b608b5eba4596', Got: '{md5_check}'"

# Test with an S3 file that doesn't exist using the AWS_S3_BUCKET_NAME environment variable
def test_get_mime_type_nonexistent_s3_file():
    """
    # Test Get MIME Type: Nonexistent S3 File
    Checks the `klingon_file_manager.utils.get_mime_type` function's response when attempting to retrieve the MIME type for
    an S3 file that does not exist.

    It constructs a hypothetical S3 URL for a nonexistent file and asserts that the function
    returns a 404 status code.
    """
    if AWS_S3_BUCKET_NAME:
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/tests/nonexistent-file.jpg"
        mime_type = get_mime_type(s3_url)
        # Assert that there will be a status=404 error returned in the
        # mime_type dictionary
        assert mime_type['status'] == 404

def test_get_mime_type_invalid_file_path_blank():
    """
    # Test Get MIME Type: Invalid File Path - Blank
    Tests the `klingon_file_manager.utils.get_mime_type` function's error handling when provided with an invalid (blank)
    file path argument.

    This test ensures that an appropriate error message and a 500 status code are returned
    when an empty string is passed to the function.
    """
    result = get_mime_type('')
    assert result['status'] == 500
    assert result['message'] == 'Internal Server Error'
    assert result['mime_type'] is None


def test_get_mime_type_invalid_file_path_noexist():
    """
    # Test Get MIME Type: Invalid File Path - Nonexistent File
    Evaluates the `klingon_file_manager.utils.get_mime_type` function's behavior with a nonexistent file path to ensure it
    correctly returns a 404 status and the corresponding error message.

    The function is called with a path to a nonexistent file and the test checks that the response
    indicates the file does not exist.
    """
    result = get_mime_type('nonexistent-file.txt')
    assert result['status'] == 404
    assert result['message'] == 'Not Found - The file you have requested does not exist'
    assert result['mime_type'] is None

def test_get_mime_type_s3_object_not_found():
    """
    # Test Get MIME Type: S3 Object Not Found
    Verifies the `klingon_file_manager.utils.get_mime_type` function's handling of a scenario where the specified S3 object
    cannot be found.

    The test constructs an S3 URL for a non-existent object and asserts that the function returns
    a 404 status with an error message indicating the object does not exist.
    """
    s3_url = f"s3://{AWS_S3_BUCKET_NAME}/nonexistent-object.jpg"
    result = get_mime_type(s3_url)
    print(f"result: {result}")
    assert result['status'] == 404
    assert result['message'] == 'Not Found - The S3 file you have requested does not exist'
    assert result['mime_type'] is None
