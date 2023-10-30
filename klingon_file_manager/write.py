# write.py
import io
import os
import boto3
import hashlib
from typing import Union, Dict, Optional, Callable
from .utils import get_aws_credentials, is_binary_file
import hashlib


def write_file(path: str, content: Union[str, bytes], md5: Optional[str] = None, metadata: Optional[Dict[str, str]] = None, debug: bool = False):
    """
    Writes content to a file at a given path, which can be either a local file or an S3 object.

    Args:
        path (str): The path where the file should be written. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        content (Union[str, bytes]): The content to write to the file.
        md5 (Optional[str]): The MD5 hash of the content, used to verify the integrity of the data. Defaults to None.
        metadata (Optional[Dict[str, str]]): Additional metadata to include with the file. Defaults to None.
        debug (bool): Flag to enable debugging. Defaults to False.

    Returns:
        dict: A dictionary containing the status of the write operation with the following schema:
            {
                "status": int,          # HTTP-like status code (e.g., 200 for success, 500 for failure)
                "message": str,         # Message describing the outcome
                "md5": str,             # The MD5 hash of the written file (only included if status is 200)
                "debug": Dict[str, str] # Debug information (only included if 'debug' flag is True)
            }
    """
    try:
        debug_info = {}
        # Check if the path is an S3 URI
        if path.startswith("s3://"):
            # Get AWS credentials
            AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
            AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
            # Write to S3 if the path is an S3 URI
            if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
                aws_credentials = get_aws_credentials()
                if aws_credentials["status"] != 200:
                    return {
                        "status": 403,
                        "message": "AWS credentials not found",
                        "content": None,
                        "is_binary": None,
                        "debug": {"error": "AWS credentials not found"} if debug else {},
                    }
                AWS_ACCESS_KEY_ID = aws_credentials["credentials"]["AWS_ACCESS_KEY_ID"]
                AWS_SECRET_ACCESS_KEY = aws_credentials["credentials"]["AWS_SECRET_ACCESS_KEY"]

            # Extract S3 bucket and key from the path
            s3_uri_parts = path[5:].split("/", 1)
            bucket_name = s3_uri_parts[0]
            key = s3_uri_parts[1]

            # Add s3_uri_parts, bucket_name, and key to debug_info
            debug_info["s3_uri_parts"] = s3_uri_parts
            debug_info["bucket_name"] = bucket_name
            debug_info["key"] = key
            
            try:
                # Initialize S3 resource
                s3 = boto3.resource('s3')
                
                # Get file size in bytes
                file_size = len(content)
                
                # Set file name from key
                file_name = os.path.basename(key)

                # MD5 handler
                if md5:
                    # If the content is not a string or bytes, convert it to a string
                    if not isinstance(content, (str, bytes)):
                        content = str(content)

                    # If the content is a string, encode it to UTF-8 bytes
                    if isinstance(content, str):
                        content = content.encode('utf-8')

                    # Calculate the MD5 hash of the content
                    calculated_md5 = hashlib.md5(content).hexdigest()

                    # If the calculated MD5 does not match the provided MD5, return an error
                    if calculated_md5 != md5:
                        return {
                            "status": 400,
                            "message": "Provided MD5 does not match calculated MD5.",
                            "debug": debug_info if debug else {},
                        }

                    # Ensure metadata is a dictionary
                    if metadata is None:
                        metadata = {}

                    # Ensure metadata is a dictionary
                    if metadata is None:
                        metadata = {}

                    # Store the calculated MD5 in the metadata
                    metadata["md5"] = calculated_md5

                # Determine if the content is binary or text
                is_binary = is_binary_file(content)

                # Convert content into binary if it's a string
                if isinstance(content, str):
                    content = content.encode('utf-8')

                # Initialize S3 client
                s3_client = boto3.client('s3')

                # Create a BytesIO object from the content
                with io.BytesIO(content) as f:
                    # Calculate the MD5 hash of the content and store it in the metadata
                    md5_hash = hashlib.md5(content).hexdigest()
                    metadata['ContentMD5'] = md5_hash

                    # Convert all metadata values to strings
                    metadata_str = {k: str(v) for k, v in metadata.items()}

                    # Upload the file to S3
                    s3_client.upload_fileobj(
                        Fileobj=f,
                        Bucket=bucket_name,
                        Key=key,
                        ExtraArgs={'Metadata': metadata_str}
                    )

                return {
                    "status": 200,
                    "message": "File written successfully to S3.",
                    "md5": md5_hash,
                    "debug": debug_info,
                    "content": content[:10] if isinstance(content, bytes) else content,
                }
            except Exception as exception:
                debug_info["exception"] = str(exception)
                if debug:
                    return {
                        "status": 500,
                        "message": f"Failed to write file to S3: {str(exception)}",
                        "debug": debug_info if debug else {},
                    }
                return {
                    "status": 500,
                    "message": "Failed to write file to S3.",
                    "debug": debug_info if debug else {},
                }
        else:
            # Write to the local file system
            with open(path, "wb" if isinstance(content, bytes) else "w") as file:
                debug_info['write_start'] = f"Starting write with content={content}"
                file.write(content)

            return {
                "status": 200,
                "message": "File written successfully.",
                "debug": debug_info,
            }
    except Exception as exception:
        debug_info["exception"] = str(exception)
        if debug:
            return {
                "status": 500,
                "message": f"Failed to write file: {str(exception)}",
                "debug": debug_info if debug else {},
            }
        return {
            "status": 500,
            "message": "Failed to write file.",
            "debug": debug_info if debug else {},
        }
