# get.py
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

import os
import boto3
from typing import Union, Dict
from .utils import get_aws_credentials, is_binary_file


def read_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """Reads a file from a given path.

    This function reads a file from a specified path. The path can either be a
    local directory or an S3 bucket.

    Args:
        path: The path of the file to read.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing the status of the read operation. The schema
        is as follows:
            {
                "status": int,          # HTTP-like status code
                "message": str,         # Message describing the outcome
                "content": Union[str, bytes],  # The actual file content
                "binary": bool,         # Flag indicating if the content is binary
                "debug": Dict[str, str] # Debug information
            }
    """
    debug_info = {}

    try:
        if path.startswith("s3://"):
            debug_info.update(_read_from_s3(path, debug))
        else:
            debug_info.update(_read_from_local(path, debug))

        return debug_info

    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": f"Failed to read file: {str(exception)}" if debug else "Failed to read file.",
            "content": None,
            "binary": None,
            "debug": debug_info if debug else {},
        }


def _read_from_s3(path: str, debug: bool) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """Reads a file from an S3 bucket.

    Args:
        path: The S3 path where the file should be read from.
        debug: Flag to enable debugging.

    Returns:
        A dictionary containing the status of the read operation from S3.
    """
    debug_info = {}

    s3_uri_parts = path[5:].split("/", 1)
    bucket_name = s3_uri_parts[0]
    key = s3_uri_parts[1]
    
    debug_info["s3_uri_parts"] = s3_uri_parts
    debug_info["bucket_name"] = bucket_name
    debug_info["key"] = key

    s3 = resource('s3')
    s3_object = s3.Object(bucket_name, key)
    
    try:
        content = s3_object.get()['Body'].read()
    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": "Failed to read file from S3.",
            "content": None,
            "binary": None,
            "debug": debug_info if debug else {},
        }
    
    return {
        "status": 200,
        "message": "File read successfully from S3.",
        "content": content,
        "binary": True,
        "debug": debug_info if debug else {},
    }



def _read_from_local(path: str, debug: bool) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """Reads a file from a local directory.

    Args:
        path: The local path where the file should be read from.
        debug: Flag to enable debugging.

    Returns:
        A dictionary containing the status of the read operation from the local directory.
    """
    debug_info = {}

    try:
        with open(path, "rb") as file:
            content = file.read()
    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": "Failed to read file from local.",
            "content": None,
            "binary": None,
            "debug": debug_info if debug else {},
        }
        
    is_binary = is_binary_file(content)

    return {
        "status": 200,
        "message": "File read successfully.",
        "content": content,
        "binary": is_binary,
        "debug": debug_info if debug else {},
    }
