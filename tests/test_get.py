#test_get.py

import pytest
from unittest.mock import patch, mock_open, MagicMock
from klingon_file_manager.get import get_file, _get_from_s3, _get_from_local

def mock_s3_get_object():
    s3_object = MagicMock()
    s3_object.get.return_value = {'Body': MagicMock(read=lambda: b"mocked content")}
    return s3_object

@pytest.fixture
def mock_boto3_resource():
    with patch('boto3.resource') as mock_resource:
        mock_resource.return_value.Object.return_value = mock_s3_get_object()
        yield mock_resource

@pytest.fixture
def mock_is_binary_file():
    with patch('klingon_file_manager.get.is_binary_file') as mock_binary:
        yield mock_binary

@pytest.fixture
def mock_open_file():
    mocked_file_content = b"mocked file content"
    m = mock_open(read_data=mocked_file_content)
    with patch('builtins.open', m):
        yield m

def test_get_from_s3_success(mock_boto3_resource, mock_is_binary_file):
    mock_is_binary_file.return_value = True
    
    response = _get_from_s3("s3://mocked_bucket/mocked_key", False)
    expected_response = {
        "status": 200,
        "message": "File read successfully from S3.",
        "content": b"mocked content",
        "binary": True,
        "debug": {}
    }
    
    assert response == expected_response

def test_get_from_s3_exception(mock_boto3_resource, mock_is_binary_file):
    mock_boto3_resource.return_value.Object.side_effect = Exception("S3 Error")
    
    response = _get_from_s3("s3://mocked_bucket/mocked_key", True)
    assert response["status"] == 500
    assert "S3 Error" in response["debug"]["exception"]

def test_get_from_local_success(mock_open_file, mock_is_binary_file):
    mock_is_binary_file.return_value = True
    
    response = _get_from_local("/path/to/local/file", False)
    expected_response = {
        "status": 200,
        "message": "File read successfully.",
        "content": b"mocked file content",
        "binary": True,
        "debug": {}
    }
    
    assert response == expected_response

def test_get_from_local_exception(mock_open_file, mock_is_binary_file):
    mock_open_file.side_effect = Exception("File Read Error")
    
    response = _get_from_local("/path/to/local/file", True)
    assert response["status"] == 500
    assert "File Read Error" in response["debug"]["exception"]

def test_get_file_from_s3_success(mock_boto3_resource, mock_is_binary_file):
    mock_is_binary_file.return_value = True
    
    response = get_file("s3://mocked_bucket/mocked_key", False)
    expected_response = {
        "status": 200,
        "message": "File read successfully from S3.",
        "content": b"mocked content",
        "binary": True,
        "debug": {}
    }
    
    assert response == expected_response

def test_get_file_from_s3_exception(mock_boto3_resource, mock_is_binary_file):
    mock_boto3_resource.return_value.Object.side_effect = Exception("S3 Error")
    
    response = get_file("s3://mocked_bucket/mocked_key", True)
    assert response["status"] == 500
    assert "S3 Error" in response["debug"]["exception"]

def test_get_file_from_local_success(mock_open_file, mock_is_binary_file):
    mock_is_binary_file.return_value = True
    
    response = get_file("/path/to/local/file", False)
    expected_response = {
        "status": 200,
        "message": "File read successfully.",
        "content": b"mocked file content",
        "binary": True,
        "debug": {}
    }
    
    assert response == expected_response

def test_get_file_from_local_exception(mock_open_file, mock_is_binary_file):
    mock_open_file.side_effect = Exception("File Read Error")
    
    response = get_file("/path/to/local/file", True)
    assert response["status"] == 500
    assert "File Read Error" in response["debug"]["exception"]

