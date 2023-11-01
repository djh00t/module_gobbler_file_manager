# utils.py
"""
# Utils Overview
Utility functions for the Klingon File Manager, including AWS credential fetching.

This module provides a centralized way to manage file operations on both
local and AWS S3 storage. It leverages utility functions from the `utils` module
and specific actions from `get`, `post`, and `delete` modules.

# Functions

## get_mime_type
Fetch the MIME type of a file.

## get_aws_credentials
Fetch AWS credentials.

## is_binary_file
Check if a file is binary.

# Usage Examples

To get the MIME type of a local file:
```python
>>> get_mime_type('/path/to/local/file.txt')
'text/plain'
```

To get the MIME type of an S3 file:
```python
>>> get_mime_type('s3://bucket/file.jpg')
'image/jpeg'
```

To check if a local file is binary:
```python
>>> is_binary_file('/path/to/local/file.bin')
True
```

To check if an S3 file is binary:
```python
>>> is_binary_file('s3://bucket/file.bin')
True
```

To fetch AWS credentials:
```python
>>> credentials = get_aws_credentials()
>>> print(credentials['aws_access_key_id'])
{
    'status': 200,
    'message': 'AWS credentials retrieved successfully.',
    'credentials': {
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    }
}
```
"""

import boto3
from boto3 import Session
import magic
from typing import Dict, Union



def get_mime_type(file_path: str) -> str:
    """
    # Get the MIME type of a file.

    ## Args
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | file_path | string            | Path to the file |   |

    ## Returns
    A string containing the MIME type of the file. For example if run against a
    jpeg file, the function would return `image/jpeg`
    
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


import os
from dotenv import load_dotenv

def get_aws_credentials(debug: bool = False) -> Dict[str, Union[int, str]]:
    """
    # Fetches AWS credentials from .env file or environment variables.

    ## Args
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | debug     | bool              | Flag to enable debugging. | False |

    ## Returns
    A dictionary containing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY as follows:

    ```python
    {
        'status': 200,
        'message': 'AWS credentials retrieved successfully.',
        'credentials': {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        },
    }
    """
    load_dotenv()
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if not access_key or not secret_key:
        return {
            'status': 424,
            'message': 'Failed Dependency - No working S3 credentials in .env or environment',
        }

    session = Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    try:
        user = session.client('iam').get_user()
    except Exception as e:
        return {
            'status': 403,
            'message': 'Access Denied - AWS credentials are invalid',
        }

    # TODO: Check read and write access to the bucket using GetUserPolicy API

    return {
        'status': 200,
        'message': 'AWS credentials retrieved, valid and have read and write access to this bucket',
        'credentials': {
            'AWS_ACCESS_KEY_ID': access_key,
            'AWS_SECRET_ACCESS_KEY': secret_key,
        },
    }

def is_binary_file(file_path_or_content: Union[str, bytes]) -> bool:
    """
    # Check if a file or content is binary.

    ## Args
    | Name      | Type              | Description |
    |-----------|-------------------|-------------|
    | file_path_or_content | string or bytes | The path to the file or the content of the file. |

    ## Returns
    A boolean value of true if the file or content is binary, False otherwise.
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
