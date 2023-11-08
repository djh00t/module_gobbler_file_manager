#test_get.py
"""
# Get File Tests

This module contains pytest unit tests for the `get_file` function, as well as
its helper functions `_get_from_s3` and `_get_from_local` from the
`klingon_file_manager.get` module. It verifies the functionality of file
retrieval from both S3 and local file systems under various scenarios,
including successful reads and exception handling.

Fixtures are used to mock AWS S3 resource calls and file open/read operations
to ensure that tests can run in isolation without requiring actual AWS
resources or file system access.
"""

import pytest
from unittest.mock import patch, mock_open, MagicMock, call
from klingon_file_manager.get import get_file, _get_from_s3, _get_from_local

def mock_s3_get_object():
    """
    # Mock S3 Get Object
    Mocks the retrieval of an S3 object, simulating the `get` operation returning mocked content.
    """
    s3_object = MagicMock()
    s3_object.get.return_value = {'Body': MagicMock(read=lambda: b"mocked content")}
    return s3_object

@pytest.fixture
def mock_boto3_resource():
    """
    # Mock Boto3 Resource
    Fixture that mocks the boto3 resource for S3, returning a mock S3 object upon request.
    """
    with patch('boto3.resource') as mock_resource:
        mock_resource.return_value.Object.return_value = mock_s3_get_object()
        yield mock_resource

@pytest.fixture
def mock_is_binary_file():
    """
    # Mock is_binary_file
    Fixture that mocks the `is_binary_file` function, allowing tests to specify the returned binary status.
    """
    with patch('klingon_file_manager.get.is_binary_file') as mock_binary:
        yield mock_binary

@pytest.fixture
def mock_open_file():
    """
    # Mock Open File
    Fixture that mocks the `open` built-in to simulate reading from a file without accessing the filesystem.
    """
    mocked_file_content = b"mocked file content"
    m = mock_open(read_data=mocked_file_content)
    with patch('builtins.open', m):
        yield m

def test_get_from_s3_success(mock_boto3_resource, mock_is_binary_file):
    """
    # Get from S3 Success
    Verifies that a file can be successfully retrieved from S3 and correctly identifies it as binary or not.
    """
    # Set debug
    debug=True

    # Set src_path
    src_path="s3://mocked_bucket/mocked_key"

    # Define the file content and MD5 hash
    file_content = b"Hello, world!"

    file_md5 = "6cd3556deb0da54bca060b4c39479839"
    get_md5 = file_md5
    
    # Set mock_is_binary_file
    mock_is_binary_file.return_value = True

    # Mock the S3 object to simulate a successful get operation with the expected content and MD5 metadata
    mock_s3_response = {
        'Body': MagicMock(read=lambda: file_content),
        'Metadata': {'md5': get_md5}
    }
    mock_boto3_resource.return_value.Object.return_value.get.return_value = mock_s3_response
    # Ensure that the metadata.get call returns the correct MD5 hash string
    mock_boto3_resource.return_value.Object.return_value.metadata.get.return_value = get_md5
    
    response = _get_from_s3(
        path=src_path,
        debug=debug,
    )
    
    print(f"Result: {response}")
    
    # Use the mocked MD5 value from the mock_s3_response for the expected MD5
    expected_response = {
        "status": 200,
        "message": "File read successfully from S3.",
        "content": file_content,
        "binary": True,
        "debug": {},
        "md5": get_md5
    }
    
    assert response == expected_response

def test_get_from_s3_exception(mock_boto3_resource, mock_is_binary_file):
    """
    # Get from S3 Exception
    Ensures that the appropriate response and debug information is provided when an exception is encountered during S3 file retrieval.
    """
    mock_boto3_resource.return_value.Object.side_effect = Exception("S3 Error")
    
    response = _get_from_s3("s3://mocked_bucket/mocked_key", True)
    assert response["status"] == 500
    assert "S3 Error" in response["debug"]["exception"]

def test_get_from_local_success(mock_open_file, mock_is_binary_file):
    """
    # Get from Local Success
    Verifies that a local file can be successfully read and correctly identifies it as binary or not.
    """
    mock_is_binary_file.return_value = True
    
    response = _get_from_local("/path/to/local/file", False)
    expected_response = {
        "status": 200,
        "message": "File read successfully.",
        "content": b"mocked file content",
        "binary": True,
        "md5": "3137f75275e870ffcb014f020fbc4a37",
        "debug": {}
    }
    
    assert response == expected_response

def test_get_from_local_exception(mock_open_file, mock_is_binary_file):
    """
    # Get from Local Exception
    Ensures that the appropriate response and debug information is provided when an exception is encountered during local file retrieval.
    """
    mock_open_file.side_effect = Exception("File Read Error")
    
    response = _get_from_local("/path/to/local/file", True)
    assert response["status"] == 500
    assert "File Read Error" in response["debug"]["exception"]

def test_get_file_from_s3_success(mock_boto3_resource, mock_is_binary_file):
    """
    # Get File from S3 Success
    Tests the high-level `get_file` function's ability to retrieve a file from S3 successfully.
    """
    mock_is_binary_file.return_value = True
    
    # Mock the get_md5_hash function to return a consistent MD5 value and ensure it is called with the correct arguments
    # Also, ensure that the mocked MD5 value is used in the response
    with patch('klingon_file_manager.get.get_md5_hash', return_value="6cd3556deb0da54bca060b4c39479839") as mock_get_md5_hash:
        mock_boto3_resource.return_value.Object.return_value.metadata.get.return_value = "6cd3556deb0da54bca060b4c39479839"
        response = get_file("s3://mocked_bucket/mocked_key", False)
        expected_response = {
            "status": 200,
            "message": "File read successfully from S3.",
            "content": b"mocked content",
            "binary": True,
            "md5": "6cd3556deb0da54bca060b4c39479839",
            "debug": {}
        }
        
        assert response == expected_response

def test_get_file_from_s3_exception(mock_boto3_resource, mock_is_binary_file):
    """
    # Get File from S3 Exception
    Tests the high-level `get_file` function's handling of exceptions during S3 file retrieval.
    """
    mock_boto3_resource.return_value.Object.side_effect = Exception("S3 Error")
    
    response = get_file("s3://mocked_bucket/mocked_key", True)
    assert response["status"] == 500
    assert "S3 Error" in response["debug"]["exception"]

def test_get_file_from_local_success(mock_open_file, mock_is_binary_file):
    """
    # Get File from Local Success
    Tests the high-level `get_file` function's ability to retrieve a local file successfully.
    """
    mock_is_binary_file.return_value = True
    
    # Mock the get_md5_hash function to return a consistent MD5 value
    with patch('klingon_file_manager.get.get_md5_hash') as mock_get_md5_hash:
        mock_get_md5_hash.return_value = "mocked_md5_hash_value"
        response = get_file("/path/to/local/file", False)
        expected_response = {
            "status": 200,
            "message": "File read successfully.",
            "content": b"mocked file content",
            "binary": True,
            "md5": "mocked_md5_hash_value",
            "debug": {}
        }
        
        assert response == expected_response

def test_get_file_from_local_exception(mock_open_file, mock_is_binary_file):
    """
    # Get File from Local Exception
    Tests the high-level `get_file` function's handling of exceptions during local file retrieval.
    """
    mock_open_file.side_effect = Exception("File Read Error")
    
    response = get_file("/path/to/local/file", True)
    assert response["status"] == 500
    assert "File Read Error" in response["debug"]["exception"]

