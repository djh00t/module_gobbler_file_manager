from klingon_file_manager import manage_file
from klingon_file_manager.utils import ProgressPercentage
import base64
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


def test_large_upload_progress():
    # Set test files name
    file_name = './large_file'
    
    # Generate a 100MB file using dd command
    subprocess.run(['dd', 'if=/dev/zero', 'of='+file_name, 'bs=1M', 'count=100'])

    # Get md5 hash of the generated file
    with open(file_name, 'rb') as f:
        # Read the file content
        file_content = f.read()
        
        # Get the md5 hash of the file content
        md5_hash = hashlib.md5(file_content).digest()

        # Encode the md5 hash of the file content to base64 to send to S3
        contents_md5 = base64.b64encode(md5_hash).decode('utf-8')
        
        # Convert md5_hash to a hex string for metadata and logging
        md5_hash_hex = md5_hash.hex()

        # Get & announce the file size in bytes
        file_size = len(file_content)

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


    # Create metadata
    metadata = {
        "md5": md5_hash_hex,
        "filesize": file_size
    }

    # Upload the file with progress callback and dump the full response from
    # klingon-file-manager to console
    result = manage_file(
        action='post',
        path="s3://fsg-gobbler/tests/"+file_name,
        content=file_content,
        md5=md5_hash_hex,
        metadata=metadata,
        progress=true,
        debug=False
    )

    # Remove the test file
    os.remove(file_name)

    print(f"Upload result: {result}")

test_large_upload_progress()
