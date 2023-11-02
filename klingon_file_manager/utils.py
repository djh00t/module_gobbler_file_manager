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
    "status": 200,
    "message": "AWS credentials retrieved successfully.",
    "credentials":
        {
            "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
            "AWS_SECRET_ACCESS_KEY": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        },
    "access": {
        "bucket1":
            {
                "ListBucket": True,
                "GetBucketAcl": True,
                "PutObject": True,
                "DeleteObject": True,
            },
        "bucket2":
            {
                "ListBucket": True,
                "GetBucketAcl": True,
                "PutObject": True,
                "DeleteObject": True,
            },
    },
}
```
"""

from boto3 import Session
from dotenv import load_dotenv
from typing import List, Dict, Union, Any, Callable
import hashlib
import boto3
import botocore.exceptions
import magic
import os
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import time
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Load s3 client
s3_client = boto3.client('s3')

def timing_decorator(func: Callable) -> Callable:
    """
    # Decorator for timing the execution of a function
    
    This decorator measures the time taken for the wrapped function to execute
    and prints the duration in seconds.

    ## Arguments

    | Name      | Type              | Description |
    |-----------|-------------------|-------------|
    | func      | Callable          | The function to be decorated. |

    ## Returns
    The decorated function.

    ## Example
    ```python
    >>> @timing_decorator
    ... def example_function():
    ...     print("Executing function...")
    ...
    >>> example_function()
    Executing function...
    example_function took 0.0001 seconds to run.
    ```
    """
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time} seconds to run.")
        return result
    return wrapper

@timing_decorator
def get_mime_type(file_path: str) -> dict:
    """
    # Get the MIME type of a file

    ## Args
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | file_path | string            | Path to the file |   |

    ## Returns
    A dictionary containing the status code, message, MIME type, and any debug information.
    
    """
    try:
        if file_path.startswith('s3://'):
            bucket_name, key = file_path[5:].split('/', 1)
            obj = s3_client.get_object(Bucket=bucket_name, Key=key)
            return {
                'status': 200,
                'message': 'Success',
                'mime_type': obj['ContentType'],
                'debug': None
            }
        else:
            with open(file_path, 'rb') as file:
                content = file.read(1024)
            return {
                'status': 200,
                'message': 'Success',
                'mime_type': magic.from_buffer(content, mime=True),
                'debug': None
            }

    except s3_client.exceptions.NoSuchKey:
        return {
            'status': 404,
            'message': 'Not Found - The file you have requested does not exist',
            'mime_type': None,
            'debug': {'file_path': file_path, 'bucket_name': bucket_name, 'key': key}
        }

    except Exception as e:
        return {
            'status': 500,
            'message': 'Internal Server Error',
            'mime_type': None,
            'debug': {'error': str(e), 'file_path': file_path}
        }

@timing_decorator
@lru_cache(maxsize=128)
def parallel_check_bucket_permissions(bucket_names: List[str], s3: Any) -> Dict[str, Any]:
    """
    # Check permissions of multiple S3 buckets in parallel

    This function uses a thread pool to concurrently execute the `check_bucket_permissions` 
    function on multiple bucket names. The results are then aggregated into a dictionary.

    ## Args

    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | bucket_names | List[str]      | A list of S3 bucket names to check. |   |
    | s3        | boto3.client      | S3 client object |   |

    ## Returns
    A dictionary where the keys are the bucket names and the values are the permissions for each bucket.

    ## Usage Example
    ```python
    >>> parallel_check_bucket_permissions(['bucket1', 'bucket2'], s3_client)
    {'bucket1': 'READ_WRITE', 'bucket2': 'READ_ONLY'}
    ```
    **Note:**
    The `check_bucket_permissions` function should be defined to take a bucket name
    and an S3 client object, and return the permissions for the bucket.
    """
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda bucket_name: (bucket_name, check_bucket_permissions(bucket_name, s3)), bucket_names))
    
    return {bucket_name: permissions for bucket_name, permissions in results}

@timing_decorator
@lru_cache(maxsize=128)
def check_bucket_permissions(bucket_name, s3):
    """
    # Check permissions of an S3 bucket

    Returns a dictionary containing ListBucket, GetBucketAcl, PutObject, and
    DeleteObject permissions for the given bucket.

    ## Args
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | bucket_name | string          | The name of the bucket to check permissions for. |   |
    | s3        | boto3.client      | S3 client |   |

    ## Returns
    Python dictionary containing the permissions as follows:
    ```python
    {
        'ListBucket': True,
        'GetBucketAcl': False,
        'PutObject': False,
        'DeleteObject': False,
    }    
    ```

    | Key       | Type              | Description |
    |-----------|-------------------|-------------|
    | ListBucket | boolean          | True if the user has ListBucket permission, False otherwise |
    | GetBucketAcl | boolean        | True if the user has GetBucketAcl permission, False otherwise |
    | PutObject | boolean           | True if the user has PutObject permission, False otherwise |
    | DeleteObject | boolean        | True if the user has DeleteObject permission, False otherwise |
        
    """
    permissions = {
        'ListBucket': False,
        'GetBucketAcl': False,
        'PutObject': False,
        'DeleteObject': False,
    }

    try:
        s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=0)
        permissions['ListBucket'] = True
    except s3_client.exceptions.NoSuchBucket:
        return permissions

    try:
        s3_client.get_bucket_acl(Bucket=bucket_name)
        permissions['GetBucketAcl'] = True
    except s3_client.exceptions.NoSuchBucket:
        return permissions

    try:
        object_key = 'temp_permission_check_object'
        s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=b'')
        permissions['PutObject'] = True
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        permissions['DeleteObject'] = True
    except s3_client.exceptions.NoSuchBucket:
        return permissions

    return permissions

@timing_decorator
@lru_cache(maxsize=128)
def get_aws_credentials(debug: bool = False) -> Dict[str, Union[int, str]]:
    """
    # Get AWS credentials and check access to S3 buckets
    
    Fetches AWS credentials from .env file or environment variables. If the
    function finds them, it checks if they are valid and returns them along
    with a list of buckets and the permissions the credentials have to each.

    ## Args
    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | debug     | bool              | Flag to enable debugging. | False |

    ## Returns
    A dictionary containing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY as well
    as a list of buckets the credentials have read and write access to as follows:

    ```python
    {
        'status': 200,
        'message': 'AWS credentials retrieved successfully.',
        'credentials': {
            'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
            'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        },
        'access': {
                'bucket1': {
                    'ListBucket': true,
                    'GetBucketAcl': true,
                    'PutObject': true,
                    'DeleteObject': true
                },
                'bucket2': {
                    'ListBucket': true,
                    'GetBucketAcl': true,
                    'PutObject': true,
                    'DeleteObject': true
                }
        },
    }
    ```
    """
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    # Make sure there are AWS variables in the dotenv or environment
    if not access_key or not secret_key:
        return {
            'status': 424,
            'message': 'Failed Dependency - No working AWS credentials in .env or environment',
        }

    session = Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    
    try:
        user = session.client('iam').get_user()
    except Exception as e:
        return {
            'status': 403,
            'message': 'Access Denied - AWS credentials are invalid',
        }

    s3 = session.client('s3')
    response = s3_client.list_buckets()
    buckets = response['Buckets']

    bucket_names = [bucket['Name'] for bucket in buckets]
    access = parallel_check_bucket_permissions(tuple(bucket_names), s3)


    return {
        'status': 200,
        'message': 'AWS credentials retrieved successfully.',
        'credentials': {
            'AWS_ACCESS_KEY_ID': access_key,
            'AWS_SECRET_ACCESS_KEY': secret_key,
        },
        'access': access
    }

@timing_decorator
def is_binary_file(file_path_or_content: Union[str, bytes]) -> bool:
    """
    # Check if a file or content is binary

    ## Args
    | Name      | Type              | Description |
    |-----------|-------------------|-------------|
    | file_path_or_content | string or bytes | The path to the file or the content of the file. |

    ## Returns
    A boolean value of true if the file or content is binary, False otherwise.
    """
    if isinstance(file_path_or_content, str):
        if file_path_or_content.startswith('s3://'):
            bucket_name, key = file_path_or_content[5:].split('/', 1)
            obj = s3_client.get_object(Bucket=bucket_name, Key=key)
            return obj['ContentType'].startswith('application/')
        else:
            with open(file_path_or_content, 'rb') as file:
                content = file.read(1024)
            mime_type = magic.from_buffer(content, mime=True)
            return mime_type.startswith('application/')
    elif isinstance(file_path_or_content, bytes):
        mime_type = magic.from_buffer(file_path_or_content, mime=True)
        return mime_type.startswith('application/')
    else:
        raise TypeError("file_path_or_content must be either str or bytes.")

def get_s3_metadata(s3_url):
    """
    # Fetch metadata of an S3 object.
    
    ## Parameters
    
    | Name      | Type              | Description |
    |-----------|-------------------|-------------|
    | s3_url    | string            | The S3 URL of the object |
    
    ## Returns
    A dictionary containing the metadata key-value pairs. The schema is as follows:
    ```python
    {
        'MetadataKey1': 'MetadataValue1',
        'MetadataKey2': 'MetadataValue2',
        ...
    }
    ```

    In case of an error:

    ```python
    {
        'Error': 'Error message'
    }
    ```
    
    ## Usage example

    ```python
    if __name__ == "__main__":
        s3_url = "s3://your-bucket-name/your-object-key"
        result = get_s3_metadata(s3_url)
        print("Metadata:", result)
    ```
    """
    # Parse the S3 URL
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc
    key = parsed_url.path.lstrip('/')
    
    # Fetch the object metadata
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=key)
        print(response)
    except Exception as e:
        print(f"Error: {e}")
        return {'Error': str(e)}
    
    # Return the entire response
    return response

# Function to get MD5 hash of the content
def get_md5_hash(content: Union[str, bytes]) -> str:
    """
    # Calculates the MD5 hash of the given content.
    """
    if isinstance(content, str):
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(content).hexdigest()

# Function to get file size
def get_file_size(content: Union[str, bytes]) -> int:
    """
    # Calculates the size of the given content.
    """
    if isinstance(content, str):
        return len(content.encode('utf-8'))
    else:
        return len(content)


def get_mime_type_content(content: Union[str, bytes]) -> str:
    """
    Determines the MIME type of the given content using the magic library.

    Args:
        content (Union[str, bytes]): The content for which to determine the MIME type.

    Returns:
        str: The MIME type of the content.
    """
    # Initialize magic
    magic_mime = magic.Magic(mime=True)

    # If content is a string, convert to bytes
    if isinstance(content, str):
        content = content.encode('utf-8')

    # Get MIME type
    mime_type = magic_mime.from_buffer(content)

    return mime_type