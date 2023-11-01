import pytest
from klingon_file_manager import post_file, get_s3_metadata, timing_decorator
import os
import hashlib
import logging
import boto3

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

@timing_decorator
def test_post_to_local_success():
    # Define test parameters
    path = "/tmp/test.txt"
    content = "Hello, world!"

    # Debug logging
    if debug_mode:
        logger.debug(f"Posting file to path: {path}")

    # Call the post_file function
    result = post_file(path, content)

    print(result)

    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")

    # Add assertions to check the result
    assert result["status"] == 200
    assert result["message"] == "File written successfully."

@timing_decorator
def test_post_to_s3_success():
    # Define test parameters
    aws_s3_bucket_name =  os.environ.get("AWS_S3_BUCKET_NAME")
    path = f"s3://{aws_s3_bucket_name}/tests/test.txt"
    content = "Hello, S3!"  # Replace with the content you want to post

    # Debug logging
    if debug_mode:
        logger.debug(f"Posting file to S3 path: {path}")

    # Call the post_file function
    result = post_file(path, content)

    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")

    # Add assertions to check the result
    assert result["status"] == 200
    assert result["message"] == "File written successfully to S3."

@timing_decorator
def test_post_to_s3_failure():
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    path = f"s3://{aws_s3_bucket_name}-fail/tests/failfile.txt"  # Use the bucket name in the S3 path
    content = "Hello, S3!"  # Replace with the content you want to post

    # Debug logging
    if debug_mode:
        logger.debug(f"Posting file to S3 path: {path}")

    # Call the post_file function with intentionally incorrect content
    result = post_file(path, "Incorrect content")

    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")

    # Add assertions to check the result
    assert result["status"] == 500  # Assuming it fails and returns a 500 status code
    assert "Failed to post file" in result["message"]  # Check for an error message

@timing_decorator
def test_post_to_local_failure():
    # Define test parameters
    path = "/tmp/"  # Replace with an actual local directory path
    content = "Hello, world!"  # Replace with the content you want to post

    # Debug logging
    if debug_mode:
        logger.debug(f"Posting file to path: {path}")

    # Call the post_file function with a path that does not exist
    result = post_file(path, content)

    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")

    # Add assertions to check the result
    assert result["status"] == 500  # Assuming it fails and returns a 500 status code
    assert "Failed to post file" in result["message"]  # Check for an error message

@timing_decorator
def test_post_empty_content():
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    path = f"s3://{aws_s3_bucket_name}/tests/empty_file.txt"  # Use a valid S3 path
    empty_content = ""  # Empty content
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting empty content to S3 path: {path}")
    
    # Call the post_file function with empty content
    result = post_file(path, empty_content)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message

@timing_decorator
def test_post_binary_content():
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    path = f"s3://{aws_s3_bucket_name}/tests/binary_file.bin"  # Use a valid S3 path
    binary_content = b'\x01\x02\x03\x04\x05'  # Binary content
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting binary content to S3 path: {path}")
    
    # Call the post_file function with binary content
    result = post_file(path, binary_content)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message

@timing_decorator
def test_post_invalid_md5():
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    path = f"s3://{aws_s3_bucket_name}/tests/md5_mismatch.txt"  # Use a valid S3 path
    content = "Hello, S3!"  # Replace with the content you want to post
    invalid_md5 = "invalid_md5_hash"  # Provide an invalid MD5 hash
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting with invalid MD5 hash to S3 path: {path}")
    
    # Call the post_file function with an invalid MD5 hash
    result = post_file(path, content, md5=invalid_md5,debug=True)

    print(result)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 409  # Assuming it fails due to MD5 mismatch and returns a 409 status code
    assert "Conflict - Provided MD5 does not match calculated MD5." in result["message"]  # Check for an error message

@timing_decorator
def test_post_with_metadata():
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    s3_path = f"s3://{aws_s3_bucket_name}/tests/file_with_metadata.txt"  # Use a valid S3 path
    content = "Hello, S3!"  # Replace with the content you want to post
    metadata = {"custom_key": "custom_value"}  # Additional metadata
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting with metadata to S3 path: {s3_path}")
    
    # Call the post_file function with additional metadata
    result = post_file(s3_path, content, metadata=metadata)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message
    
    # Retrieve metadata from the S3 object
    s3 = boto3.resource('s3')
    bucket_name, object_key = s3_path[5:].split("/", 1)
    s3_object = s3.Object(bucket_name, object_key)
    fetched_metadata = s3_object.metadata
    
    # Validate that the fetched metadata matches what was sent
    assert fetched_metadata == metadata

@timing_decorator
def test_post_to_s3_authentication_failure():
    # Define test parameters
    s3_path = "s3://invalid-bucket/tests/test.txt"  # Use an invalid S3 path
    content = "Hello, S3!"  # Replace with the content you want to post
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting to invalid S3 path: {s3_path}")
    
    # Call the post_file function with an invalid S3 path
    result = post_file(s3_path, content)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 500  # Assuming it fails due to authentication error and returns a 500 status code
    assert "Failed to post file" in result["message"]  # Check for an error message
    
@timing_decorator
def test_post_to_local_directory_not_found():
    # Define test parameters
    invalid_local_path = "/non_existent_directory/test.txt"  # Use an invalid local directory path
    content = "Hello, world!"  # Replace with the content you want to post
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting to invalid local path: {invalid_local_path}")
    
    # Call the post_file function with an invalid local path
    result = post_file(invalid_local_path, content)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 500  # Assuming it fails due to the directory not found and returns a 500 status code
    assert "Failed to post file" in result["message"]  # Check for an error message

@timing_decorator
def test_post_to_s3_with_md5():
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    s3_path = f"s3://{aws_s3_bucket_name}/tests/file_with_md5.txt"  # Use a valid S3 path
    content = "Hello, S3!"  # Replace with the content you want to post
    md5_hash = hashlib.md5(content.encode('utf-8')).hexdigest()  # Calculate the MD5 hash
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting with MD5 to S3 path: {s3_path}")
    
    # Call the post_file function with MD5 hash
    result = post_file(s3_path, content, md5=md5_hash)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message
    
    # Retrieve metadata from S3
    metadata = get_s3_metadata(s3_path)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Metadata from S3: {metadata}")
    
    # Add an assertion to compare the stored MD5 hash with the calculated MD5 hash
    assert metadata.get("ContentMD5") == md5_hash

@timing_decorator
def test_post_to_s3_with_incorrect_md5():
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    s3_path = f"s3://{aws_s3_bucket_name}/tests/file_with_md5.txt"  # Use a valid S3 path
    content = "Hello, S3!"  # Replace with the content you want to post
    md5_hash = "incorrect_md5_hash"  # Provide an incorrect MD5 hash
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Posting with incorrect MD5 to S3 path: {s3_path}")
    
    # Call the post_file function with incorrect MD5 hash
    result = post_file(s3_path, content, md5=md5_hash)
    
    # Debug logging
    if debug_mode:
        logger.debug(f"Result: {result}")
    
    # Add assertions to check the result
    assert result["status"] == 409  # Assuming it fails due to MD5 mismatch and returns a 400 status code
    assert "Conflict - Provided MD5 does not match calculated MD5." in result["message"]  # Check for an error message






# Run the test with pytest
if __name__ == "__main__":
    pytest.main()
