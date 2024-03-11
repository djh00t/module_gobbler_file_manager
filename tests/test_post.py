# test_post.py
"""
# Post File Tests

This module contains pytest unit tests for the `post_file` function from the
`klingon_file_manager.post` package. It tests various scenarios for posting
content to both local file systems and AWS S3 storage.

Scenarios include:
    - successful posts
    - posts with empty content
    - posts with binary content
    - posts that should fail due to incorrect paths
    - posts that should fail due to permissions
    - posts that should fail due to MD5 checksum mismatches
    - posts that have additional metadata
    - S3 authentication failures
    - S3 invalid bucket name failures

"""
import pytest
from klingon_file_manager import post_file, get_md5_hash, get_md5_hash_filename
import os
import hashlib
import logging
import boto3


def test_post_to_local_success():
    """
    # Post to Local Success
    Tests the successful posting of text content to a local file path using the
    `klingon_file_manager.utils` `post_file` function.
    """

    # Define test parameters
    path = "/tmp/test.txt"
    content = "test_post_to_local_success"
    # Call the post_file function
    result = post_file(path, content)
    print(result)
    # Add assertions to check the result
    assert result["status"] == 200
    assert result["message"] == "File written successfully."


def test_post_to_s3_success():
    """
    # Post to S3 Success
    Test the successful posting of content to an S3 bucket. This function verifies that the `post_file` function
    can write text content to an S3 path and return a success message indicating the successful write operation to S3.
    """

    # Define test parameters
    aws_s3_bucket_name =  os.environ.get("AWS_S3_BUCKET_NAME")
    path = f"s3://{aws_s3_bucket_name}/development/unit-tests/test.txt"
    content = "test_post_to_s3_success"
    # Call the post_file function
    result = post_file(path, content)
    # Add assertions to check the result
    assert result["status"] == 200
    assert result["message"] == "File written successfully to S3."


def test_post_to_s3_failure():
    """
    # Post to S3 Failure
    Tests the failure of posting to an S3 bucket with intentionally incorrect content.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")
    path = f"s3://{aws_s3_bucket_name}-fail/development/unit-tests/failfile.txt"
    content = "test_post_to_s3_failure"
    # Call the post_file function with intentionally incorrect content
    result = post_file(path, "Incorrect content")
    # Add assertions to check the result
    assert result["status"] == 500
    assert "The specified bucket does not exist" in result["message"]


def test_post_to_local_failure():
    """
    # Post to Local Failure
    Tests the failure of posting content to a non-existent local directory path.
    """
    # Define test parameters
    path = "/tmp/"  # Replace with an actual local directory path
    content = "test_post_to_local_failure"  # Replace with the content you want to post
    # Call the post_file function with a path that does not exist
    result = post_file(path, content)
    # Add assertions to check the result
    assert result["status"] == 500  # Assuming it fails and returns a 500 status code
    assert "Failed to post file" in result["message"]  # Check for an error message


def test_post_empty_content():
    """
    # Post Empty Content
    Tests posting an empty string to an S3 bucket and expects successful completion.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    path = f"s3://{aws_s3_bucket_name}/development/unit-tests/empty_file.txt"  # Use a valid S3 path
    empty_content = ""  # Empty content
    # Call the post_file function with empty content
    result = post_file(path, empty_content)
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message


def test_post_binary_content():
    """
    # Post Binary Content
    Tests posting binary content to an S3 bucket and expects successful completion.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    path = f"s3://{aws_s3_bucket_name}/development/unit-tests/binary_file.bin"  # Use a valid S3 path
    binary_content = b'\x01\x02\x03\x04\x05'  # Binary content
    # Call the post_file function with binary content
    result = post_file(path, binary_content)
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message


def test_post_invalid_md5():
    """
    # Post Invalid MD5
    Tests posting content to an S3 bucket with an invalid MD5 hash provided.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    path = f"s3://{aws_s3_bucket_name}/development/unit-tests/md5_mismatch.txt"  # Use a valid S3 path
    content = "test_post_invalid_md5"  # Replace with the content you want to post
    invalid_md5 = "invalid_md5_hash"  # Provide an invalid MD5 hash
    # Call the post_file function with an invalid MD5 hash
    result = post_file(path, content, md5=invalid_md5,debug=True)
    print(result)
    # Add assertions to check the result
    assert result["status"] == 409  # Assuming it fails due to MD5 mismatch and returns a 409 status code
    assert "Conflict - Provided MD5 does not match calculated MD5." in result["message"]  # Check for an error message


def test_post_with_metadata():
    """
    # Post with Metadata
    Tests posting content with custom metadata to an S3 bucket and verifies the metadata persistence.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    s3_path = f"s3://{aws_s3_bucket_name}/development/unit-tests/file_with_metadata.txt"  # Use a valid S3 path
    content = "test_post_with_metadata"  # Replace with the content you want to post
    metadata = {"custom_key": "custom_value"}  # Additional metadata
    # Call the post_file function with additional metadata
    result = post_file(s3_path, content, metadata=metadata)
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message
    # Retrieve metadata from the S3 object
    s3 = boto3.resource('s3')
    bucket_name, object_key = s3_path[5:].split("/", 1)
    s3_object = s3.Object(bucket_name, object_key)
    fetched_metadata = s3_object.metadata
    # Make sure key value pairs from metadata are present in the fetched
    # metadata. Note that the fetched metadata will also contain some
    # additional key value pairs that are not present in the metadata
    # dictionary.
    for key, value in metadata.items():
        assert fetched_metadata.get(key) == value

def test_post_to_s3_authentication_failure():
    """
    # Post to S3 Authentication Failure
    Tests the posting to an S3 bucket with authentication issues and expects a failure.
    """
    # Define test parameters
    s3_path = "s3://invalid-bucket/development/unit-tests/test.txt"  # Use an invalid S3 path
    content = "test_post_to_s3_authentication_failure"  # Replace with the content you want to post
    # Call the post_file function with an invalid S3 path
    result = post_file(s3_path, content)
    # Add assertions to check the result
    assert result["status"] == 500
    assert "An error occurred while posting the file to S3: An error occurred (AccessDenied) when calling the PutObject operation: Access Denied" in result["message"]
    

def test_post_to_local_directory_not_found():
    """
    # Post to Local Directory Not Found
    Tests the failure of posting content to a local path that is non-existent.
    """
    # Define test parameters
    invalid_local_path = "/non_existent_directory/test.txt"  # Use an invalid local directory path
    content = "test_post_to_local_directory_not_found"  # Replace with the content you want to post
    # Call the post_file function with an invalid local path
    result = post_file(invalid_local_path, content)
    # Add assertions to check the result
    assert result["status"] == 500  # Assuming it fails due to the directory not found and returns a 500 status code
    assert "Failed to post file" in result["message"]  # Check for an error message


def test_post_to_s3_with_manual_md5():
    """
    # Post to S3 with manual MD5
    Tests posting content to an S3 bucket with a correct MD5 hash provided.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")
    path = f"s3://{aws_s3_bucket_name}/development/unit-tests/file_with_md5.txt"
    content = "test_post_to_s3_with_manual_md5"
    src_md5 = get_md5_hash(content)  # Calculate the MD5 hash
    # Call the post_file function with MD5 hash
    result = post_file(path=path, content=content, md5=src_md5)
    # Gather the MD5 hash from the result
    post_md5 = result["md5"]
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message
    assert result["md5"] == src_md5  # Check that the MD5 hash is returned in the result
    # Retrieve metadata from S3
    dst_md5 = get_md5_hash_filename(path)
    # Add an assertion to compare the stored MD5 hash with the calculated MD5 hash
    assert src_md5 == post_md5 == dst_md5, f"MD5 does not match the expected value. Expected: src_md5: {src_md5} post_md5: {src_md5} dst_md5: {src_md5}, Got: src_md5: {src_md5} post_md5: {post_md5} dst_md5: {dst_md5}"


def test_post_to_s3_with_incorrect_md5():
    """
    # Post to S3 with Incorrect MD5
    Tests posting content to an S3 bucket with an incorrect MD5 hash and expects a checksum mismatch error.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    s3_path = f"s3://{aws_s3_bucket_name}/development/unit-tests/file_with_incorrect_md5.txt"  # Use a valid S3 path
    content = "test_post_to_s3_with_incorrect_md5"  # Replace with the content you want to post
    md5_hash = "incorrect_md5_hash"  # Provide an incorrect MD5 hash
    # Call the post_file function with incorrect MD5 hash
    result = post_file(s3_path, content, md5=md5_hash)
    # Add assertions to check the result
    assert result["status"] == 409  # Assuming it fails due to MD5 mismatch and returns a 400 status code
    assert "Conflict - Provided MD5 does not match calculated MD5." in result["message"]  # Check for an error message


def test_post_to_local_non_existent_directory():
    """
    # Post to Local Non-Existent Directory
    Tests the failure of posting content to a local directory that does not exist.
    """
    # Define test parameters
    path = "/non_existent_directory/test.txt"  # Use a path that does not exist
    content = "test_post_to_local_non_existent_directory"  # Replace with the content you want to post
    # Call the post_file function with a path that does not exist
    result = post_file(path, content)
    # Add assertions to check the result
    assert result["status"] == 500  # Assuming it fails due to a non-existent directory and returns a 500 status code
    assert "Failed to post file" in result["message"]  # Check for an error message

def test_post_to_s3_invalid_bucket():
    """
    # Post to S3 Invalid Bucket
    Tests the failure of posting content to an invalid or inaccessible S3 bucket.
    """
    # Define test parameters
    aws_s3_bucket_name = "invalid-bucket-name"  # Use an invalid or inaccessible bucket name
    s3_path = f"s3://{aws_s3_bucket_name}/development/unit-tests/invalid_bucket_file.txt"
    content = "test_post_to_s3_invalid_bucket"  # Replace with the content you want to post
    # Call the post_file function with an invalid bucket name
    result = post_file(s3_path, content)
    # Add assertions to check the result
    assert result["status"] == 500
    assert "Access Denied" in result["message"]

def test_post_to_s3_create_path():
    """
    # Post to S3 Create Path
    Tests posting content to an S3 bucket with a non-existent path, expecting the path to be created.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    new_s3_path = f"s3://{aws_s3_bucket_name}/development/unit-tests/non_existent_path/created_file.txt"
    content = "test_post_to_s3_create_path"  # Replace with the content you want to post
    # Call the post_file function with a path that includes a non-existent path
    result = post_file(new_s3_path, content)
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message

def test_post_to_s3_with_auto_md5():
    """
    # Post to S3 with dynamically generated MD5
    Tests posting content to an S3 bucket with a dynamically generated correct MD5 hash.
    """
    # Define test parameters
    aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")  # Get the S3 bucket name from environment variable
    s3_path = f"s3://{aws_s3_bucket_name}/development/unit-tests/md5_file.txt"
    content = "test_post_to_s3_with_auto_md5"  # Replace with the content you want to post
    # Calculate MD5 hash of the content
    md5_hash = hashlib.md5(content.encode()).hexdigest()
    # Call the post_file function with dynamically generated MD5 hash
    result = post_file(s3_path, content, md5=md5_hash)
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully to S3." in result["message"]  # Check for a success message

def test_post_to_local_with_md5():
    """
    # Post to Local with MD5
    Tests posting content to a local path with a correct MD5 hash provided.
    """
    # Define test parameters
    local_path = "/tmp/md5_file.txt"  # Replace with an actual local directory path
    content = "test_post_to_local_with_md5"  # Replace with the content you want to post
    # Calculate MD5 hash of the content
    md5_hash = hashlib.md5(content.encode()).hexdigest()
    # Call the post_file function with dynamically generated MD5 hash
    result = post_file(local_path, content, md5=md5_hash)
    # Add assertions to check the result
    assert result["status"] == 200  # Assuming it succeeds and returns a 200 status code
    assert "File written successfully." in result["message"]  # Check for a success message


# Run the test with pytest
if __name__ == "__main__":
    pytest.main()
