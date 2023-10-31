# __init__.py
"""
klingon_file_manager
--------------------

A File Management Service for Local and AWS S3 Storage.

This library provides a set of functions to manage files both locally and on AWS S3. 

Functions:
- manage_file: Main function to manage files. It can handle operations like upload, download, delete, etc.
- delete_file: Function to delete a file from local storage or AWS S3.
- get_file: Function to get a file from local storage or AWS S3.
- post_file: Function to post a file to local storage or AWS S3.
- get_mime_type: Utility function to get the MIME type of a file.
- get_aws_credentials: Utility function to get AWS credentials from environment variables.
- is_binary_file: Utility function to check if a file is binary.

"""

from .main import manage_file
from .delete import delete_file
from .get import get_file
from .post import post_file
from .utils import get_mime_type, get_aws_credentials, is_binary_file
