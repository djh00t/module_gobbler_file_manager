import time
import os
import pytest
from gobbler_file_manager import manage_file
from gobbler_file_manager.utils import get_aws_credentials
import lorem
import logging
import boto3

# Use the get_aws_credentials function to get AWS credentials returned as a
# json object containing the following keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
aws_credentials = get_aws_credentials()
# Make sure we got a json object with a credentials object in it
assert 'credentials' in aws_credentials
# Get the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY values from the
# credentials object.
aws_access_key_id = aws_credentials['credentials']['AWS_ACCESS_KEY_ID']
aws_secret_access_key = aws_credentials['credentials']['AWS_SECRET_ACCESS_KEY']
# Make sure that we got the AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY values
# from the credentials object.
assert aws_access_key_id is not None
assert aws_secret_access_key is not None
# Set s3 bucket name
s3_bucket_name = 'fsg-gobbler'

# Generate a 100 word string of lorem ipsum text
#test_txt_content = lorem.text()
test_txt_content = "Hello World!"
test_bin_content = b'\x00\x00\x00\x00\x00\x00\x00\x00'

# Test Files - get
test_txt_get = 'tests/test_get_txt_file.txt'
test_bin_get = 'tests/test_get_bin_file.wav'

# Test Files - post
test_txt_post = 'tests/test_post_txt_file.txt'
test_bin_post = 'tests/test_post_bin_file.wav'


# Make sure that a file exists at a given s3 path and contains the expected
# content.
def assert_s3_file_content(path, content):
    s3 = boto3.resource('s3')
    obj = s3.Object(s3_bucket_name, path)
    assert obj.content_length > 0
    actual_content = obj.get()['Body'].read().decode()
    print(f"Actual content: {actual_content}")
    print(f"Expected content: {content}")
    assert actual_content == content

# Create test files
def setup_test_files():
    ##
    ## GET TEST FILES
    ##
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
    assert assert_s3_file_content(test_txt_get, test_txt_content)
    
    # Upload test_bin_get file to test_bin_get_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_bin_get, s3_bucket_name, test_bin_get)
    # Make sure that the test_bin_get_s3 file was created
    assert assert_s3_file_content(test_bin_get, test_bin_content)

    ##
    ## POST TEST FILES
    ##
    # Create local test txt file
    with open(test_txt_post, 'w') as f:
        f.write(test_txt_content)
    # Create local test binary file
    with open(test_bin_post, 'wb') as f:
        f.write(test_bin_content)
    # Upload test_txt_post file to test_txt_post_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file( test_txt_post, s3_bucket_name, test_txt_post )
    # Make sure that the test_txt_post_s3 file was created
    assert assert_s3_file_content( "s3://"+s3_bucket_name+"/"+test_txt_post, test_txt_content )
    # Upload test_bin_post file to test_bin_post_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_bin_post, s3_bucket_name, test_bin_post )

def teardown_test_files():
    ##
    ## GET TEST FILES
    ##
    # Delete local test txt file
    os.remove(test_txt_get)
    # Delete local test binary file
    os.remove(test_bin_get)
    # Delete test_txt_get file
    s3 = boto3.resource('s3')
    s3.Object(s3_bucket_name, test_txt_get).delete()
    # Delete test_bin_get_s3 file
    s3 = boto3.resource('s3')
    s3.Object(s3_bucket_name, test_bin_get).delete()

    ##
    ## POST TEST FILES
    ##
    # Delete local test txt file
    os.remove(test_txt_post)
    # Delete local test binary file
    os.remove(test_bin_post)
    # Delete test_txt_post_s3 file
    s3 = boto3.resource('s3')
    s3.Object(s3_bucket_name, 'fsg-test/test_post_txt_file.txt').delete()
    # Delete test_bin_post_s3 file
    s3 = boto3.resource('s3')
    s3.Object(s3_bucket_name, 'fsg-test/test_post_bin_file.wav').delete()


# Setup test files
setup_test_files()

# Test 1 - get local text file
def test_get_local_txt_file():
    result = manage_file('get', None, test_txt_get, False, True)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['file'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] == False
    #assert 'debug' in result
    #assert isinstance(result['debug'], dict)

# Test 2 - get local binary file
def test_get_local_bin_file():
    result = manage_file('get', None, test_bin_get, False, True)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['file'] == b'\x00\x00\x00\x00\x00\x00\x00\x00'
    assert result['path'] == test_bin_get
    assert result['binary'] == True
    #assert 'debug' in result
    #assert isinstance(result['debug'], dict)

# Test 3 - get s3 text file
def test_get_s3_txt_file():
    result = manage_file('get', None, test_txt_get, False, True)
    #print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['file'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] == False
    #assert 'debug' in result
    #assert isinstance(result['debug'], dict)

#test_get_s3_txt_file()

# Sleep for 5 seconds
#time.sleep(5)

# Cleanup test files
#teardown_test_files()
