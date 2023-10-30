from klingon_file_manager import manage_file
from klingon_file_manager.utils import ProgressPercentage
import base64
import boto3
import hashlib
import lorem
import os
import subprocess


AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

# Set s3 bucket name
s3_bucket_name = AWS_S3_BUCKET_NAME

# Generate a 100 word string of lorem ipsum text
test_txt_content = lorem.text()

# test_txt_content = 'Hello World!'
test_bin_content = b'\x00\x00\x00\x00\x00\x00\x00\x00'

# Test Files - get
test_txt_get = 'tests/test_get_txt_file.txt'
test_bin_get = 'tests/test_get_bin_file.wav'

# Test Files - post
test_txt_post = 'tests/test_post_txt_file.txt'
test_bin_post = 'tests/test_post_bin_file.wav'


def compare_s3_local_file(local_file, s3_file):
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

# Cleanup test files
def cleanup_test_files():
    ##
    ## Remove any test files created by other test runs
    ##
    # Create array of test file URLs and paths
    test_files = [
        "s3://"+s3_bucket_name+"/"+test_txt_post,
        "s3://"+s3_bucket_name+"/"+test_bin_post,
        "s3://"+s3_bucket_name+"/"+test_txt_get,
        "s3://"+s3_bucket_name+"/"+test_bin_get,
        test_txt_post,
        test_bin_post,
        test_txt_get,
        test_bin_get
    ]
    # Loop through the test files and delete them if they exist and log if they
    # existed or not, and if they were deleted or not
    for test_file in test_files:
        # Check if the test file exists
        if manage_file('get', test_file, None)['status'] == 200:
            # If the test file exists, delete it
            result = manage_file('delete', test_file, None)
            print(result)
            assert result['status'] == 200
            assert result['action'] == 'delete'
            assert result['path'] == test_file
            # Make sure that the test file was deleted
            assert manage_file('get', test_file, None)['status'] == 404
        else:
            # If the test file does not exist, log that it did not exist
            print("Test file did not exist: " + test_file)

    
        

# Create test files
def setup_test_files():
    ##
    ## GET TEST FILES
    ##
    # Cleanup previous test files
    cleanup_test_files()
    # Create local test txt file
    with open(test_txt_get, 'w') as f:
        f.write(test_txt_content)
    # Make sure that the test_txt_get file was created
    assert os.path.exists(test_txt_get)
    # Create local test binary file
    with open(test_bin_get, 'wb') as f:
        f.write(test_bin_content)
    # Make sure that the test_bin_get file was created
    assert os.path.exists(test_bin_get)
    # Upload test_txt_get file to test_txt_get location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_txt_get, s3_bucket_name, test_txt_get)
    # Make sure that the test_txt_get file was created
    compare_s3_local_file(test_txt_get, test_txt_get)
    # Upload test_bin_get file to test_bin_get_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_bin_get, s3_bucket_name, test_bin_get)
    # Make sure that the test_bin_get_s3 file was created
    compare_s3_local_file(test_bin_get, test_bin_get)

#setup_test_files()

# Test 12 - Test aws credentials
def test_check_aws_access_key_id():
    assert AWS_ACCESS_KEY_ID is not None

# Test 13 - Test aws credentials
def test_check_aws_secret_access_key():
    assert AWS_SECRET_ACCESS_KEY is not None


# Test 7 - post s3 text file
def test_post_s3_txt_file():
    result = manage_file(action='post', path="s3://"+s3_bucket_name+"/"+test_txt_post, content=test_txt_content, debug=True)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == "s3://"+s3_bucket_name+"/"+test_txt_post
    assert result['binary'] is False
    # Additional check: Read the file from s3 to make sure content was written
    # correctly
    validate = manage_file('get', "s3://"+s3_bucket_name+"/"+test_txt_post, None, debug=True)
    print(validate)
    assert validate['status'] == 200
    assert validate['action'] == 'get'
    assert validate['content'].decode() == test_txt_content
    assert validate['path'] == "s3://"+s3_bucket_name+"/"+test_txt_post

#test_post_s3_txt_file()

# Basic manage_file test - write test_txt_content text to tests/text.txt
def test_post_local_txt_file():
    result = manage_file(action='post', path=test_txt_post, content=test_txt_content, debug=True)
    print(result)

#test_post_local_txt_file()

# Basic manage_file test - write test_txt_content text to s3
# fsg-gobbler/tests/test_post_txt_file.txt
def test_post_s3_txt_file():
    print(f"Posting to: path=s3://fsg-gobbler/{test_txt_post}")
    result = manage_file(action='post', path="s3://fsg-gobbler/"+test_txt_post, content=test_txt_content, debug=True)
    
#    print(result)






def test_large_upload_progress():
    # Generate a 100MB file using dd command
    subprocess.run(['dd', 'if=/dev/zero', 'of=./large_file', 'bs=1M', 'count=10'])

    # Get md5 hash of the generated file
    with open('./large_file', 'rb') as f:
        # Read the file content
        file_content = f.read()
        
        # Get the md5 hash of the file content
        md5_hash = hashlib.md5(file_content).digest()
        # print(f"md (binary):                    {md5_hash}")

        # Encode the md5 hash of the file content to base64 to send to S3
        contents_md5 = base64.b64encode(md5_hash).decode('utf-8')
        # print(f"contents_md5 (base64):          {contents_md5}")
        
        # Convert md5_hash to a hex string for metadata and logging
        md5_hash_hex = md5_hash.hex()
        print(f"The MD5 Hash of this file is:   {md5_hash_hex}")

        # Get & announce the file size in bytes
        file_size = len(file_content)
        # print(f"The file size is: {file_size} bytes")

        # Get the file size in either bytes, kilobytes, megabytes or gigabytes depending
        # on how large it is, showing up to 6 decimal places, returning a
        # string
        def get_file_size(file_size, show_bytes=False):
            if show_bytes:
                return f"{file_size} B"
            elif file_size < 1000000:
                return f"{round(file_size / 1000, 6)} KB"
            elif file_size < 1000000000:
                return f"{round(file_size / 1000000, 6)} MB"
            else:
                return f"{round(file_size / 1000000000, 6)} GB"
        print(f"The file size is: {get_file_size(file_size)}")

    # Create metadata
    metadata = {
        "md5chksum": md5_hash_hex,
        "filesize": file_size
    }

    # Create a progress callback
    progress = ProgressPercentage(file_size, './large_file')

    # Upload the file with progress callback
    from klingon_file_manager import manage_file
    manage_file(
        action='post',
        path="s3://fsg-gobbler/tests/large_file",
        content=file_content,
        md5=md5_hash_hex,
        metadata=metadata,
        debug=True
    )

    # Delete the generated file
    #os.remove('./large_file')

    # Sleep for 5 seconds to allow the file to sync within s3's systems
    import time
    time.sleep(5)

    # Get file metadata
    s3 = boto3.client('s3')
    try:
        head_object_response = s3.head_object(Bucket='fsg-gobbler', Key='tests/large_file')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    metadata = head_object_response['Metadata']
    content_length = head_object_response['ContentLength']
    content_type = head_object_response['ContentType']

    print(f"metadata:           {metadata}")
    print(f"content_length:     {content_length}")
    print(f"content_type:       {content_type}")

test_large_upload_progress()

