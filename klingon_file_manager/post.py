# post.py
"""
# Post Overview

Post files to locally mounted and S3 storage.

This submodule provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules.

# Functions

## post_file
Function for writing files into locally mounted filesystems or S3.

# Usage Examples
To post a file to a local directory:

```python
>>> manage_file('post', '/path/to/local/file', 'Hello, world!')
```

To post a file to an S3 bucket:
```python
>>> manage_file('post', 's3://bucket/file', 'Hello, world!')
```
"""

import io
import os
import hashlib
from typing import Union, Dict, Optional
import boto3

from .utils import get_aws_credentials, is_binary_file

def post_file(
        path: str,
        content: Union[str, bytes],
        md5: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    # Post content to a file at a given path.

    This function posts content to a file at a specified path. The path can
    either be a local directory or an S3 bucket.

    ## Args
    
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | path      | string            | Path where the file should be written |   |
    | content   | string or bytes   | Content to post |  |
    | md5       | string            | MD5 hash of the file, used for data integrity | * See note |
    | metadata  | dictionary        | Additional metadata to include with the file | ^ See note |
    | debug     | boolean           | Flag to enable/disable debugging | False |

    **Note:**

    \* If md5 is provided, it will be compared against the calculated MD5 hash
        of the content. If they do not match, the post will fail. If md5 hash
        is not provided, it will be calculated, returned in the response and
        will also be used to validate that the file arrived in tact by S3

    ^ Default metadata includes the following, if you add your own metadata, it
        will be merged with the default metadata:
    ```python
    {
        "md5": str,
        "filesize": int
    }
    ```

    ## Returns
    
    A dictionary containing the status of the post operation. The schema
    is as follows:
    ```python
    {
        "status": int,
        "message": str,
        "md5": str,
        "debug": Dict[str, str]
    }
    ```
    | Key      | Type              | Description |
    |-----------|-------------------|-------------|
    | status    | int               | HTTP-like status code |
    | message   | string            | Message describing the outcome |
    | md5       | string            | MD5 hash of the written file |
    | debug     | dictionary        | Debug information |
    """
    debug_info = {}

    try:
        if path.startswith("s3://"):
            debug_info.update(_post_to_s3(
                path, content, md5, metadata, debug))
        else:
            debug_info.update(_post_to_local(
                path, content, debug))

        return debug_info

    except Exception as exception:
        debug_info["exception"] = str(exception)
        return {
            "status": 500,
            "message": f"Failed to post file: {str(exception)}" if debug else "Failed to post file.",
            "debug": debug_info if debug else {},
        }

def _post_to_s3(
        path: str,
        content: Union[str, bytes],
        md5: Optional[str],
        metadata: Optional[Dict[str, str]],
        debug: bool) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    # Posts content to an S3 bucket.

    This is a helper function for post_file.

    ## Args

    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | path      | string            | The S3 path where the file should be written. Must be an S3 URI. |   |
    | content   | string or bytes   | Content to post |  |
    | md5       | string            | MD5 hash of the file, used for data integrity | * See note |
    | metadata  | dictionary        | Additional metadata to include with the file | ^ See note |
    | debug     | boolean           | Flag to enable/disable debugging | False |

    ## Returns
    A dictionary containing the status of the post operation to S3 as follows:
    
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


def _post_to_local(
        path: str,
        content: Union[str, bytes],
        debug: bool) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """Posts content to a local directory.

    This is a helper function for post_file.

    Args:
        path: The local path where the file should be written.
        content: The content to post.
        debug: Flag to enable debugging. Defaults to False.

    Returns:
        A dictionary containing the status of the post operation to the local directory.
    """
    debug_info = {}

    # Post to the local file system
    with open(path, "wb" if isinstance(content, bytes) else "w") as file:
        debug_info['post_start'] = f"Starting post with content={content}"
        file.write(content)

    return {
        "status": 200,
        "message": "File written successfully.",
        "debug": debug_info if debug else {},
    }
