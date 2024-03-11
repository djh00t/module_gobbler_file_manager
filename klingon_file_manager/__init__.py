# __init__.py
"""
# Klingon File Manager

Klingon File Manager is a cross-platform file management system designed to
streamline and unify the process of file management across local and s3 storage
solutions. The module provides a single programmatic interface for reading,
writing, and deleting files, with additional support for debugging and AWS S3
authentication.

## Modules
- [`manage`](/klingon_file_manager/manage.html): Coordinates the CRUD (Create,
Read, Update, Delete) operations, orchestrating calls to submodules, ensuring
transactional integrity.
  
## Submodules
- [`post`](/klingon_file_manager/post.html): Manages the saving of files to AWS
S3 or a local storage system, including setting appropriate metadata and
permissions.
- [`get`](/klingon_file_manager/get.html): Handles the retrieval of files,
supporting both AWS S3 and local file paths, ensuring proper MIME type
handling.
- [`delete`](/klingon_file_manager/delete.html): Provides functionality for
deleting files from AWS S3 or local storage, with checks for proper permissions
and existence.
- [`utils`](/klingon_file_manager/utils.html): A collection of utility
functions that support the main operations.
  - [`timing_decorator`](/klingon_file_manager/utils.html#timing_decorator):
    Decorator for timing the execution of a function.
  - [`get_mime_type`](/klingon_file_manager/utils.html#get_mime_type): Gets the
    MIME type of a file.
  - [`parallel_check_bucket_permissions`](/klingon_file_manager/utils.html#parallel_check_bucket_permissions):
    Checks the permissions of multiple S3 buckets concurrently.
  - [`check_bucket_permissions`](/klingon_file_manager/utils.html#check_bucket_permissions):
    Checks the permissions of an S3 bucket.
  - [`get_aws_credentials`](/klingon_file_manager/utils.html#get_aws_credentials):
    Gets AWS credentials from environment variables.
  - [`is_binary_file`](/klingon_file_manager/utils.html#is_binary_file): Checks
    if a file is binary or not.
  - [`get_s3_metadata`](/klingon_file_manager/utils.html#get_s3_metadata): Gets
    the metadata of an S3 object.
  - [`get_md5_hash`](/klingon_file_manager/utils.html#get_md5_hash): Calculates
    the MD5 hash of the given content. 
  - [`get_file_size`](/klingon_file_manager/utils.html#get_file_size):
    Calculates the size of the given content. 
  - [`get_mime_type_content`](/klingon_file_manager/utils.html#get_mime_type_content): Determines the MIME type of the given content.

## Usage Examples

### Uploading a File to S3

```python
###
### Uploading a File to S3
###
# Note: This example assumes that the AWS credentials are stored in environment
#       variables.
from klingon_file_manager import post

# Specify the local file path and the target S3 bucket and key
local_file_path = '/path/to/local/file.txt'
s3_bucket = 'my-s3-bucket'
s3_key = 'folder/file.txt'

# Upload the file
post.upload_file(local_file_path, s3_bucket, s3_key)
```

### Downloading a File from S3
  
```python
###
### Downloading a File from S3
###
# Note: This example assumes that the AWS credentials are stored in environment
#       variables.
from klingon_file_manager import get

# Specify the S3 bucket and key, and the local file path for saving the file
s3_bucket = 'my-s3-bucket'
s3_key = 'folder/file.txt'
local_file_path = '/path/to/download/file.txt'

# Download the file
get.download_file(s3_bucket, s3_key, local_file_path)
```

### Deleting a File Locally

```python
###
### Deleting a File Locally
###
# Note: This example assumes that the AWS credentials are stored in environment
#       variables.
from klingon_file_manager import delete

# Specify the local file path
local_file_path = '/path/to/delete/file.txt'

# Delete the file
delete.delete_file(local_file_path)
```

### Managing Files Across Local and S3

```python
###
### Managing Files Across Local and S3
###
# Note: This example assumes that the AWS credentials are stored in environment
#       variables.
from klingon_file_manager import manage

# Move a file from local to S3
local_file_path = '/path/to/local/file.txt'
s3_bucket = 'my-s3-bucket'
s3_key = 'folder/file.txt'

# Perform the move operation which might involve upload and delete
manage.move_file(local_file_path, s3_bucket, s3_key)

# List all files in a local directory and an S3 bucket
local_directory_path = '/path/to/local/directory'
s3_bucket = 'my-s3-bucket'

local_files = manage.list_files(local_directory_path)
s3_files = manage.list_files(s3_bucket)

print(f"Local files: {local_files}")
print(f"S3 files: {s3_files}")
```

"""

from .manage import manage_file, move_file, FilesystemRouter
from .delete import delete_file
from .get import get_file
from .post import post_file, _post_to_local, _post_to_s3
from .utils import get_mime_type, check_bucket_permissions, get_aws_credentials, is_binary_file, get_s3_metadata, timing_decorator, get_file_size, get_md5_hash, get_mime_type_content,parallel_check_bucket_permissions,get_md5_hash_filename,check_file_exists, compare_s3_local_file
