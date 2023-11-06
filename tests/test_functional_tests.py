import os
from klingon_file_manager import manage_file
import lorem
import boto3

AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

# Set s3 bucket name
s3_bucket_name = AWS_S3_BUCKET_NAME

# Test Files - get
test_txt_get = 'tests/testfiles/test_get_txt_file.txt'
test_bin_get = 'tests/testfiles/test_get_bin_file.wav'

# Test Files - post
test_txt_post = 'tests/testfiles/test_post_txt_file.txt'
test_bin_post = 'tests/testfiles/test_post_bin_file.wav'

def cleanup_previous_run():
    # Remove the test_txt_get file if it exists, otherwise skip
    if os.path.exists(test_txt_get):
        os.remove(test_txt_get)
    # Remove the test_bin_get file if it exists, otherwise skip
    if os.path.exists(test_bin_get):
        os.remove(test_bin_get)
    # Remove the test_txt_post file if it exists, otherwise skip
    if os.path.exists(test_txt_post):
        os.remove(test_txt_post)
    # Remove the test_bin_post file if it exists, otherwise skip
    if os.path.exists(test_bin_post):
        os.remove(test_bin_post)
    # Remove tests/testfiles/1kb.bin if it exists, otherwise skip
    if os.path.exists("tests/testfiles/1kb.bin"):
        os.remove("tests/testfiles/1kb.bin")
    
cleanup_previous_run()

# Generate a 100 word string of lorem ipsum text
test_txt_content = lorem.text()

# Make sure tests/testfiles directory exists
if not os.path.exists("tests/testfiles"):
    os.mkdir("tests/testfiles")

# Create a 1KB test binary file
with open("tests/testfiles/1kb.bin", "wb") as f:
    f.write(os.urandom(1024))
    
# Read the 1KB test binary file into test_bin_content
test_bin_content = open("tests/testfiles/1kb.bin", "rb").read()

# Hard link the 1KB test binary file to the test_bin_get file
os.link("tests/testfiles/1kb.bin", test_bin_get)

# Hard link the 1KB test binary file to the test_bin_post file
os.link("tests/testfiles/1kb.bin", test_bin_post)


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


# Create test files
def test_setup_test_files():
    ##
    ## GET TEST FILES
    ##
    # Create local test txt file
    with open(test_txt_get, 'w') as f:
        f.write(test_txt_content)
    # Make sure that the test_txt_get file was created
    assert os.path.exists(test_txt_get)
    # Create local test get binary file by symlinking to the 1kb.bin file if it
    # doesn't already exist
    if not os.path.exists(test_bin_get):
        os.copy('tests/testfiles/1kb.bin', test_bin_get)
    # Create local test post binary file by symlinking to the 1kb.bin file if it
    # doesn't already exist
    if not os.path.exists(test_bin_post):
        os.copy('tests/testfiles/1kb.bin', test_bin_post)
    # Make sure that the test_bin_get file was created
    assert os.path.exists(test_bin_get)
    # Make sure that the test_bin_post file was created
    assert os.path.exists(test_bin_post)
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


# Test 1 - get local text file
def test_get_local_txt_file():
    result = manage_file('get', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] is False
    # Additional check: Read the file to make sure content was written
    # correctly
    with open(test_txt_get, 'r') as file:
        assert file.read() == test_txt_content


# Test 2 - get local binary file
def test_get_local_bin_file():
    result = manage_file('get', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'] == test_bin_content
    assert result['path'] == test_bin_get
    assert result['binary'] is True
    # Additional check: Read the file to make sure content was written
    # correctly
    with open(test_bin_get, 'rb') as file:
        assert file.read() == test_bin_content


# Test 3 - get s3 text file
def test_get_s3_txt_file():
    result = manage_file('get', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'].decode() == test_txt_content
    assert result['path'] == test_txt_get
    assert result['binary'] is False

# Test 4 - get s3 binary file
def test_get_s3_bin_file():
    result = manage_file('get', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'get'
    assert result['content'] == test_bin_content
    assert result['path'] == test_bin_get
    assert result['binary'] is True

# Test 5 - post local text file
def test_post_local_txt_file():
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

# Test 6 - post local binary file
def test_post_local_bin_file():
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

# Test 7 - post s3 text file
def test_post_s3_txt_file():
    result = manage_file('post', "s3://"+s3_bucket_name+"/"+test_txt_post, test_txt_content)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == "s3://"+s3_bucket_name+"/"+test_txt_post
    assert result['binary'] is False
    # Additional check: Read the file from s3 to make sure content was written
    # correctly
    validate = manage_file('get', "s3://"+s3_bucket_name+"/"+test_txt_post, None)
    print(validate)
    assert validate['status'] == 200
    assert validate['action'] == 'get'
    assert validate['content'].decode() == test_txt_content
    assert validate['path'] == "s3://"+s3_bucket_name+"/"+test_txt_post

# Test 8 - post s3 binary file
def test_post_s3_bin_file():
    result = manage_file('post', "s3://"+s3_bucket_name+"/"+test_bin_post, test_bin_content)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'post'
    assert result['path'] == "s3://"+s3_bucket_name+"/"+test_bin_post
    # Additional check: Read the file from s3 to make sure content was written
    # correctly
    validate = manage_file('get', "s3://"+s3_bucket_name+"/"+test_bin_post, None)
    print(validate)
    assert validate['status'] == 200
    assert validate['action'] == 'get'
    assert validate['content'] == test_bin_content
    assert validate['path'] == "s3://"+s3_bucket_name+"/"+test_bin_post

# Test 9 - Test invalid action
def test_invalid_action():
    result = manage_file('invalid', None , None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'invalid'

# Test 10 - Test invalid local path
def test_get_invalid_local_path():
    result = manage_file('get', './nonexistent.txt' , None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'get'

# Test 11 - Test invalid S3 path
def test_get_invalid_s3_path():
    result = manage_file('get', 's3://'+s3_bucket_name+'/nonexistent.txt' , None)
    print(result)
    assert result['status'] == 500
    assert result['action'] == 'get'

# Test 12 - Test aws credentials
def test_check_aws_access_key_id():
    assert AWS_ACCESS_KEY_ID is not None

# Test 13 - Test aws credentials
def test_check_aws_secret_access_key():
    assert AWS_SECRET_ACCESS_KEY is not None

# Test 14 - delete local text files
def test_delete_local_test_txt_post_file():
    # Make sure that the test_txt_post file was created
    assert os.path.exists(test_txt_post)
    # Now, delete the local test_txt_post file
    result = manage_file('delete', test_txt_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_txt_post
    # Make sure that the test_txt_post file was deleted
    assert not os.path.exists(test_txt_post)
    # Add a delay to ensure the file system has time to update
    import time
    time.sleep(1)
    assert not os.path.exists(test_txt_post)

# Test 15 - delete local text files
def test_delete_local_test_txt_get_file():
    # Make sure that the test_txt_get file was created
    assert os.path.exists(test_txt_get)
    # Now, delete the local test_txt_get file
    result = manage_file('delete', test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_txt_get
    # Make sure that the test_txt_get file was deleted
    assert not os.path.exists(test_txt_get)

# Test 16 - delete local binary file
def test_delete_local_test_bin_post_file():
    # Make sure that the test_bin_post file was created
    assert os.path.exists(test_bin_post)
    # Now, delete the local test_bin_post file
    result = manage_file('delete', test_bin_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_bin_post
    # Make sure that the test_bin_post file was deleted
    assert not os.path.exists(test_bin_post)

# Test 17 - delete local binary file
def test_delete_local_test_bin_get_file():
    # Make sure that the test_bin_get file was created
    assert os.path.exists(test_bin_get)
    # Now, delete the local test_bin_get file
    result = manage_file('delete', test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == test_bin_get
    # Make sure that the test_bin_get file was deleted
    assert not os.path.exists(test_bin_get)

# Test 18 - delete s3 test_txt_post file
def test_delete_s3_test_txt_post_file():
    # Now, delete the s3 text file
    result = manage_file('delete', "s3://"+s3_bucket_name+"/"+test_txt_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == "s3://"+s3_bucket_name+"/"+test_txt_post

# Test 19 - delete s3 test_bin_post file
def test_delete_s3_test_bin_post_file():
    # Now, delete the s3 test_bin_post file
    result = manage_file('delete', "s3://"+s3_bucket_name+"/"+test_bin_post, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == "s3://"+s3_bucket_name+"/"+test_bin_post

# Test 20 - delete s3 test_txt_get file
def test_delete_s3_test_txt_get_file():
    # Now, delete the s3 test_txt_get file
    result = manage_file('delete', "s3://"+s3_bucket_name+"/"+test_txt_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == "s3://"+s3_bucket_name+"/"+test_txt_get
    
# Test 21 - delete s3 test_bin_get file
def test_delete_s3_test_bin_get_file():
    # Now, delete the s3 test_bin_get file
    result = manage_file('delete', "s3://"+s3_bucket_name+"/"+test_bin_get, None)
    print(result)
    assert result['status'] == 200
    assert result['action'] == 'delete'
    assert result['path'] == "s3://"+s3_bucket_name+"/"+test_bin_get

def test_teardown_test_files():
    # Remove the test_bin_get file if it exists, otherwise skip
    if os.path.exists(test_bin_get):
        os.remove(test_bin_get)
    # Remove the test_bin_post file if it exists, otherwise skip
    if os.path.exists(test_bin_post):
        os.remove(test_bin_post)
    # Remove the 1kb.bin file if it exists, otherwise skip
    if os.path.exists("tests/testfiles/1kb.bin"):
        os.remove("tests/testfiles/1kb.bin")
    # Remove the test_txt_get file if it exists, otherwise skip
    if os.path.exists(test_txt_get):
        os.remove(test_txt_get)
    # Remove the test_txt_post file if it exists, otherwise skip
    if os.path.exists(test_txt_post):
        os.remove(test_txt_post)
    # Remove the tests/testfiles directory if it exists, otherwise skip
    if os.path.exists("tests/testfiles"):
        os.rmdir("tests/testfiles")