# __init__.py
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

from .main import manage_file
from .delete import delete_file
from .get import read_file
from .post import write_file
from .utils import get_mime_type, get_aws_credentials, is_binary_file