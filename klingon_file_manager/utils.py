# utils.py
"""File Management Service for Local and AWS S3 Storage.

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
    To read a file from a local directory:
    >>> manage_file('get', '/path/to/local/file')

    To write a file to an S3 bucket:
    >>> manage_file('post', 's3://bucket/file', 'Hello, world!')

    To delete a file from a local directory:
    >>> manage_file('delete', '/path/to/local/file')
"""

import magic
from boto3 import Session
from typing import Dict, Union, bool, str


def get_mime_type(file_path: str) -> str:
    """Gets the MIME type of a file.

    Args:
        file_path: The path to the file.

    Returns:
        The MIME type of the file.
    """
    with open(file_path, 'rb') as file:
        content = file.read()
    return magic.from_buffer(content, mime=True)


def get_aws_credentials(debug: bool = False) -> Dict[str, Union[int, str]]:
    """Fetches AWS credentials from environment variables or provided arguments.

    Args:
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
    """
    session = Session()
    credentials = session.get_credentials()
    return {
        'status': 200,
        'message': 'AWS credentials retrieved successfully.',
        'credentials': {
            'AWS_ACCESS_KEY_ID': credentials.access_key,
            'AWS_SECRET_ACCESS_KEY': credentials.secret_key,
        },
    }

def is_binary_file(content: bytes, debug: bool = False) -> bool:
    """Checks if content is binary or text.

    Args:
        content: The content to check.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        True if the content is binary, False otherwise.
    """
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    is_binary_str = lambda data: bool(data.translate(None, text_chars))
    return is_binary_str(content)
