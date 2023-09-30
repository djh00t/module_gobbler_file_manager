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

# Generate a 100 word string of lorem ipsum text
#test_txt_content = lorem.text()
test_txt_content = "Hello World!"

# Test Files - get
test_txt_get_local = 'tests/test_get_txt_file.txt'
test_bin_get_local = 'tests/test_get_bin_file.wav'
test_txt_get_s3 = 's3://fsg-gobbler/fsg-test/test_get_txt_file.txt'
test_bin_get_s3 = 's3://fsg-gobbler/fsg-test/test_get_bin_file.wav'

# Test Files - post
test_txt_post_local = 'tests/test_post_txt_file.txt'
test_bin_post_local = 'tests/test_post_bin_file.wav'
test_txt_post_s3 = 's3://fsg-gobbler/fsg-test/test_post_txt_file.txt'
test_bin_post_s3 = 's3://fsg-gobbler/fsg-test/test_post_bin_file.wav'


# Create test files
def setup_test_files():
    ##
    ## GET TEST FILES
    ##
    # Create local test txt file
    with open(test_txt_get_local, 'w') as f:
        f.write(test_txt_content)
    # Make sure that the test_txt_get_local file was created
    assert os.path.exists(test_txt_get_local)
    # Create local test binary file
    with open(test_bin_get_local, 'wb') as f:
        f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    # Make sure that the test_bin_get_local file was created
    assert os.path.exists(test_bin_get_local)
    # Upload test_txt_get_local file to test_txt_get_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_txt_get_local, 'fsg-gobbler', 'fsg-test/test_get_txt_file.txt')
    # Make sure that the test_txt_get_s3 file was created
    assert s3.Object('fsg-gobbler', 'fsg-test/test_get_txt_file.txt').content_length > 0
    # Upload test_bin_get_local file to test_bin_get_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_bin_get_local, 'fsg-gobbler', 'fsg-test/test_get_bin_file.wav')
    # Make sure that the test_bin_get_s3 file was created
    assert s3.Object('fsg-gobbler', 'fsg-test/test_get_bin_file.wav').content_length > 0

    ##
    ## POST TEST FILES
    ##
    # Create local test txt file
    with open(test_txt_post_local, 'w') as f:
        f.write(test_txt_content)
    # Create local test binary file
    with open(test_bin_post_local, 'wb') as f:
        f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    # Upload test_txt_post_local file to test_txt_post_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_txt_post_local, 'fsg-gobbler', 'fsg-test/test_post_txt_file.txt')
    # Upload test_bin_post_local file to test_bin_post_s3 location
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(test_bin_post_local, 'fsg-gobbler', 'fsg-test/test_post_bin_file.wav')

def teardown_test_files():
    ##
    ## GET TEST FILES
    ##
    # Delete local test txt file
    os.remove(test_txt_get_local)
    # Delete local test binary file
    os.remove(test_bin_get_local)
    # Delete test_txt_get_s3 file
    s3 = boto3.resource('s3')
    s3.Object('fsg-gobbler', 'fsg-test/test_get_txt_file.txt').delete()
    # Delete test_bin_get_s3 file
    s3 = boto3.resource('s3')
    s3.Object('fsg-gobbler', 'fsg-test/test_get_bin_file.wav').delete()

    ##
    ## POST TEST FILES
    ##
    # Delete local test txt file
    os.remove(test_txt_post_local)
    # Delete local test binary file
    os.remove(test_bin_post_local)
    # Delete test_txt_post_s3 file
    s3 = boto3.resource('s3')
    s3.Object('fsg-gobbler', 'fsg-test/test_post_txt_file.txt').delete()
    # Delete test_bin_post_s3 file
    s3 = boto3.resource('s3')
    s3.Object('fsg-gobbler', 'fsg-test/test_post_bin_file.wav').delete()

# Setup test files
setup_test_files()

# Test 1 - get local text file
def test_get_local_txt_file():
    result = manage_file('get', None, test_txt_get_local, False, True)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['file'].decode() == test_txt_content
    assert result['path'] == test_txt_get_local
    assert result['binary'] == False
    assert result['debug'] == {}




# Sleep for 5 seconds
time.sleep(5)

# Cleanup test files
#teardown_test_files()
