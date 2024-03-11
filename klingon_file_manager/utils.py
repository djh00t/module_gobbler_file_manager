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
import re
from boto3 import Session
from dotenv import load_dotenv
from typing import List, Dict, Union, Any, Callable
import hashlib
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import magic
import os
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import time
import logging
from urllib.parse import urlparse

# Logging configuration
logging.basicConfig(level=logging.INFO)

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
    >>> #@timing_decorator
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

#@timing_decorator
def get_mime_type(file_path: str) -> dict:
    """
    Get the MIME type of a file

    Args:
    | Name      | Type     | Description           | Default |
    |-----------|----------|-----------------------|---------|
    | file_path | string   | Path to the file       |         |

    Returns:
    A dictionary containing the status code, message, MIME type, and any debug information.
    
    """
    # Check if the file_path is empty
    if not file_path:
        return {
            'status': 500,
            'message': 'Internal Server Error',
            'mime_type': None,
            'debug': {'error': 'Empty file_path', 'file_path': file_path}
        }
    # Check if it's an S3 URL
    if file_path.startswith('s3://'):
        try:
            bucket_name, key = file_path[5:].split('/', 1)
            obj = s3_client.get_object(Bucket=bucket_name, Key=key)
            return {
                'status': 200,
                'message': 'Success',
                'mime_type': obj['ContentType'],
                'debug': None
            }
        except:  # Catch the specific exceptions related to S3 here.
            return {
                'status': 404,
                'message': 'Not Found - The S3 file you have requested does not exist',
                'mime_type': None,
                'debug': {'file_path': file_path, 'bucket_name': bucket_name, 'key': key}
            }
    
    # Check if it's a local file
    if os.path.exists(file_path):
        try:
            with open(file_path, 'rb') as file:
                content = file.read(1024)
            mime_type = magic.from_buffer(content, mime=True)
            return {
                'status': 200,
                'message': 'Success',
                'mime_type': mime_type,
                'debug': None
            }
        except Exception as e:
            return {
                'status': 500,
                'message': 'Internal Server Error',
                'mime_type': None,
                'debug': {'error': str(e), 'file_path': file_path}
            }
    else:
        return {
            'status': 404,
            'message': 'Not Found - The file you have requested does not exist',
            'mime_type': None,
            'debug': {'file_path': file_path}
        }

#@timing_decorator
#@lru_cache(maxsize=128)
def parallel_check_bucket_permissions(bucket_names: List[str], s3_client: Any) -> Dict[str, Any]:
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
        results = list(executor.map(lambda bucket_name: (bucket_name, check_bucket_permissions(bucket_name, s3_client)), bucket_names))
    
    return {bucket_name: permissions for bucket_name, permissions in results}

#@timing_decorator
#@lru_cache(maxsize=128)
def check_bucket_permissions(bucket_name, s3_client):
    print(f"Checking permissions for bucket: {bucket_name}")
    print(f"Checking permissions for s3_client: {s3_client}")
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
    
    # Set the default permissions to False
    permissions = {
        'ListBucket': False,
        'GetBucketAcl': False,
        'PutObject': False,
        'DeleteObject': False
    }

    # Set default bucket_exists to True
    bucket_exists = True

    # Copy permissions variable into bucket_not_exists_permissions
    bucket_not_exists_permissions = permissions.copy()

    # Check ListBucket permission
    if bucket_exists:
        try:
            s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
            permissions['ListBucket'] = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                permissions = bucket_not_exists_permissions
                print(f"No such bucket: {bucket_name}")
                bucket_exists = False
            else:
                permissions['ListBucket'] = False
                print(f"Error checking ListBucket permission: {e}")

    # Check GetBucketAcl permission
    if bucket_exists:
        try:
            s3_client.get_bucket_acl(Bucket=bucket_name)
            permissions['GetBucketAcl'] = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                permissions = bucket_not_exists_permissions
                print(f"No such bucket: {bucket_name}")
                bucket_exists = False
            else:
                permissions['GetBucketAcl'] = False
                print(f"Error checking GetBucketAcl permission: {e}")

    # Check PutObject permission
    if bucket_exists:
        try:
            s3_client.put_object(Bucket=bucket_name, Key='test_permission_object', Body=b'test')
            permissions['PutObject'] = True
            # Clean up by deleting the test object
            s3_client.delete_object(Bucket=bucket_name, Key='test_permission_object')
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                permissions = bucket_not_exists_permissions
                print(f"No such bucket: {bucket_name}")
                bucket_exists = False
            else:
                permissions['PutObject'] = False
                print(f"Error checking PutObject permission: {e}")

    # Check DeleteObject permission
    if bucket_exists:
        try:
            s3_client.delete_object(Bucket=bucket_name, Key='non_existent_object_for_permission_check')
            permissions['DeleteObject'] = True
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                permissions = bucket_not_exists_permissions
                print(f"No such bucket: {bucket_name}")
                bucket_exists = False
            elif e.response['Error']['Code'] != 'NoSuchKey':
                permissions['DeleteObject'] = False
                print(f"Error checking DeleteObject permission: {e}")
            else:
                permissions['DeleteObject'] = False
                print(f"Error checking DeleteObject permission: {e}")

    return permissions

#@timing_decorator
def get_aws_credentials(debug: bool = False, access_key: str = None, secret_key: str = None) -> Dict[str, Union[int, str]]:
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

    # Get AWS credentials from arguments or environment variables
    print("Access Key from arguments:", access_key)
    print("Secret Key from arguments:", secret_key)
    access_key = access_key or os.getenv('AWS_ACCESS_KEY_ID')
    print("Access Key after fetching from os.getenv:", access_key)
    secret_key = secret_key or os.getenv('AWS_SECRET_ACCESS_KEY')
    print("Secret Key after fetching from os.getenv:", secret_key)
    # Insert the print statement here
    print(f"Access Key in Function: {access_key}")
    print(f"Secret Key in function: {secret_key}")

    # If either of the AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY credentials
    # is unset, set to None or spaces/tabs or otherwise unprintable characters,
    # return a 424 status code with the message 'Failed Dependency - Missing or
    # Incomplete AWS credentials in .env or environment'
    if not access_key or not secret_key or not access_key.strip() or not secret_key.strip():
        return {
            'status': 424,
            'message': 'Failed Dependency - Missing or Incomplete AWS credentials in .env or environment',
        }

    # Check if the credentials are valid
    try:
        session = Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        print(f"Session Details: {session.__dict__}")
        user = session.client('iam').get_user()
        print(f"User Details: {user}")
    except NoCredentialsError:
        return {
            'status': 403,
            'message': 'Access Denied - AWS credentials are invalid',
        }
    except ClientError as e:
        print(f"Exception details: {e}")
        if e.response['Error']['Code'] == 'InvalidClientTokenId':
            return {
                'status': 403,
                'message': 'Access Denied - AWS credentials are invalid',
            }
        raise e

    # Check if the credentials have access to S3
    try:
        user = session.client('iam').get_user()
    except Exception as e:
        return {
            'status': 403,
            'message': 'Access Denied - AWS credentials are invalid',
        }
    response = s3_client.list_buckets()
    buckets = response['Buckets']

    bucket_names = [bucket['Name'] for bucket in buckets]
    access = parallel_check_bucket_permissions(tuple(bucket_names), s3_client)

    if 'access' in response:
        print(f"Final buckets in response: {list(response['access'].keys())}")

    return {
        'status': 200,
        'message': 'AWS credentials retrieved successfully.',
        'credentials': {
            'AWS_ACCESS_KEY_ID': access_key,
            'AWS_SECRET_ACCESS_KEY': secret_key,
        },
        'access': access
    }

#@timing_decorator
def is_binary_file(file_path_or_content: Union[str, bytes]) -> bool:
    """
    Determine if the provided content or file path represents binary or text content.

    Args:
    | Name                | Type          | Description                               |
    |---------------------|---------------|-------------------------------------------|
    | file_path_or_content| str or bytes  | The path to the file or the content.      |

    Returns:
    A boolean indicating if the content is binary (True) or text (False).
    """
    try:
        # Check if content is bytes
        if isinstance(file_path_or_content, bytes):
            try:
                # Attempt to decode as UTF-8, if it fails, it's likely binary
                file_path_or_content.decode('utf-8')
                return False  # Decoding succeeded, likely text
            except UnicodeDecodeError:
                return True  # Decoding failed, likely binary

        # If content is string, perform further checks
        elif isinstance(file_path_or_content, str):
            # Check for S3 URL
            if file_path_or_content.startswith('s3://'):
                # S3 logic here, assuming we can determine if the S3 object is binary or text
                # Placeholder return, should be replaced with actual S3 object check
                return True

            # Check if content is a file path using regex
            elif re.match(r"^(~?/)?(\.?([^/\0\n ]|\\ )+/?)*([^/\0\n ]+|'[^/\0\n']+')$", file_path_or_content):
                if os.path.isfile(file_path_or_content):
                    # File-based logic here, assuming we can determine if the local file is binary or text
                    # Placeholder return, should be replaced with actual file content check
                    return True

                # String matches file path pattern but is not a file, treat as content
                else:
                    # Content-based logic here, assuming we can determine if the string is binary or text
                    # Placeholder return, should be replaced with actual content analysis
                    return False

            # If the regex does not match, treat it as text content
            else:
                return False

        # If the input is neither str nor bytes, raise a TypeError
        else:
            raise TypeError("file_path_or_content must be either str or bytes.")
            
    except Exception as e:
        # Log the exception or handle it as needed
        raise e  # Reraising the exception after handling it

# Note: Actual MIME type checks using 'magic' or S3 object content type checks are not included here.
# Replace the placeholder returns with proper checks as needed.

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
        # Return an empty dictionary instead of None when an error occurs
        return {'Error': str(e), 'Metadata': {}}
    
    # Return the entire response if no error occurred
    return response.get('Metadata', {})

# Function to get MD5 hash of the content
def get_md5_hash(content: Union[str, bytes]) -> str:
    """
    # Calculates the MD5 hash of the given content.

    ## Arguments

    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | content   | Union[str, bytes] | The content for which to calculate the MD5 hash. |   |

    ## Returns
    The MD5 hash of the content.
    
    """
    if isinstance(content, str):
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    else:
        return hashlib.md5(content).hexdigest()

# Function to get file size
def get_file_size(content: Union[str, bytes]) -> int:
    """
    # Calculates the size of the given content.

    ## Arguments

    | Name      | Type              | Description | Default |
    |-----------|-------------------|-------------|---------|
    | content   | Union[str, bytes] | The content for which to calculate the size. |   |

    ## Returns
    The size of the content in bytes.
    
    """
    if isinstance(content, str):
        return len(content.encode('utf-8'))
    else:
        return len(content)


def get_mime_type_content(content: Union[str, bytes]) -> str:
    """
    Determines the MIME type of the given content.

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

def get_md5_hash_filename(filename: str, debug=False) -> str:
    """
    Get the MD5 hash of a file using filename and path, with optional debugging information.
    
    ## Arguments
    
    | Name      | Type    | Description                        | Default |
    |-----------|---------|------------------------------------|---------|
    | filename  | str     | The name of the file               | None    |
    | debug     | bool    | Flag to return debugging information | False  |

    Returns:
    The MD5 hash of the file, with optional debugging information.
    """
    debug_info = {
        'filename_provided': filename,
        'steps': []
    }

    # Check if the filename is empty
    if not filename:
        debug_info['error'] = "No filename supplied"
        raise ValueError("No filename supplied")

    # Check if the filename is an S3 URL
    if filename.startswith('s3://'):
        debug_info['steps'].append('Filename is an S3 URL')
        # Fetch the metadata of the S3 object
        metadata = get_s3_metadata(filename)
        debug_info['steps'].append('S3 metadata retrieved')
        debug_info['metadata'] = metadata
        debug_info['md5_from_metadata'] = metadata['md5']
        # Extract the MD5 hash from the metadata
        md5_hash = metadata['md5']
        if debug:
            debug_info['result'] = md5_hash
            return debug_info
        return md5_hash

    # Check if the file exists
    if not os.path.exists(filename):
        debug_info['steps'].append('File does not exist')
        if debug:
            debug_info['result'] = None
            return debug_info
        return None

    try:
        # Open the file and read the contents
        with open(filename, 'rb') as file:
            content = file.read()
            debug_info['steps'].append('File content read')
        # Return the MD5 hash of the file contents
        md5_hash = get_md5_hash(content)
        debug_info['steps'].append('MD5 hash computed')
    except Exception as e:
        debug_info['steps'].append(f'Error reading file: {e}')
        if debug:
            debug_info['error'] = str(e)
            return debug_info
        raise

    if debug:
        debug_info['result'] = md5_hash
        return debug_info
    return md5_hash


# Function to check if a file exists
def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
    | Name      | Type     | Description           | Default |
    |-----------|----------|-----------------------|---------|
    | file_path | string   | Path to the file      |         |

    Returns:
    A boolean indicating if the file exists (True) or not (False).
    """
    # Check if the file_path is an S3 URL
    if file_path.startswith('s3://'):
        # Fetch the metadata of the S3 object
        metadata = get_s3_metadata(file_path)
        # If metadata is returned, the file exists
        if metadata:
            return True
        # If no metadata is returned, the file does not exist
        else:
            return False

    # If the file_path is not an S3 URL, assume it's a local file path
    else:
        # Check if the file exists
        return os.path.exists(file_path)

def compare_s3_local_file(local_file, s3_file):
    """
    # Compare S3 Local File
    Validates that a file on S3 has the same content as a local file by downloading and comparing them.
    """
    # Download the S3 file to a tmp file name
    s3 = boto3.resource('s3')
    s3.meta.client.download_file(s3_bucket_name, s3_file, 'tests/tmp')
    # Make sure that the tmp file was created
    assert os.path.exists('tests/tmp')
    # Compare the local file to the tmp file
    local_file_content = open(local_file, 'rb').read()
    tmp_file_content = open('tests/tmp', 'rb').read()
    # Make sure that the local file and the tmp file have the same content
    assert local_file_content == tmp_file_content
    # Delete the tmp file
    os.remove('tests/tmp')
