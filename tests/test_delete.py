# test_delete.py
"""
# Delete Tests

This module contains pytest unit tests for the `delete_file` function from the
`klingon_file_manager.delete` module. It tests both local and S3 file deletions
under various conditions.

"""
import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.delete import delete_file


def test_delete_local_file_success():
    """
    # Delete Local File Success
    Ensures that a local file is successfully deleted without affecting the local filesystem by mocking the `os.remove` call.
    Verifies that `os.remove` is called with the correct path and that the response indicates successful deletion.
    """
    # Patch the os.remove function to simulate file deletion without affecting the local file system.
    with patch("os.remove") as mock_remove:
        # Call the delete_file function with the path to the file we want to delete.
        response = delete_file("/path/to/local/file")
        # Check that os.remove was called once with the correct file path.
        mock_remove.assert_called_once_with("/path/to/local/file")
        # Assert that the response status and message indicate a successful deletion.
        assert response["status"] == 200
        assert response["message"] == "File deleted successfully."

def test_delete_local_file_failure():
    """
    # Delete Local File Failure
    Tests local file deletion when an exception occurs. It simulates a failure by causing `os.remove` to raise an Exception.
    Verifies that the response indicates failure and contains exception details in debug mode.
    """
    # Patch the os.remove function to raise an exception to simulate an error during file deletion.
    with patch("os.remove", side_effect=Exception("Error")):
        # Call the delete_file function with the path to the file we want to delete and debug mode enabled.
        response = delete_file("/path/to/local/file", debug=True)
        # Assert that the response status and message indicate a failure in file deletion.
        assert response["status"] == 500
        assert response["message"] == "Failed to delete file."
        # Assert that the debug information contains the exception details.
        assert "exception" in response["debug"]

def test_delete_s3_file_success():
    """
    # Delete S3 File Success
    Tests successful deletion of a file from S3. It mocks AWS credential retrieval and the `boto3.client` to simulate S3 interactions.
    Verifies that `delete_object` is called with the correct parameters and that the response indicates successful deletion from S3.
    """
    # Patch the get_aws_credentials function to return successful status to simulate having valid AWS credentials.
    with patch("klingon_file_manager.delete.get_aws_credentials", return_value={"status": 200}):
        # Mock the boto3 client to simulate interaction with AWS S3 without making actual network calls.
        with patch("boto3.client") as mock_client:
            mock_s3 = MagicMock()
            mock_client.return_value = mock_s3
            # Call the delete_file function with the S3 URI of the file we want to delete.
            response = delete_file("s3://bucket/file")
            # Check that delete_object was called once with the correct bucket and key.
            mock_s3.delete_object.assert_called_once_with(Bucket="bucket", Key="file")
            # Assert that the response status and message indicate a successful deletion from S3.
            assert response["status"] == 200
            assert response["message"] == "File deleted successfully from S3."

def test_delete_s3_file_no_credentials():
    """
    # Delete S3 File No Credentials
    Tests file deletion from S3 when AWS credentials are missing. It simulates missing credentials by returning a 403 status.
    Verifies that the response indicates failure due to missing AWS credentials.
    """
    # Patch the get_aws_credentials function to return a 403 status to simulate missing AWS credentials.
    with patch("klingon_file_manager.delete.get_aws_credentials", return_value={"status": 403}):
        # Call the delete_file function with the S3 URI of the file we want to delete.
        response = delete_file("s3://bucket/file")
        # Assert that the response indicates a failure due to missing AWS credentials.
        assert response["status"] == 403
        assert response["message"] == "AWS credentials not found"

def test_delete_s3_file_failure():
    """
    # Delete S3 File Failure
    Tests S3 file deletion when an S3-related exception occurs. It mocks AWS credential retrieval and the `boto3.client`, causing an exception.
    Verifies that the response indicates a failure in deleting from S3 and contains exception details in debug mode.
    """
    # Patch the get_aws_credentials function to return successful status to simulate having valid AWS credentials.
    with patch("klingon_file_manager.delete.get_aws_credentials", return_value={"status": 200}):
        # Mock the boto3 client and simulate an exception during the S3 delete operation.
        with patch("boto3.client") as mock_client:
            mock_s3 = MagicMock()
            mock_s3.delete_object.side_effect = Exception("S3 Error")
            mock_client.return_value = mock_s3
            # Call the delete_file function with the S3 URI of the file we want to delete and debug mode enabled.
            response = delete_file("s3://bucket/file", debug=True)
            # Assert that the response status and message indicate a failure in deleting from S3.
            assert response["status"] == 500
            assert response["message"] == "Failed to delete file from S3."
            # Assert that the debug information contains the exception details.
            assert "exception" in response["debug"]

def test_delete_file_general_exception():
    """
    # Delete File General Exception
    Tests file deletion when a general exception occurs, simulating an error by causing `os.remove` to raise a general Exception.
    Verifies that the response indicates a general failure in file deletion and contains exception details in debug mode.
    """
    # Patch the os.remove function to raise a general exception to simulate an error.
    with patch("os.remove", side_effect=Exception("General Error")):
        # Call the delete_file function with the path to the file we want to delete and debug mode enabled.
        response = delete_file("/path/to/local/file", debug=True)
        # Assert that the response status and message indicate a general failure in file deletion.
        assert response["status"] == 500
        assert response["message"] == "Failed to delete file."
        # Assert that the debug information contains the exception details.
        assert "exception" in response["debug"]