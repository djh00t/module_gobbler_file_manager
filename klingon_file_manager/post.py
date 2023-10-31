# post.py
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


import io
import os
import hashlib
from typing import Union, Dict, Optional
import boto3

from .utils import get_aws_credentials, is_binary_file

def write_file(
        path: str,
        content: Union[str, bytes],
        md5: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """Writes content to a file at a given path.

    This function writes content to a file at a specified path. The path can
    either be a local directory or an S3 bucket.

    Args:
        path: The path where the file should be written.
        content: The content to write to the file.
        md5: The MD5 hash of the content, used for data integrity. Defaults to None.
        metadata: Additional metadata to include with the file. Defaults to None.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing the status of the write operation. The schema
        is as follows:
            {
                "status": int,          # HTTP-like status code
                "message": str,         # Message describing the outcome
                "md5": str,             # The MD5 hash of the written file
                "debug": Dict[str, str] # Debug information
            }
    """
    debug_info = {}

    try:
        if path.startswith("s3://"):
            debug_info.update(_write_to_s3(
                path, content, md5, metadata, debug))
        else:
            debug_info.update(_write_to_local(
                path, content, debug))

        return debug_info

    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": f"Failed to write file: {str(exception)}" if debug else "Failed to write file.",
            "debug": debug_info if debug else {},
        }

def _write_to_s3(
        path: str,
        content: Union[str, bytes],
        md5: Optional[str],
        metadata: Optional[Dict[str, str]],
        debug: bool) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """Writes content to an S3 bucket.

    This is a helper function for write_file.

    Args:
        path: The S3 path where the file should be written.
        content: The content to write to the file.
        md5: The MD5 hash of the content, used for data integrity. Defaults to None.
        metadata: Additional metadata to include with the file. Defaults to None.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing the status of the write operation to S3.
    """
    debug_info = {}

    # Your S3 logic here
    # Extract S3 bucket and key from the path
    s3_uri_parts = path[5:].split("/", 1)
    bucket_name = s3_uri_parts[0]
    key = s3_uri_parts[1]

    # Initialize S3 resource and client
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3')

    # Additional Debug Info
    debug_info["s3_uri_parts"] = s3_uri_parts
    debug_info["bucket_name"] = bucket_name
    debug_info["key"] = key

    # Handle MD5 and metadata
    if md5:
        calculated_md5 = hashlib.md5(content).hexdigest()
        if calculated_md5 != md5:
            return {
                "status": 400,
                "message": "Provided MD5 does not match calculated MD5.",
                "debug": debug_info if debug else {},
            }
        if metadata is None:
            metadata = {}
        metadata["ContentMD5"] = calculated_md5

    # Convert all metadata values to strings
    metadata_str = {k: str(v) for k, v in metadata.items()}

    # Create a BytesIO object from the content
    with io.BytesIO(content) as f:
        # Upload the file to S3
        s3_client.upload_fileobj(
            Fileobj=f,
            Bucket=bucket_name,
            Key=key,
            ExtraArgs={'Metadata': metadata_str}
        )

    return {
        "status": 200,
        "message": "File written successfully to S3.",
        "md5": hashlib.md5(content).hexdigest(),
        "debug": debug_info if debug else {},
    }

from typing import Union, Dict


def _write_to_local(
        path: str,
        content: Union[str, bytes],
        debug: bool) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """Writes content to a local directory.

    This is a helper function for write_file.

    Args:
        path: The local path where the file should be written.
        content: The content to write to the file.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing the status of the write operation to the local directory.
    """
    debug_info = {}

    # Write to the local file system
    with open(path, "wb" if isinstance(content, bytes) else "w") as file:
        debug_info['write_start'] = f"Starting write with content={content}"
        file.write(content)

    return {
        "status": 200,
        "message": "File written successfully.",
        "debug": debug_info if debug else {},
    }
