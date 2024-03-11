# test_functional_tests.py
"""
# Functional Tests
This module tests the functionality of the `manage_file` function within the
`klingon_file_manager.manage` package. It includes tests for creating, retrieving, and
deleting both text and binary files on the local filesystem and AWS S3.

#### Note:
This module requires the following environment variables to be set:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_S3_BUCKET_NAME

The aws access keypair will need access to your S3 bucket as the tests will
create and delete files in the bucket, so it is recommended to use a dedicated
bucket for testing purposes.

"""
import os
import logging
from klingon_file_manager import manage_file, move_file, get_md5_hash_filename
import lorem
import boto3

# Logging configuration
logging.basicConfig(level=logging.INFO)

"""
# AWS Credentials & Bucket Name
These credentials are retrieved from the operating system environment and are
used to access the AWS S3 bucket.

"""
# Retrieve AWS credentials from environment variables
AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
""" AWS_ACCESS_KEY_ID - required for S3 access @private """
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
""" AWS_SECRET_ACCESS_KEY - required for S3 access @private """
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
""" AWS_S3_BUCKET_NAME - required for S3 access @private """
# Set s3 bucket name
s3_bucket_name = AWS_S3_BUCKET_NAME
""" s3_bucket_name - required for S3 access @private """


def test_create_test_dirs():
    """
    # Create Test Directories
    This test case is responsible for creating the ./tests/testfiles directory if it does not exist.
    """
    if not os.path.exists("tests/testfiles"):
        print("Creating tests/testfiles directory")
        os.mkdir("tests/testfiles")
    else:
        print("./tests/testfiles directory already exists")

# Ensure test directories are created
test_create_test_dirs()

def generate_text_file(file_name, chars: int = 100):
    """
    # Generate Text File
    Generates a text file with lorem ipsum content and returns the file path.
    """
    content = lorem.text()[:chars]
    with open(file_name, 'w') as f:
        f.write(content)
    return file_name


"""
# Test File Variables
Set the names of the test files to be used in the tests below.
"""
# Test Files - get
test_txt_get = 'tests/testfiles/test_get_txt_file.txt'
""" test_txt_get - name of the test text file to be used in GET tests """
test_bin_get = 'tests/testfiles/test_get_bin_file.wav'
""" test_bin_get - name of the test binary file to be used in GET tests """

# Test Files - post
test_txt_post = 'tests/testfiles/test_post_txt_file.txt'
""" test_txt_post - name of the test text file to be used in POST tests """
generate_text_file(test_txt_post)
test_bin_post = 'tests/testfiles/test_post_bin_file.wav'
""" test_bin_post - name of the test binary file to be used in POST tests """


# Test Files - move
test_txt_move = 'tests/testfiles/test_move_txt_file.txt'
""" test_txt_move - name of the test text file to be used in MOVE tests """
generate_text_file(test_txt_move)
test_bin_move = 'tests/testfiles/test_move_bin_file.wav'
""" test_bin_move - name of the test binary file to be used in MOVE tests """


# Generate a 100 word string of lorem ipsum text
test_txt_content = lorem.text()
""" test_txt_content - lorem ipsum text to be used in text file tests """


# Create a 1KB test binary file
""" ./tests/testfiles/1kb.bin - 1KB binary file to be used in binary file tests """
with open("./tests/testfiles/1kb.bin", "wb") as f:
    f.write(os.urandom(1024))
    
# Read the 1KB test binary file into test_bin_content if
# ./tests/testfiles/1kb.bin doesn't exist
""" test_bin_content - binary content of the 1KB test binary file """
with open("./tests/testfiles/1kb.bin", "rb") as f:
    test_bin_content = f.read()

# Hard link the 1KB test binary file to the test_bin_get file if test_bin_get
# doesn't exist
""" test_bin_get - name of the test binary file to be used in GET tests """
if not os.path.exists(test_bin_get):
    os.link("./tests/testfiles/1kb.bin", test_bin_get)

# Hard link the 1KB test binary file to the test_bin_post file if test_bin_post
# doesn't exist
""" test_bin_post - name of the test binary file to be used in POST tests """
if not os.path.exists(test_bin_post):
    os.link("./tests/testfiles/1kb.bin", test_bin_post)

# Hard link the 1KB test binary file to the test_bin_move file if test_bin_move
# doesn't exist
""" test_bin_move - name of the test binary file to be used in MOVE tests """
if not os.path.exists(test_bin_move):
    os.link("./tests/testfiles/1kb.bin", test_bin_move)


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

# Create test files
def test_setup_test_files():
    """
    # Setup Test Files
    Ensures that necessary test files are created both locally and on S3 to be used in subsequent tests.
    This setup includes creating text and binary files, verifying their creation, and uploading them to S3.
    """
    # Create local test txt file
    with open(test_txt_get, 'w') as f:
        f.write(test_txt_content)
    # Make sure that the test_txt_get file was created
    assert os.path.exists(test_txt_get), "Text file for GET request was not created."

    # Create local binary files by copying the 1KB binary test file.
    if not os.path.exists(test_bin_get):
        os.copy('tests/testfiles/1kb.bin', test_bin_get)
    if not os.path.exists(test_bin_post):
        os.copy('tests/testfiles/1kb.bin', test_bin_post)
    if not os.path.exists(test_bin_move):
        os.copy('tests/testfiles/1kb.bin', test_bin_move)
    # Confirm that the binary files exist.
    assert os.path.exists(test_bin_get), "Binary file for GET request was not created."
    assert os.path.exists(test_bin_post), "Binary file for POST request was not created."
    assert os.path.exists(test_bin_move), "Binary file for MOVE request was not created."

    # Upload the text and binary files to S3 and confirm their presence by comparing with local files.
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_txt_get, s3_bucket_name, test_txt_get)
    compare_s3_local_file(test_txt_get, test_txt_get)
    s3.meta.client.upload_file(test_bin_get, s3_bucket_name, test_bin_get)
    compare_s3_local_file(test_bin_get, test_bin_get)



# Function to test the retrieval of a text file from S3.
def test_get_s3_txt_file():
    """
    # Get S3 Text File
    
    Tests the retrieval of a text file from S3 to ensure the `manage_file`
    function correctly handles S3 GET requests.
    """
    # Attempt to retrieve the S3 text file using the `manage_file` function.
    result = manage_file('get', test_txt_get, None)
    # Verify that the result indicates a successful retrieval with the correct content and file path.
    assert result['status'] == 200, "Retrieval of S3 text file failed - status code mismatch."
    assert result['action'] == 'get', "Retrieval of S3 text file failed - action mismatch."
    assert result['content'].decode() == test_txt_content, "Retrieval of S3 text file failed - content mismatch."
    assert result['path'] == test_txt_get, "Retrieval of S3 text file failed - path mismatch."
    assert result['binary'] is False, "Retrieval of S3 text file failed - binary flag mismatch."

# Function to test the retrieval of a binary file from S3.
def test_get_s3_bin_file():
    """
    # Get S3 Binary File
    
    Tests the retrieval of a binary file from S3 to ensure the `manage_file`
    function correctly handles S3 GET requests for binary data.
    """
    # Attempt to retrieve the S3 binary file using the `manage_file` function.
    result = manage_file('get', test_bin_get, None)
    # Verify that the result indicates a successful retrieval with the correct content and file path.
    assert result['status'] == 200, "Retrieval of S3 binary file failed - status code mismatch."
    assert result['action'] == 'get', "Retrieval of S3 binary file failed - action mismatch."
    assert result['content'] == test_bin_content, "Retrieval of S3 binary file failed - content mismatch."
    assert result['path'] == test_bin_get, "Retrieval of S3 binary file failed - path mismatch."
    assert result['binary'] is True, "Retrieval of S3 binary file failed - binary flag mismatch."

def test_get_s3_txt_file():
    """
    # Get S3 Text File
    Checks the functionality of retrieving a text file from S3 using the `manage_file` function.
    """
    result = manage_file('get', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] is False

def test_get_s3_bin_file():
    """
    # Get S3 Binary File
    Verifies the `manage_file` function's ability to correctly retrieve a binary file from S3.
    """
    result = manage_file('get', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'] == test_bin_content
    assert result['path'] == test_bin_get
    assert result['binary'] is True

def test_post_local_txt_file():
    """
    # Post Local Text File
    Tests the `manage_file` function for its ability to handle posting text content to a local file.
    """
    result = manage_file(
        action='post',
        path=test_txt_post,
        content=test_txt_content[:100]
    )
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['content'][:10] == test_txt_content[:10]
    assert result['path'] == test_txt_post
    assert result['binary'] is False

def test_post_local_bin_file():
    """
    # Post Local Binary File
    Ensures the `manage_file` function can post binary content to a local file.
    """
    result = manage_file(
        action='post',
        path=test_bin_post,
        content=test_bin_content
    )
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == test_bin_post
    assert result['binary'] is True


def test_post_s3_txt_file():
    """
    # Post S3 Text File
    Tests the `manage_file` function's ability to post a text file to S3 and subsequently retrieve it for verification.
    """
    result = manage_file('post', f"s3://{s3_bucket_name}/{test_txt_post}", test_txt_content)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_txt_post}"
    assert result['binary'] is False
    validate = manage_file('get', f"s3://{s3_bucket_name}/{test_txt_post}", None)
    print(validate)
    assert validate['status'] == 200
    assert validate['action'] == 'get'
    assert validate['content'].decode() == test_txt_content
    assert validate['path'] == f"s3://{s3_bucket_name}/{test_txt_post}"

def test_post_s3_bin_file():
    """
    # Post S3 Binary File
    Ensures the `manage_file` function can post binary content to S3 and validate it by retrieving the content.
    """
    result = manage_file('post', f"s3://{s3_bucket_name}/{test_bin_post}", test_bin_content)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_bin_post}"
    validate = manage_file('get', f"s3://{s3_bucket_name}/{test_bin_post}", None)
    print(validate)
    assert validate['status'] == 200
    assert validate['action'] == 'get'
    assert validate['content'] == test_bin_content
    assert validate['path'] == f"s3://{s3_bucket_name}/{test_bin_post}"

def test_invalid_action():
    """
    # Invalid Action
    Validates the `manage_file` function's handling of an invalid action by confirming that it returns an error status.
    """
    result = manage_file('invalid', None, None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'invalid'

def test_get_invalid_local_path():
    """
    # Invalid Local Path
    Tests the `manage_file` function's response to an invalid local file path to ensure proper error handling.
    """
    result = manage_file('get', './nonexistent.txt', None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'get'

def test_get_invalid_s3_path():
    """
    # Invalid S3 Path
    Checks the `manage_file` function's behavior when attempting to get a file from an invalid S3 path.
    """
    result = manage_file('get', f's3://{s3_bucket_name}/nonexistent.txt', None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'get'

def test_move_local_txt_file_local():
    """
    # Move Local Text File to Local Directory
    Tests the `move_file` function's ability to move a local text file to a local directory.
    """
    src_file = 'tests/testfiles/test_move_local_txt_file.txt'
    dst_file = 'tests/testfiles/test_move_local_txt_file_moved.txt'
    generate_text_file(src_file, 100)
    src_md5 = get_md5_hash_filename(src_file)
    result = move_file(src_file, dst_file, True)
    dst_md5 = get_md5_hash_filename(dst_file)
    # Capture result variables
    print(f"Result: {result}")
    status = result['status']
    message = result['message']
    source = result['source']
    destination = result['destination']
    print(f"Result: {result}")
    print(f"SRC MD5: {src_md5}")
    print(f"DST MD5: {dst_md5}")
    assert result['status'] == 200
    assert result['message'] == 'File moved successfully.'
    assert result['source'] == src_file
    assert result['destination'] == dst_file
    assert src_md5 == dst_md5

def test_move_local_txt_file_s3():
    """
    # Move Local Text File to S3
    Ensures the `move_file` function can move a local text file to S3.
    """
    src_file = 'tests/testfiles/test_move_local_txt_file.txt'
    dst_file = f"s3://{s3_bucket_name}/development/unit-tests/test_move_local_txt_file_moved.txt"
    generate_text_file(src_file, 100)
    src_md5 = get_md5_hash_filename(src_file)
    result = move_file(src_file, dst_file)
    dst_md5 = get_md5_hash_filename(dst_file)
    # Capture result variables
    print(f"Result: {result}")
    status = result['status']
    message = result['message']
    # source = result['source']
    destination = result['destination']
    print(f"Result: {result}")
    print(f"SRC MD5: {src_md5}")
    print(f"DST MD5: {dst_md5}")
    assert result['status'] == 200
    assert result['message'] == 'File moved successfully.'
    assert result['source'] == src_file
    assert result['destination'] == dst_file
    assert src_md5 == dst_md5


def test_check_aws_access_key_id():
    """
    # Check AWS Access Key ID
    Asserts that the AWS Access Key ID is set in the environment variables.
    """
    assert AWS_ACCESS_KEY_ID is not None

def test_check_aws_secret_access_key():
    """
    # AWS Secret Access Key
    Ensures that the AWS Secret Access Key is defined in the environment.
    """
    assert AWS_SECRET_ACCESS_KEY is not None

def test_delete_local_test_txt_post_file():
    """
    # Delete Local Text File (test_txt_post)
    Tests the deletion of a local text file and verifies that the file no longer exists after deletion.
    """
    assert os.path.exists(test_txt_post)
    result = manage_file('delete', test_txt_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_txt_post
    assert not os.path.exists(test_txt_post)

def test_delete_local_test_txt_get_file():
    """
    # Delete Local Text File (test_txt_get)
    Validates the functionality to delete a local text file and confirms the file's absence after the process.
    """
    assert os.path.exists(test_txt_get)
    result = manage_file('delete', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_txt_get
    assert not os.path.exists(test_txt_get)

def test_delete_local_test_bin_post_file():
    """
    # Delete Local Binary File (test_bin_post)
    Checks the `manage_file` function's ability to remove a local binary file and ensures the file is not present post-deletion.
    """
    assert os.path.exists(test_bin_post)
    result = manage_file('delete', test_bin_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_bin_post
    assert not os.path.exists(test_bin_post)

def test_delete_local_test_bin_get_file():
    """
    # Delete Local Binary File (test_bin_get)
    Tests the deletion of a local binary file, confirming the file's removal from the filesystem.
    """
    assert os.path.exists(test_bin_get)
    result = manage_file('delete', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_bin_get
    assert not os.path.exists(test_bin_get)

def test_delete_s3_test_txt_post_file():
    """
    # Delete S3 Text File (test_txt_post)
    Tests the deletion of a text file stored in S3 and checks the success of the delete action.
    """
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_txt_post}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_txt_post}"

def test_delete_s3_test_bin_post_file():
    """
    # Delete S3 Binary File (test_bin_post)
    Verifies the ability to delete a binary file from S3 and ensures that the action completes successfully.
    """
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_bin_post}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_bin_post}"

def test_delete_s3_test_txt_get_file():
    """
    # Delete S3 Text File (test_txt_get)
    Tests the deletion of a text file stored in S3 and ensures the path is correct and the deletion status is successful.
    """
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_txt_get}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_txt_get}"

def test_delete_s3_test_bin_get_file():
    """
    # Delete S3 Binary File (test_bin_get)
    Verifies the functionality of the `manage_file` function to delete a binary file from S3, checking the status and action result.
    """
    result = manage_file('delete', f"s3://{s3_bucket_name}/{test_bin_get}", None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == f"s3://{s3_bucket_name}/{test_bin_get}"


def test_cleanup_test_files():
    """
    # Teardown Test Files
    This test case is responsible for cleaning up and removing all test files created during the testing process, both locally and in the test files directory.
    """
    # Remove tests/testfiles directory if it exists
    if os.path.exists('tests/testfiles'):
        print("tests/testfiles directory exists, emptying it..")
        # Remove all files in tests/testfiles directory
        for file in os.listdir('tests/testfiles'):
            print(f"Removing tests/testfiles/{file}")
            os.remove(f"tests/testfiles/{file}")
        # Remove tests/testfiles directory
        print("Removing tests/testfiles directory")
        os.rmdir('tests/testfiles')
