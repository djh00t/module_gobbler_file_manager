# utils.py
"""
Utility functions for the Klingon File Manager, including AWS credential fetching.

This module provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules.

Functions:
    get_mime_type: Fetch the MIME type of a file.
    is_binary_file: Check if a file is binary.
    get_aws_credentials: Fetch AWS credentials.

Example:
    # To get the MIME type of a local file:
    >>> get_mime_type('/path/to/local/file.txt')
    'text/plain'
    
    # To get the MIME type of an S3 file:
    >>> get_mime_type('s3://bucket/file.jpg')
    'image/jpeg'
    
    # To check if a local file is binary:
    >>> is_binary_file('/path/to/local/file.bin')
    True
    
    # To check if an S3 file is binary:
    >>> is_binary_file('s3://bucket/file.bin')
    True
    
    # To fetch AWS credentials:
    >>> credentials = get_aws_credentials()
    >>> print(credentials['aws_access_key_id'])
    'YOUR_AWS_ACCESS_KEY_ID'
"""

import magic
from boto3 import Session
from typing import Dict, Union


def get_mime_type(file_path: str) -> str:
    """Gets the MIME type of a file.

    Args:
        file_path: The path to the file.

    Returns:
        The MIME type of the file.
    """
    if file_path.startswith('s3://'):
        s3 = boto3.client('s3')
        bucket_name, key = file_path[5:].split('/', 1)
        obj = s3.get_object(Bucket=bucket_name, Key=key)
        return obj['ContentType']
    else:
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

def is_binary_file(file_path_or_content: Union[str, bytes]) -> bool:
    """Check if a file or content is binary.

    Args:
        file_path_or_content: The path to the file or the content of the file.

    Returns:
        True if the file or content is binary, False otherwise.
    """
    if isinstance(file_path_or_content, str):
        if file_path_or_content.startswith('s3://'):
            s3 = boto3.client('s3')
            bucket_name, key = file_path_or_content[5:].split('/', 1)
            obj = s3.get_object(Bucket=bucket_name, Key=key)
            return obj['ContentType'].startswith('application/')
        else:
            with open(file_path_or_content, 'rb') as file:
                content = file.read()
            mime_type = magic.from_buffer(content, mime=True)
            return mime_type.startswith('application/')
    elif isinstance(file_path_or_content, bytes):
        mime_type = magic.from_buffer(file_path_or_content, mime=True)
        return mime_type.startswith('application/')
    else:
        raise TypeError("file_path_or_content must be either str or bytes.")
