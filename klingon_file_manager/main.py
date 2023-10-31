# main.py
"""
File Management Service for Local and AWS S3 Storage.

This module provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules. It provides an
interface for reading, writing, and deleting files, with additional support for
debugging and AWS authentication.

Modules:
    utils: Provides utility functions like AWS credential fetching and file type checking.
    get: Contains the functionality for reading files.
    post: Contains the functionality for writing files.
    delete: Contains the functionality for deleting files.

Functions:
    manage_file: The main function that delegates to specific actions based on user input.

Example:
    # To get a file from a local directory:
    >>> manage_file('get', '/path/to/local/file')
    
    # To get a file from an S3 bucket:
    >>> manage_file('get', 's3://bucket/file')
    
    # To post a file to a local directory:
    >>> manage_file('post', '/path/to/local/file', 'Hello, world!')
    
    # To post a file to an S3 bucket:
    >>> manage_file('post', 's3://bucket/file', 'Hello, world!')
    
    # To delete a file from a local directory:
    >>> manage_file('delete', '/path/to/local/file')
    
    # To delete a file from an S3 bucket:
    >>> manage_file('delete', 's3://bucket/file')

"""

from typing import Union, Dict, Optional, Callable
from .utils import is_binary_file, get_aws_credentials
from .delete import delete_file
from .post import post_file
from .get import get_file

# Use the get_aws_credentials function to get AWS credentials returned as a
# json object containing the following keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
aws_credentials = get_aws_credentials()


def manage_file(
    action: str,
    path: str,
    content: str = None,
    md5: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    debug: bool = True,
) -> dict:
    print("manage_file function called")  # Debug print statement

    debug_info = {}
    result = {
        'action': action,
        'path': path,
        'content': "<binary data>" if isinstance(content, bytes) and action != 'get' else (content[:10] if isinstance(content, str) else content[:10].decode('utf-8')) if content and debug else content,
        'content_size': len(content),
        'binary': is_binary_file(content),
        'md5': md5,
        'metadata': metadata,
        'debug': debug_info if debug else {},
    }

    try:
        print("Inside try block")  # Debug print statement
        if action == 'get':
            print("Action is get")  # Debug print statement
            get_result = get_file(path, debug)
            result['status'] = get_result['status']
            result['content'] = get_result['content']
            result['binary'] = is_binary_file(result['content'], debug)
            # Add the debug info for the get_file() function
            if debug or result['status'] == 500:
                debug_info['get_file'] = get_result['debug']
        elif action == 'post':
            print("Action is post")  # Debug print statement
            result['binary'] = is_binary_file(content, debug)
            debug_info['post_file_start'] = f"Starting post_file with path={path}, content={content[:10]}, md5={md5}, metadata={metadata}"
            post_result = post_file(path, content, md5, metadata, debug)
            result['status'] = post_result['status']
            # Add the debug info for the post_file() function
            if debug or result['status'] == 500:
                debug_info['post_file'] = post_result['debug']
            return result
        elif action == 'delete':
            print("Action is delete")  # Debug print statement
            delete_result = delete_file(path, debug)
            result['status'] = delete_result['status']
            # Add the debug info for the delete_file() function
            if debug or result['status'] == 500:
                debug_info['delete_file'] = delete_result['debug']
        else:
            print("Invalid action")  # Debug print statement
            result['status'] = 500
            debug_info['error'] = 'Invalid action'
    except Exception as exception:
        print(f"Exception occurred: {str(exception)}")  # Debug print statement
        result['status'] = 500
        result['error_message'] = str(exception)
        # Add the debug info for the exception
        debug_info['exception'] = str(exception) if debug else None
        debug_info['error_message'] = str(exception) if debug else None
    # If the debug flag is not set and there was no failure, remove the debug field
    # No need to delete the 'debug' key as it will be empty if debug is False
    if not debug and result['status'] != 500:
        del result['debug']
