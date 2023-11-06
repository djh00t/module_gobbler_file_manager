import pytest
from unittest.mock import MagicMock, patch
from klingon_file_manager.delete import delete_file

def test_delete_local_file_success():
    with patch("os.remove") as mock_remove:
        response = delete_file("/path/to/local/file")
        mock_remove.assert_called_once_with("/path/to/local/file")
        assert response["status"] == 200
        assert response["message"] == "File deleted successfully."

def test_delete_local_file_failure():
    with patch("os.remove", side_effect=Exception("Error")):
        response = delete_file("/path/to/local/file", debug=True)
        assert response["status"] == 500
        assert response["message"] == "Failed to delete file."
        assert "exception" in response["debug"]

def test_delete_s3_file_success():
    with patch("klingon_file_manager.delete.get_aws_credentials", return_value={"status": 200}):
        with patch("boto3.client") as mock_client:
            mock_s3 = MagicMock()
            mock_client.return_value = mock_s3
            response = delete_file("s3://bucket/file")
            mock_s3.delete_object.assert_called_once_with(Bucket="bucket", Key="file")
            assert response["status"] == 200
            assert response["message"] == "File deleted successfully from S3."

def test_delete_s3_file_no_credentials():
    with patch("klingon_file_manager.delete.get_aws_credentials", return_value={"status": 403}):
        response = delete_file("s3://bucket/file")
        assert response["status"] == 403
        assert response["message"] == "AWS credentials not found"

def test_delete_s3_file_failure():
    with patch("klingon_file_manager.delete.get_aws_credentials", return_value={"status": 200}):
        with patch("boto3.client") as mock_client:
            mock_s3 = MagicMock()
            mock_s3.delete_object.side_effect = Exception("S3 Error")
            mock_client.return_value = mock_s3
            response = delete_file("s3://bucket/file", debug=True)
            assert response["status"] == 500
            assert response["message"] == "Failed to delete file from S3."
            assert "exception" in response["debug"]

def test_delete_file_general_exception():
    with patch("os.remove", side_effect=Exception("General Error")):
        response = delete_file("/path/to/local/file", debug=True)
        assert response["status"] == 500
        assert response["message"] == "Failed to delete file."
        assert "exception" in response["debug"]
