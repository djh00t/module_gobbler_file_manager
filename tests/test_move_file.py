import pytest
from unittest.mock import patch, MagicMock, call
from klingon_file_manager.manage import move_file

# Mock the get_file, post_file, and delete_file functions
@patch('klingon_file_manager.manage.get_file')
@patch('klingon_file_manager.manage.post_file')
@patch('klingon_file_manager.manage.delete_file')
def test_move_file(mock_delete_file, mock_post_file, mock_get_file):
    # Define the source and destination paths
    source_path = '/path/to/source/file'
    dest_path = '/path/to/destination/file'

    # Define the file content and MD5 hash
    file_content = b'Hello, world!'
    file_md5 = 'fc3ff98e8c6a0d3087d515c0473f8677'

    # Set up the mock get_file function to return the file content and MD5 hash
    mock_get_file.return_value = {'status': 200, 'content': file_content, 'md5': file_md5}

    # Set up the mock post_file function to return a successful status
    mock_post_file.return_value = {'status': 200}

    # Set up the mock delete_file function to return a successful status
    mock_delete_file.return_value = {'status': 200}

    # Call the move_file function
    result = move_file(source_path, dest_path)

    # Assert that the move_file function returned a successful status
    assert result['status'] == 200

    # Assert that the move_file function returned the correct source and destination paths
    assert result['source'] == source_path
    assert result['destination'] == dest_path

    # Assert that the move_file function returned the correct MD5 hash
    assert result['md5'] == file_md5

    # Assert that the get_file, post_file, and delete_file functions were called with the correct arguments
    calls = [call(source_path, False), call(dest_path, False)]
    mock_get_file.assert_has_calls(calls)
    mock_post_file.assert_called_once_with(dest_path, file_content, file_md5, False, False)
    mock_delete_file.assert_called_once_with(source_path, False, False)

@patch('klingon_file_manager.manage.get_file')
@patch('klingon_file_manager.manage.post_file')
@patch('klingon_file_manager.manage.delete_file')
def test_move_file_get_file_fails(mock_delete_file, mock_post_file, mock_get_file):
    # Define the source and destination paths
    source_path = '/path/to/source/file'
    dest_path = '/path/to/destination/file'

    # Set up the mock get_file function to return a failure status
    mock_get_file.return_value = {'status': 500}

    # Call the move_file function
    result = move_file(source_path, dest_path)

    # Assert that the move_file function returned a failure status
    assert result['status'] == 500

    # Assert that the get_file function was called with the correct arguments
    mock_get_file.assert_called_once_with(source_path, False)

@patch('klingon_file_manager.manage.get_file')
@patch('klingon_file_manager.manage.post_file')
@patch('klingon_file_manager.manage.delete_file')
def test_move_file_post_file_fails(mock_delete_file, mock_post_file, mock_get_file):
    # Define the source and destination paths
    source_path = '/path/to/source/file'
    dest_path = '/path/to/destination/file'

    # Define the file content and MD5 hash
    file_content = b'Hello, world!'
    file_md5 = 'fc3ff98e8c6a0d3087d515c0473f8677'

    # Set up the mock get_file function to return the file content and MD5 hash
    mock_get_file.return_value = {'status': 200, 'content': file_content, 'md5': file_md5}

    # Set up the mock post_file function to return a failure status
    mock_post_file.return_value = {'status': 500}

    # Call the move_file function
    result = move_file(source_path, dest_path)

    # Assert that the move_file function returned a failure status
    assert result['status'] == 500

    # Assert that the get_file and post_file functions were called with the correct arguments
    mock_get_file.assert_called_once_with(source_path, False)
    mock_post_file.assert_called_once_with(dest_path, file_content, file_md5, False, False)

@patch('klingon_file_manager.manage.get_file')
@patch('klingon_file_manager.manage.post_file')
@patch('klingon_file_manager.manage.delete_file')
def test_move_file_delete_file_fails(mock_delete_file, mock_post_file, mock_get_file):
    # Define the source and destination paths
    source_path = '/path/to/source/file'
    dest_path = '/path/to/destination/file'

    # Define the file content and MD5 hash
    file_content = b'Hello, world!'
    file_md5 = 'fc3ff98e8c6a0d3087d515c0473f8677'

    # Set up the mock get_file function to return the file content and MD5 hash
    mock_get_file.return_value = {'status': 200, 'content': file_content, 'md5': file_md5}

    # Set up the mock post_file function to return a successful status
    mock_post_file.return_value = {'status': 200}

    # Set up the mock delete_file function to return a failure status
    mock_delete_file.return_value = {'status': 500}

    # Call the move_file function
    result = move_file(source_path, dest_path)

    # Assert that the move_file function returned a failure status
    assert result['status'] == 500

    # Assert that the get_file, post_file, and delete_file functions were called with the correct arguments
    mock_get_file.assert_called_once_with(source_path, False)
    mock_post_file.assert_called_once_with(dest_path, file_content, file_md5, False, False)
    mock_delete_file.assert_called_once_with(source_path, False, False)

@patch('klingon_file_manager.manage.get_file')
@patch('klingon_file_manager.manage.post_file')
@patch('klingon_file_manager.manage.delete_file')
def test_move_file_md5_mismatch(mock_delete_file, mock_post_file, mock_get_file):
    # Define the source and destination paths
    source_path = '/path/to/source/file'
    dest_path = '/path/to/destination/file'

    # Define the file content and different MD5 hashes for source and destination
    file_content = b'Hello, world!'
    source_md5 = 'fc3ff98e8c6a0d3087d515c0473f8677'
    dest_md5 = 'different_md5_hash'

    # Set up the mock get_file function to return the file content and source MD5 hash for the source file
    # and the file content and destination MD5 hash for the destination file
    mock_get_file.side_effect = [
        {'status': 200, 'content': file_content, 'md5': source_md5},
        {'status': 200, 'content': file_content, 'md5': dest_md5}
    ]

    # Set up the mock post_file function to return a successful status
    mock_post_file.return_value = {'status': 200}

    # Call the move_file function
    result = move_file(source_path, dest_path)

    # Assert that the move_file function returned a failure status due to MD5 mismatch
    assert result['status'] == 500
    assert result['message'] == 'MD5 checksum mismatch after moving the file.'

    # Assert that the get_file and post_file functions were called with the correct arguments
    mock_get_file.assert_has_calls([call(source_path, False), call(dest_path, False)])
    mock_post_file.assert_called_once_with(dest_path, file_content, source_md5, False, False)
