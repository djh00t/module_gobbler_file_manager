# delete.py
"""
# Delete Overview

Delete files from local and AWS S3 storage.

This module provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules.

# Functions

## delete_file
Function for deleting files on locally mounted or S3 storage.

# Usage Examples
To delete a file from a local directory:
```python
>>> manage_file('delete', '/path/to/local/file')
```

To delete a file from an S3 bucket:
```python
>>> manage_file('delete', 's3://bucket/file')
```
"""


from typing import Union, Dict
import os
import boto3
from .utils import get_aws_credentials

def delete_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    # Delete a file from either a locally mounted or S3 storage.
    
    ## Args

    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | path      | string            | Path where the file should be deleted. Can be a local path or an S3 URI. |   |
    | debug     | boolean           | Flag to enable/disable debugging | False |

    ## Returns
    A dictionary containing the status of the delete operation as follows:
    ```python
    {
        "status": 200,
        "message": "File deleted successfully.",
        "debug": {}
    }
    ```
    
    | Key       | Type              | Description |
    |-----------|-------------------|-------------|
    | status    | int               | HTTP-like status code |
    | message   | string            | Message describing the outcome |
    | debug     | dictionary        | Debug information |
    
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

