# get.py
"""
# Get Overview

Module for getting files from local and AWS S3 storage.

This module provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules.

# Functions

## get_file
Function for getting files from locally mounted filesystems or S3.

# Usage Examples

To get a file from a local directory:
```python
>>> manage_file('get', '/path/to/local/file')
```

To get a file from an S3 bucket:
```python
>>> manage_file('get', 's3://bucket/file')
```
"""


import os
import boto3
from typing import Union, Dict
from .utils import get_aws_credentials, is_binary_file


def get_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    # Gets a file from a given path.

    This function gets a file from a specified path. The path can either be a
    local directory or an S3 bucket.

    ## Args
    
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | path      | string            | Path the file should be retrieved from |
    | debug     | boolean           | Flag to enable/disable debugging | False |

    ## Returns
    
    A dictionary containing the status of the get operation as follows:
    
    ```python
    {
        "status": int,
        "message": str,
        "content": Union[str, bytes],
        "binary": bool,
        "debug": Dict[str, str]
    }
    ```
    
    | Key       | Type              | Description |
    |-----------|-------------------|-------------|
    | status    | int               | HTTP-like status code |
    | message   | string            | Message describing the outcome |
    | content   | string or bytes   | Content of the file |
    | binary    | boolean           | Flag indicating if the content is binary |
    | debug     | dictionary        | Debug information |
    """
    debug_info = {}

    try:
        if path.startswith("s3://"):
            debug_info.update(_get_from_s3(path, debug))
        else:
            debug_info.update(_get_from_local(path, debug))

        return debug_info

    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": f"Failed to get file: {str(exception)}" if debug else "Failed to get file.",
            "content": None,
            "binary": None,
            "debug": debug_info if debug else {},
        }


def _get_from_s3(path: str, debug: bool) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    # Gets a file from an S3 bucket.

    ## Args

    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | path      | string            | Path where the file should be retrieved from. Must be an S3 URI. |   |
    | debug     | boolean           | Flag to enable/disable debugging | False |

    ## Returns
    A dictionary containing the status of the get operation from S3 as follows:

    ```python
    {
        "status": 200,
        "message": "File read successfully from S3.",
        "content": b'file content in bytes',
        "binary": True,
        "debug": {}
    }
    ```

    | Key       | Type              | Description |
    |-----------|-------------------|-------------|
    | status    | int               | HTTP-like status code |
    | message   | string            | Message describing the outcome |
    | content   | bytes             | Content of the file |
    | binary    | boolean           | Flag indicating if the content is binary |
    | debug     | dictionary        | Debug information |
    
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
            "message": "Failed to get file from S3.",
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



def _get_from_local(path: str, debug: bool) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    @all
    # Gets a file from a local directory.

    ## Args

    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | path      | string            | Path where the file should be retrieved from. Must be a local path. |   |
    | debug     | boolean           | Flag to enable/disable debugging | False |

    ## Returns
    A dictionary containing the status of the get operation from the local
    directory as follows:

    ```python
    {
        "status": 200,
        "message": "File read successfully.",
        "content": b'file content in bytes',
        "binary": True,
        "debug": {}
    }
    ```

    | Key       | Type              | Description |
    |-----------|-------------------|-------------|
    | status    | int               | HTTP-like status code |
    | message   | string            | Message describing the outcome |
    | content   | bytes             | Content of the file |
    | binary    | boolean           | Flag indicating if the content is binary |
    | debug     | dictionary        | Debug information |
    
    """
    debug_info = {}

    try:
        with open(path, "rb") as file:
            content = file.read()
    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": "Failed to get file from local.",
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
