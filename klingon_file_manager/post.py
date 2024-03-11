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
import hashlib
from typing import Union, Dict, Optional
import boto3
import logging
import base64
from .utils import get_md5_hash, get_md5_hash_filename, get_file_size, get_mime_type_content

import os

def post_file(
    path: str,
    content: Union[str, bytes],
    md5: str = None,
    metadata: dict = None,
    debug=False) -> Dict[str, Union[int, str, Dict[str, str]]]:

    # Check if content is a file path
    if isinstance(content, str) and os.path.isfile(content):
        try:
            with open(content, 'rb') as file:
                content = file.read()
        except Exception as e:
            return {
                "status": 400,
                "message": f"Failed to read file at path provided in content: {str(e)}",
                "debug": {} if not debug else {"exception": str(e)}
            }

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

    \\* If md5 is provided, it will be compared against the calculated MD5 hash
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

    print(f"Path: {path}")
    print(f"Content: {content}")
    print(f"MD5: {md5}")
    print(f"Metadata: {metadata}")
    print(f"Debug: {debug}")

    # Default metadata
    # Set md5 if md5 is None
    md5=md5 if md5 is not None else get_md5_hash(content)
    # Calculate the file size and set file_size_var
    file_size=get_file_size(content)
    # Get the content type and set content_type_var
    content_type=get_mime_type_content(content)
    
    default_metadata = {
        "md5": md5,
        "file-size-bytes": file_size,
        "Content-Type": content_type,
    }

    # Build metadata dictionary
    # Step 1: check if metadata is None, if so, set metadata to
    # default_metadata
    # Step 2: if metadata is not None, make sure it is a dictionary. If it
    # isn't a dictionary try to convert it to a dictionary. If it can't be
    # converted to a dictionary, return a 400 error.
    # Step 3: if metadata is a dictionary, merge default_metadata with metadata
    # so all keys and values are retained with the provided metadata taking precedence.
    if metadata is None:
        metadata = default_metadata
    else:
        if isinstance(metadata, dict):
            metadata = {**default_metadata, **metadata}
        else:
            try:
                metadata = {**default_metadata, **dict(metadata)}
            except Exception as exception:
                logging.exception(f"Exception: {str(exception)}")
                return {
                    "status": 400,
                    "message": f"Bad metadata - should be python dictionary: {str(exception)}" if debug else "Bad metadata - should be python dictionary.",
                    "debug": debug_info if debug else {},
                }

    try:
        if path.startswith("s3://"):
            debug_info.update(
                _post_to_s3
                    (
                    path=path,
                    content=content,
                    md5=md5,
                    metadata=metadata,
                    debug=debug,
                )
            )
        else:
            debug_info.update(
                _post_to_local(
                    path=path,
                    content=content,
                    debug=debug,
                )
            )
        
        debug_info["md5"] = get_md5_hash(content)
        return debug_info

    except Exception as exception:
        debug_info["exception"] = str(exception)
        logging.exception(f"Exception: {str(exception)}")
        return {
            "status": 500,
            "message": f"Failed to post file: {str(exception)}" if debug else "Failed to post file.",
            "md5": get_md5_hash(content),
            "debug": debug_info if debug else {},
        }


# Helper function to post to S3
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

    ```python
    {
        "status": 200,
        "message": "File written successfully to S3.",
        "md5": "d41d8cd98f00b204e9800998ecf8427e",
        "debug": {}
    }
    ```
    
    | Key       | Type              | Description |
    |-----------|-------------------|-------------|
    | status    | int               | HTTP-like status code |
    | message   | string            | Message describing the outcome |
    | md5       | string            | MD5 hash of the written file |
    | debug     | dictionary        | Debug information |
    """
    debug_info = {}

    try:
        # Extract S3 bucket and key from the path
        s3_uri_parts = path[5:].split("/", 1)
        bucket_name = s3_uri_parts[0]
        key = s3_uri_parts[1]

        # Initialize S3 resource and client
        s3_client = boto3.client('s3')

        # Check for metadata = None
        if metadata is None:
            metadata = {}

        # Get md5 of content using get_md5_hash
        calculated_md5 = get_md5_hash(content)

        # Check if md5 is provided
        if md5:
            # Check if calculated_md5 matches md5. If not return a 409 error.
            if calculated_md5 != md5:
                return {
                    "status": 409,
                    "message": "Conflict - Provided MD5 does not match calculated MD5.",
                    "debug": debug_info if debug else {},
                }
            
        else:
            # If no md5 is provided, set md5 to calculated_md5
            md5 = calculated_md5

        # Add md5 to object metadata if it isn't already there
        metadata["md5"] = md5

        # Assuming md5 contains the hexadecimal MD5 hash
        hex_md5 = md5

        # Convert the hexadecimal MD5 hash to bytes
        md5_bytes = bytes.fromhex(hex_md5)

        # Encode the bytes in base64 so AWS can use it in ContentMD5
        content_md5 = base64.b64encode(md5_bytes).decode('utf-8')

        # Convert all metadata values to strings
        metadata_str = {k: str(v) for k, v in metadata.items()}

        # Convert strings to bytes
        content_bytes = content if isinstance(content, bytes) else content.encode('utf-8')

        with io.BytesIO(content_bytes) as f:
            f.seek(0)
            # Use put_object method
            result = s3_client.put_object(
                Body=f.read(),
                Bucket=bucket_name,
                Key=key,
                Metadata=metadata_str,
                ContentMD5=content_md5,
                ContentType=metadata.get('Content-Type', 'binary/octet-stream')  # Set the Content-Type
            )

        return {
            "status": 200,
            "message": "File written successfully to S3.",
            "md5": metadata.get("md5", ""),
            "debug": debug_info if debug else {},
        }
        
    except Exception as e:
        # Catch any unhandled exceptions and return an error message
        return {
            "status": 500,
            "message": "An error occurred while posting the file to S3: " + str(e),
            "debug": debug_info if debug else {},
        }


def _post_to_local(
    path: str,
    content: Union[str, bytes],
    debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    # Posts content to a local directory.

    This is a helper function for post_file.

    ## Args
    | Name  | Type      | Description | Default |
    |---|---|---|---|
    | path  | string    | The local path where the file should be written. |   |
    | content  | string or bytes | Content to post |  |
    | debug  | boolean  | Flag to enable/disable debugging | False |

    ## Returns
    A dictionary containing the status of the post operation to the local
    directory as follows:
    
    ```python
    {
        "status": 200,
        "message": "File written successfully.",
        "md5": "d41d8cd98f00b204e9800998ecf8427e",
        "debug": {}
    }
    ```

    | Key       | Type      | Description |
    |---|---|---|
    | status    | int       | HTTP-like status code |
    | message   | string    | Message describing the outcome |
    | md5       | string    | MD5 hash of the written file |
    | debug     | dictionary | Debug information |
    
    """

    debug_info = {}

    try:
        # Post to the local file system
        with open(path, "wb" if isinstance(content, bytes) else "w") as file:
            debug_info['post_start'] = f"Starting post with content={content}"
            result = file.write(content)

            # Get MD5 of written file
            post_local_md5 = get_md5_hash_filename(path)
            
            # If result is greater than or equal to 0, the write is considered successful
            if result >= 0:
                return {
                    "status": 200,
                    "message": "File written successfully.",
                    "md5": post_local_md5,
                    "debug": debug_info if debug else {},
                }
            else:
                return {
                    "status": 500,
                    "message": "Failed to post file.",
                    "md5": post_local_md5,
                    "debug": debug_info if debug else {},
                }
    except OSError as e:
        return {
            "status": 500,
            "message": f"Failed to post file: {e}",
            "md5": post_local_md5,
            "debug": debug_info if debug else {},
        }

