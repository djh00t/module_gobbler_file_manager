import pytest
from klingon_file_manager import timing_decorator, get_mime_type, get_aws_credentials, is_binary_file, get_s3_metadata
import os
import logging
import tempfile

# Set up the logger
logger = logging.getLogger(__name__)

# Configure the logger to log to stdout
stream_handler = logging.StreamHandler()  # Create a StreamHandler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Define a log message format
stream_handler.setFormatter(formatter)  # Set the formatter for the handler
logger.addHandler(stream_handler)  # Add the handler to the logger

# Check if DEBUG environment variable is set to "True"
if os.environ.get("DEBUG") == "True":
    logging.basicConfig(level=logging.DEBUG)
    debug_mode = True
else:
    logging.basicConfig(level=logging.INFO)
    debug_mode = False

# Get the AWS S3 bucket name from the environment variable
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

# Test with a local text file
### def test_get_mime_type_local_text_file():
###     with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
###         temp_file.write(b"Hello, world!")
###         file_path = temp_file.name
### 
###     mime_type = get_mime_type(file_path)
###     assert mime_type == "text/plain"

# Test with an S3 file using the AWS_S3_BUCKET_NAME environment variable
def test_get_mime_type_existing_s3_file():
    if AWS_S3_BUCKET_NAME:
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/development/raw/2023/07/[ Moiz]_2549-+61362705460_20230705035512(7873).wav"  # Replace with a valid S3 object key
        metadata = get_s3_metadata(s3_url)
        mime_type = metadata.get("ContentType")
        assert mime_type == "audio/x-wav"

def test_get_mime_type_existing_s3_file_with_md5_metadata():
    if AWS_S3_BUCKET_NAME:
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/tests/perm-files/audio-test.wav"
        metadata = get_s3_metadata(s3_url)
        # Retrieve md5 value from Metadata key in metadata dictionary
        md5_check = metadata.get("Metadata").get("md5")

        print(f"md5: {md5_check}")
        assert md5_check == "f63bbe640a48144acd9b608b5eba4596"

# Test with an S3 file that doesn't exist using the AWS_S3_BUCKET_NAME environment variable
def test_get_mime_type_nonexistent_s3_file():
    if AWS_S3_BUCKET_NAME:
        s3_url = f"s3://{AWS_S3_BUCKET_NAME}/tests/nonexistent-file.jpg"
        mime_type = get_mime_type(s3_url)
        print("===================================================")
        print(mime_type)
        print("===================================================")
        # Assert that there will be a NoSuchKey error
        assert mime_type == "NoSuchKey"

