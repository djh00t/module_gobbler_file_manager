"""
# Configuration Module

This module provides centralized classes for managing frequently used
variables/constants used by this projects unit tests. 

## Classes and Features

- **FilePathManager**: This class provides methods for handling and
  manipulating file paths. It can be used to determine where data is stored or
  retrieved from.

- **ChecksumHandler**: This class includes functions for calculating and
  verifying checksums. This is essential for ensuring data integrity during
  storage and transmission.

- **CredentialManager**: This class contains utilities for securely handling
  user credentials. This is crucial for maintaining secure access to resources.

## Usage

Import the module and create instances of the provided classes as needed. Each
class provides methods related to their respective features:

**Get Git Project Root**
```python
from config import FilePaths

def test_get_git_project_root():
    \"\"\"
    # Get Git Project Root
    Asserts that the Git project root directory is found.
    \"\"\"
    assert FilePaths.get_git_project_root() is not None
```

**Check AWS Access Key ID**
```python
from config import CredentialManager

def test_check_aws_access_key_id():
    \"\"\"
    # Check AWS Access Key ID
    Asserts that the AWS Access Key ID is set in the environment variables.
    \"\"\"
    credential_manager = CredentialManager()
    aws_access_key_id = credential_manager.get_aws_access_key_id()
    assert aws_access_key_id is not None
```

**Delete Local Test TXT File & Verify it doesn't exist**
```python
from config import FileManager

def test_delete_local_test_txt_post_file():
    \"\"\"
    # Delete Local Text File (test_txt_post)
    Tests the deletion of a local text file and verifies that the file no longer exists after deletion.
    \"\"\"
    file_manager = FileManager()
    assert file_manager.file_exists(test_txt_post)
    result = file_manager.delete_file(test_txt_post)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_txt_post
    assert not file_manager.file_exists(test_txt_post)
``` 

**Verify MD5 Hash of Local Test TXT File**
```python
from config import ChecksumHandler

def test_verify_md5_hash_local_test_txt():
    \"\"\"
    # Verify MD5 Hash of Local Test TXT File
    Tests the verification of the MD5 hash of a local text file.
    \"\"\"
    checksum_handler = ChecksumHandler()
    assert checksum_handler.verify_md5_hash(test_txt_post, test_txt_post_md5)
```

Remember to handle any exceptions that may be raised by the methods in this module.

"""

import os
from git import Repo

class BasePaths:
    """
    # BasePaths Class

    This class provides methods for generating base paths for S3 and local file storage.

    ## Methods

    | Method              | Description                                         |
    |---------------------|-----------------------------------------------------|
    | `s3_static`         | Returns the S3 static path for a given bucket name. |
    | `local_static`      | Returns the local static path for a git root.       |
    | `s3_ephemeral`      | Returns the S3 ephemeral path for a bucket name.    |
    | `local_ephemeral`   | Returns the local ephemeral path for a git root.    |
    """

    @staticmethod
    def s3_static(bucket_name):
        """
        # S3 Static

        Generates an S3 static path for a specified bucket name.

        ## Arguments

        | Name         | Type   | Description                  |
        |--------------|--------|------------------------------|
        | `bucket_name`| `str`  | The S3 bucket name.          |

        ## Returns

        | Name         | Type   | Description                  |
        |--------------|--------|------------------------------|
        | `path`       | `str`  | The S3 static URL.           |
        """
        return f"s3://{bucket_name}/development/unit-tests/static"

    @staticmethod
    def local_static(git_root):
        """
        # Local Static

        Provides the local static file path based on the Git project root directory.

        ## Arguments

        | Name       | Type   | Description                          |
        |------------|--------|--------------------------------------|
        | `git_root` | `str`  | The root directory of the Git repo.  |

        ## Returns

        | Name       | Type   | Description                          |
        |------------|--------|--------------------------------------|
        | `path`     | `str`  | The local static file path.          |
        """
        return f"{git_root}/tests/testfiles/static"

    @staticmethod
    def s3_ephemeral(bucket_name):
        """
        # S3 Ephemeral

        Creates an S3 ephemeral path for the provided bucket name.

        ## Arguments

        | Name         | Type   | Description                  |
        |--------------|--------|------------------------------|
        | `bucket_name`| `str`  | The S3 bucket name.          |

        ## Returns

        | Name         | Type   | Description                  |
        |--------------|--------|------------------------------|
        | `path`       | `str`  | The S3 ephemeral URL.        |
        """
        return f"s3://{bucket_name}/development/unit-tests/ephemeral"

    @staticmethod
    def local_ephemeral(git_root):
        """
        # Local Ephemeral

        Determines the local ephemeral file path given the Git project root.

        ## Arguments

        | Name       | Type   | Description                          |
        |------------|--------|--------------------------------------|
        | `git_root` | `str`  | The root directory of the Git repo.  |

        ## Returns

        | Name       | Type   | Description                          |
        |------------|--------|--------------------------------------|
        | `path`     | `str`  | The local ephemeral file path.       |
        """
        return f"{git_root}/tests/testfiles/ephemeral"

class FilePaths(BasePaths):
    """
    # FilePaths Class

    Extends `BasePaths` to provide full static and ephemeral paths for both S3 and local storage.

    ## Attributes

    | Attribute             | Description                                    |
    |-----------------------|------------------------------------------------|
    | `AWS_S3_BUCKET_NAME`  | The AWS S3 bucket name from environment vars.  |

    ## Methods

    | Method                | Description                                       |
    |-----------------------|---------------------------------------------------|
    | `get_git_project_root` | Returns the Git project root directory.           |
    | `s3_static_path`      | Returns the S3 static path with the bucket name.  |
    | `local_static_path`   | Returns the local static path for the git root.   |
    | `s3_ephemeral_path`   | Returns the S3 ephemeral path with the bucket name.|
    | `local_ephemeral_path` | Returns the local ephemeral path for the git root.|
    """

    # AWS Bucket Name
    _AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

    def aws_s3_bucket_name(self):
        """
        # AWS S3 Bucket Name
        
        Returns the AWS S3 Bucket Name from environment vars.

        ## Returns
        A string containing the AWS S3 Bucket Name.
        
        | Name         | Type   | Description                  |
        |--------------|--------|------------------------------|
        | `aws_s3_bucket_name` | `str`  | The AWS S3 Bucket Name.          |

        """
        return self._AWS_S3_BUCKET_NAME

    @staticmethod
    def get_git_project_root():
        """
        Returns the root directory of the Git project.

        Returns:
            str: The root directory of the Git project.
        """
        try:
            git_repo = Repo('.', search_parent_directories=True)
            git_root = git_repo.git.rev_parse("--show-toplevel")
            return git_root
        except Exception as e:
            print(f"Error finding Git project root: {e}")
            return None

    @classmethod
    def s3_static_path(cls):
        """
        Returns the S3 static path based on the AWS S3 bucket name.

        Returns:
            str: The S3 static path.
        """
        return super().s3_static(cls._AWS_S3_BUCKET_NAME)

    @classmethod
    def local_static_path(cls):
        """
        Returns the local static path based on the Git project root directory.

        Returns:
            str: The local static path.
        """
        return super().local_static(cls.get_git_project_root())

    @classmethod
    def s3_ephemeral_path(cls):
        """
        Returns the S3 ephemeral path based on the AWS S3 bucket name.

        Returns:
            str: The S3 ephemeral path.
        """
        return super().s3_ephemeral(cls._AWS_S3_BUCKET_NAME)

    @classmethod
    def local_ephemeral_path(cls):
        """
        Returns the local ephemeral path based on the Git project root directory.

        Returns:
            str: The local ephemeral path.
        """
        return super().local_ephemeral(cls.get_git_project_root())

class Checksums:
    """
    # Checksums Class

    Provides checksum values for file integrity verification.

    ## Attributes

    | Attribute         | Description                            |
    |-------------------|----------------------------------------|
    | `test_audio_md5`  | MD5 checksum for a test audio file.    |
    | `test_text_md5`   | MD5 checksum for a test text file.     |
    """

    test_audio_md5 = 'f63bbe640a48144acd9b608b5eba4596'
    test_text_md5 = '6cd3556deb0da54bca060b4c39479839'

class Credentials:
    """
    # Credentials Class

    Manages access credentials for AWS services, sourced from environment variables.

    ## Attributes

    | Attribute                | Description                                     |
    |--------------------------|-------------------------------------------------|
    | `aws_access_key_id`      | The AWS access key ID.                          |
    | `aws_secret_access_key`  | The AWS secret access key.                      |
    """
    
    # Assuming these are stored as environment variables for security
    _AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    _AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')    

    def aws_access_key_id(self):
        """
        # AWS Access Key ID
        
        Returns the AWS Access Key ID from environment vars.

        ## Returns
        A string containing the AWS Access Key ID.
        
        | Name         | Type   | Description                  |
        |--------------|--------|------------------------------|
        | `aws_access_key_id` | `str`  | AWS Access Key ID.          |

        """
        return self._AWS_ACCESS_KEY_ID

    def aws_secret_access_key(self):
        """
        # AWS Secret Access Key
        
        Returns the AWS Secret Access Key from environment vars.

        ## Returns
        A string containing the AWS Secret Access Key.
        
        | Name         | Type   | Description                  |
        |--------------|--------|------------------------------|
        | `aws_secret_access_key` | `str`  | The AWS Secret Access Key ID.          |

        """
        return self._AWS_SECRET_ACCESS_KEY


# Usage Examples
print(FilePaths.s3_static_path())       # Returns the S3 static file path
print(FilePaths.local_static_path())    # Returns the local static file path
print(FilePaths.s3_ephemeral_path())    # Returns the S3 ephemeral file path
print(FilePaths.local_ephemeral_path()) # Returns the local ephemeral file path

print(Checksums.test_audio_md5)         # Returns the MD5 checksum for test audio
print(Checksums.test_text_md5)          # Returns the MD5 checksum for test text

print(Credentials.aws_access_key_id)    # Prints AWS Access Key ID
print(Credentials.aws_secret_access_key) # Prints AWS Secret Access Key
