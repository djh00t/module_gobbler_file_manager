import pytest
from gobbler_file_manager import manage_file
from gobbler_file_manager.utils import get_aws_credentials
import lorem
import logging

# Test text content
test_txt_content=lorem.text()

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

# Use the get_aws_credentials function to get AWS credentials returned as a
# json object containing the following keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
aws_credentials = get_aws_credentials()
aws_access_key_id = aws_credentials['credentials']['AWS_ACCESS_KEY_ID']
aws_secret_access_key = aws_credentials['credentials']['AWS_SECRET_ACCESS_KEY']

# Test 1 - get local text file
def test_get_local_txt_file():
    result = manage_file('get', None, test_txt_get_local, False)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['file'] == test_txt_content
    assert result['path'] == test_txt_get_local
    assert result['binary'] == False
    assert result['debug'] == {}
    
