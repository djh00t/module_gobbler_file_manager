"""
# Move File Tests

This module contains pytest unit tests for the `move_file` function from the
`klingon_file_manager.manage` module. It tests the file moving process under various conditions.

"""
import pytest
from unittest.mock import patch, MagicMock, call
from klingon_file_manager import move_file


# Mock the get_file, post_file, and delete_file functions
@patch("klingon_file_manager.manage.get_md5_hash")
@patch("klingon_file_manager.manage.get_md5_hash_filename")
@patch("klingon_file_manager.manage.delete_file")
@patch("klingon_file_manager.manage.post_file")
@patch("klingon_file_manager.manage.get_file")
def test_move_file(
    mock_get_file,
    mock_post_file,
    mock_delete_file,
    mock_get_md5_hash,
    mock_get_md5_hash_filename,
):
    """
    # Move File Test
    Tests the `move_file` function by mocking the `get_file`, `post_file`, and `delete_file` functions.
    Verifies that the `move_file` function returns a successful status and the correct source and destination paths.
    """
    # Set debug
    debug = True
    
    # Define the source and destination paths
    src_path = "/path/to/source/file"
    dst_path = "/path/to/destination/file"

    # Define the file content and MD5 hash
    file_content = b"Hello, world!"
    
    file_md5 = "6cd3556deb0da54bca060b4c39479839"
    get_md5 = file_md5
    post_md5 = file_md5
    dst_md5 = file_md5

    # Correct the setup of mocked return values to match the expected function actions:
    mock_get_file.return_value = {
        "status": 200,
        "message": "File read successfully.",
        "content": file_content,
        "binary": False,
        "md5": get_md5,
        "debug": {},
    }

    # Set up the mock post_file function to return a successful status
    mock_post_file.return_value = {
        "status": 200,
        "message": "File written successfully.",
        "md5": post_md5,
        "debug": {},
    }

    # Set up the mock delete_file function to return a successful status
    mock_delete_file.return_value = {
        "status": 200,
        "message": "File deleted successfully.",
        "debug": {},
    }

    # Set up the mock get_md5_hash function to return the file MD5 hash
    mock_get_md5_hash.return_value = file_md5

    # Set up the mock get_md5_hash_filename function to return the file MD5 hash
    mock_get_md5_hash_filename.return_value = file_md5

    # Call the move_file function with debug=True to capture debug information
    result = move_file(
        src_path=src_path,
        dst_path=dst_path,
        debug=debug
    )
    
    print(f"SRC MD5: {get_md5}")
    print(f"POST MD5: {post_md5}")
    print(f"DEST MD5: {dst_md5}")

    print(f"Result: {result}")
    
    # Print debug information for each mocked function call
    print(f"Debug Info: {result.get('debug', {})}")

    # Validate that the test ran to completion successfully
    assert result["status"] == 200

    # Validate that all three md5 hashes are the same
    assert get_md5 == post_md5 == dst_md5

    # Verify that mock_get_file is called with the correct source path
    mock_get_file.assert_called_with(path=src_path, debug=debug)

    # Verify that mock_get_file returns the expected dictionary
    assert mock_get_file.return_value == {
        "status": 200,
        "message": "File read successfully.",
        "content": file_content,
        "binary": False,
        "md5": get_md5,
        "debug": {},
    }

    # Verify that mock_post_file is called with the correct destination path and content
    mock_post_file.assert_called_with(
        path=dst_path, content=file_content, debug=debug
    )

    # Verify that mock_post_file returns the expected dictionary
    assert mock_post_file.return_value == {
        "status": 200,
        "message": "File written successfully.",
        "md5": post_md5,
        "debug": {},
    }

    # Verify that mock_delete_file returns the expected dictionary
    assert mock_delete_file.return_value == {
        "status": 200,
        "message": "File deleted successfully.",
        "debug": {},
    }

    # Verify that mock_get_md5_hash is called three times
    assert mock_get_md5_hash.call_count == 1


@patch("klingon_file_manager.manage.get_file")
def test_move_file_get_file_fails(
    mock_get_file
):
    """
    # Move File Get File Fails Test
    Tests the `move_file` function when the `get_file` function fails.
    Verifies that the `move_file` function returns a failure status.
    """
    # Set debug
    debug = True
    
    # Define the source and destination paths
    src_path = "/path/to/source/file"
    dst_path = "/path/to/destination/file"

    # Set up the mock get_file function to return a 500 failure status
    mock_get_file.return_value = {
        "status": 500,
        "message": "Failed to get file from local.",
        "content": None,
        "binary": None,
        "md5": None,
        "debug": {},
    }

    # Call the move_file function
    result = move_file(
        src_path=src_path,
        dst_path=dst_path,
        debug=debug,
    )

    print(f"Result: {result}")

    # Assert that the move_file function returned a failure status
    assert result["status"] == 500

    # Verify that mock_get_file is called with the correct source path
    mock_get_file.assert_called_with(path=src_path, debug=debug)


@patch("klingon_file_manager.manage.get_file")
@patch("klingon_file_manager.manage.post_file")
def test_move_file_post_file_fails(
    mock_post_file,
    mock_get_file
):
    """
    # Move File Post File Fails Test
    Tests the `move_file` function when the `post_file` function fails.
    Verifies that the `move_file` function returns a failure status.
    """
    # Set debug
    debug = True
    
    # Define the source and destination paths
    src_path = "/path/to/source/file"
    dst_path = "/path/to/destination/file"

    # Define the file content and MD5 hash
    file_content = b"Hello, world!"
    
    file_md5 = "6cd3556deb0da54bca060b4c39479839"
    get_md5 = file_md5
    post_md5 = file_md5
    dst_md5 = file_md5

    # Correct the setup of mocked return values to match the expected function actions:
    mock_get_file.return_value = {
        "status": 200,
        "message": "File read successfully.",
        "content": file_content,
        "binary": False,
        "md5": get_md5,
        "debug": {},
    }

    # Set up the mock post_file function to return a failure status
    mock_post_file.return_value = mock_post_file.return_value = {
        "status": 500,
        "message": "Failed to post file.",
        "md5": post_md5,
        "debug": {},
    }

    # Call the move_file function with debug=True to capture debug information
    result = move_file(
        src_path=src_path,
        dst_path=dst_path,
        debug=debug
    )

    # Assert that the move_file function returned a 500 failure status
    assert result["status"] == 500

    # Assert that the correct message is returned
    assert result["message"] == "Failed to post file."

    # Assert that the md5 hash matches the expected value
    assert result["md5"] == post_md5

    # Assert that the get_file and post_file functions were called with the correct arguments
    mock_get_file.assert_called_once_with(path=src_path, debug=debug)

    # Ensure the mock_post_file is called with the expected arguments
    mock_post_file.assert_called_once_with(
        path=dst_path, content=file_content, debug=debug
    )


@patch("klingon_file_manager.manage.get_md5_hash")
@patch("klingon_file_manager.manage.get_md5_hash_filename")
@patch("klingon_file_manager.manage.get_file")
@patch("klingon_file_manager.manage.post_file")
@patch("klingon_file_manager.manage.delete_file")
def test_move_file_delete_file_fails(
    mock_delete_file,
    mock_post_file,
    mock_get_file,
    mock_get_md5_hash,
    mock_get_md5_hash_filename,
):
    """
    # Move File Delete File Fails Test
    Tests the `move_file` function when the `delete_file` function fails.
    Verifies that the `move_file` function returns a failure status.
    """
    # Set debug
    debug = True

    # Define the source and destination paths
    src_path = "/path/to/source/file"
    dst_path = "/path/to/destination/file"

    # Define the file content and MD5 hash
    file_content = b"Hello, world!"
    file_md5 = "6cd3556deb0da54bca060b4c39479839"
    get_md5 = file_md5
    post_md5 = file_md5
    dst_md5 = file_md5

    # Set up the mock get_file function to return the file content and MD5 hash
    mock_get_file.return_value = {
        "status": 200,
        "message": "File read successfully.",
        "content": file_content,
        "binary": False,
        "md5": get_md5,
        "debug": {},
    }

    # Set up the mock post_file function to return a successful status
    mock_post_file.return_value = {
        "status": 200,
        "message": "File written successfully.",
        "md5": post_md5,
        "debug": {},
    }

    # Set up the mock delete_file function to return a failure status
    mock_delete_file.return_value = {
        "status": 500,
        "message": "Failed to delete file.",
        "debug": {},
    }

    # Set up the mock get_md5_hash function to return the file MD5 hash
    mock_get_md5_hash.return_value = file_md5

    # Set up the mock get_md5_hash_filename function to return the file MD5 hash
    mock_get_md5_hash_filename.return_value = file_md5

    # Call the move_file function
    result = move_file(
        src_path=src_path,
        dst_path=dst_path,
        debug=debug,
    )

    print(f"Test Result: {result}")

    # Assert that the move_file function returned a failure status
    assert result["status"] == 500

    # Verify that mock_get_file is called with the correct source path
    mock_get_file.assert_called_with(
        path=src_path,
        debug=debug,
    )

    # Verify that mock_get_file returns the expected dictionary
    assert mock_get_file.return_value == {
        "status": 200,
        "message": "File read successfully.",
        "content": file_content,
        "binary": False,
        "md5": get_md5,
        "debug": {},
    }

    # Verify that mock_post_file is called with the correct destination path and content
    mock_post_file.assert_called_with(
        path=dst_path,
        content=file_content,
        debug=debug,
    )

    # Verify that mock_post_file returns the expected dictionary
    assert mock_post_file.return_value == {
        "status": 200,
        "message": "File written successfully.",
        "md5": post_md5,
        "debug": {},
    }

    mock_delete_file.assert_called_once_with(
        path=src_path,
        debug=debug,
    )

    # Verify that mock_delete_file returns the expected dictionary
    assert mock_delete_file.return_value == {
        "status": 500,
        "message": "Failed to delete file.",
        "debug": {},
    }

@patch("klingon_file_manager.manage.get_md5_hash")
@patch("klingon_file_manager.manage.get_md5_hash_filename")
@patch("klingon_file_manager.manage.delete_file")
@patch("klingon_file_manager.manage.post_file")
@patch("klingon_file_manager.manage.get_file")
def test_move_file_md5_mismatch(
    mock_get_file,
    mock_post_file,
    mock_delete_file,
    mock_get_md5_hash,
    mock_get_md5_hash_filename,
):
    """
    # Move File MD5 Mismatch Test
    Tests the `move_file` function when the MD5 hashes of the source and destination files do not match.
    Verifies that the `move_file` function returns a failure status due to MD5 mismatch.
    """
    # Set debug
    debug = True
    
    # Define the source and destination paths
    src_path = "/path/to/source/file"
    dst_path = "/path/to/destination/file"

    # Define the file content and MD5 hash
    file_content = b"Hello, world!"

    # Define different MD5 hashes for the source and destination files
    file_md5 = "6cd3556deb0da54bca060b4c39479839"
    get_md5 = file_md5
    post_md5 = "different_md5_hash"
    dst_md5 = post_md5

    # Correct the setup of mocked return values to match the expected function actions:
    mock_get_file.return_value = {
        "status": 200,
        "message": "File read successfully.",
        "content": file_content,
        "binary": False,
        "md5": get_md5,
        "debug": {},
    }

    # Set up the mock post_file function to return a successful status
    mock_post_file.return_value = {
        "status": 200,
        "message": "File written successfully.",
        "md5": post_md5,
        "debug": {},
    }

    # Set up the mock delete_file function to return a successful status
    mock_delete_file.return_value = {
        "status": 200,
        "message": "File deleted successfully.",
        "debug": {},
    }
    
    # Set up the mock get_md5_hash function to return the file MD5 hash
    mock_get_md5_hash.return_value = file_md5

    # Set up the mock get_md5_hash_filename function to return the file MD5 hash
    mock_get_md5_hash_filename.return_value = file_md5

    # Call the move_file function with debug=True to capture debug information
    result = move_file(
        src_path=src_path,
        dst_path=dst_path,
        debug=debug,
    )

    print(f"SRC MD5: {get_md5}")
    print(f"POST MD5: {post_md5}")
    print(f"DEST MD5: {dst_md5}")

    print(f"Result: {result}")

    # Print debug information for each mocked function call
    print(f"Debug Info: {result.get('debug', {})}")

    # Assert that the move_file function returned a 500 status
    assert result["status"] == 500

    # Assert that the correct message is returned
    assert result["message"] == 'MD5 checksums do not match!'

    # Verify that mock_get_file is called with the correct source path
    mock_get_file.assert_called_with(
        path=src_path,
        debug=debug,
    )

    # Verify that mock_get_file returns the expected dictionary
    assert mock_get_file.return_value == {
        "status": 200,
        "message": "File read successfully.",
        "content": file_content,
        "binary": False,
        "md5": get_md5,
        "debug": {},
    }

    # Assert that the post_file function is called with the correct arguments
    mock_post_file.assert_called_with(
        path=dst_path,
        content=file_content,
        debug=debug,
    )

@patch("klingon_file_manager.manage.get_file")
@patch("klingon_file_manager.manage.post_file")
@patch("klingon_file_manager.manage.delete_file")
def test_move_file_exception_raised(
    mock_delete_file, mock_post_file, mock_get_file
):
    """
    # Move File Exception Raised Test
    Tests the `move_file` function when an exception is raised.
    Verifies that the `move_file` function returns a failure status and the correct error message.
    """
    # Set debug
    debug = True
    
    # Define the source and destination paths
    src_path = "/path/to/source/file"
    dst_path = "/path/to/destination/file"

    # Set up the mock get_file function to raise an exception
    mock_get_file.side_effect = Exception("Test exception")

    # Call the move_file function
    result = move_file(src_path, dst_path)

    # Assert that the move_file function returned a failure status
    assert result["status"] == 500
    assert (
        result["message"]
        == "An error occurred while moving the file: Test exception"
    )
