from klingon_file_manager import manage_file
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
    subprocess.run(['dd', 'if=/dev/zero', 'of=./large_file', 'bs=1M', 'count=100'])

    # Get md5 hash of the generated file
    with open('./large_file', 'rb') as f:
        file_content = f.read()
        md5_hash = hashlib.md5(file_content).digest()
        contents_md5 = base64.b64encode(md5_hash).decode('utf-8')
        
    boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY).put_object(
        Bucket="fsg-gobbler",
        Key="tests/large_file",
        Body=file_content,
        ContentMD5=contents_md5
    )


    # Upload the generated file to the fsg-gobbler/tests directory on S3
    #s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    #s3.upload_file('./large_file', 'fsg-gobbler', 'tests/large_file')

    # Get md5 hash of the uploaded file from S3
    
    

test_large_upload_progress()
