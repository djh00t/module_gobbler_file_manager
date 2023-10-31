# delete.py
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

from typing import Union, Dict
import os
import boto3
from .utils import get_aws_credentials

def delete_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """Deletes a file from either a local file system or an S3 object.
    
    Args:
        path: The path where the file should be deleted. Can be a local path or an S3 URI.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing the status of the delete operation.
    """
    debug_info = {}

    try:
        if path.startswith("s3://"):
            aws_credentials = get_aws_credentials()
            if aws_credentials["status"] != 200:
                return {
                    "status": 403,
                    "message": "AWS credentials not found",
                    "debug": debug_info if debug else {},
                }

            s3_uri_parts = path[5:].split("/", 1)
            bucket_name, key = s3_uri_parts

            if debug:
                debug_info.update({
                    "s3_uri_parts": s3_uri_parts,
                    "bucket_name": bucket_name,
                    "key": key
                })

            s3_client = boto3.client("s3")

            try:
                s3_client.delete_object(Bucket=bucket_name, Key=key)
                return {
                    "status": 200,
                    "message": "File deleted successfully from S3.",
                    "debug": debug_info if debug else {},
                }
            except Exception as e:
                if debug:
                    debug_info["exception"] = str(e)
                return {
                    "status": 500,
                    "message": "Failed to delete file from S3.",
                    "debug": debug_info if debug else {},
                }

        else:
            try:
                os.remove(path)
                return {
                    "status": 200,
                    "message": "File deleted successfully.",
                    "debug": debug_info if debug else {},
                }
            except Exception as e:
                if debug:
                    debug_info["exception"] = str(e)
                return {
                    "status": 500,
                    "message": "Failed to delete file.",
                    "debug": debug_info if debug else {},
                }

    except Exception as e:
        if debug:
            debug_info["exception"] = str(e)
        return {
            "status": 500,
            "message": "Failed to delete file.",
            "debug": debug_info if debug else {},
        }
