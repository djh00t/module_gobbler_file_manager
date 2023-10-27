# read.py
import os
import boto3
from typing import Union, Dict
from .utils import get_aws_credentials, is_binary_file, ProgressPercentage


def read_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    Reads a file from a given path, which can be either a local file or an S3 object.
    
    Args:
        path (str): The path of the file to read. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        
    Returns:
        dict: A dictionary containing the status of the read operation with the following schema:
            {
                "status": int,           # HTTP-like status code (e.g., 200 for success, 500 for failure)
                "message": str,          # Message describing the outcome
                "content": Union[str, bytes],  # The actual file content
                "binary": bool,          # Flag indicating if the content is binary
                "debug": Dict[str, str]  # Debug information (only included if 'debug' flag is True)
            }
    """
    try:
        debug_info = {}
        
        if path.startswith("s3://"):
            AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
            AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
            # Read from S3 if the path is an S3 URI
            if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
                aws_credentials = get_aws_credentials()
                if aws_credentials["status"] != 200:
                    return {
                        "status": 403,
                        "message": "AWS credentials not found",
                        "content": None,
                        "is_binary": None,
                        "debug": {"error": "AWS credentials not found"},
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

            # Initialize S3 client with credentials
            s3 = boto3.client(
                "s3"
            )

            try:
                # Read the file from S3 with progress callback
                s3 = boto3.resource('s3')
                s3_object = s3.Object(bucket_name, key)
                file_size = s3_object.content_length
                progress = ProgressPercentage(file_size)
                s3.download_file(bucket_name, key, '/tmp/temp_file', Callback=progress)
                with open('/tmp/temp_file', 'rb') as file:
                    content = file.read()
                os.remove('/tmp/temp_file')
                is_binary = True  # S3 returns bytes
                return {
                    "status": 200,
                    "message": "File read successfully from S3.",
                    "content": content,
                    "binary": is_binary,
                    "debug": debug_info,
                }
            except Exception as exception:
                debug_info["exception"] = str(exception)
                if debug:
                    return {
                        "status": 500,
                        "message": f"Failed to read file from S3: {str(exception)}",
                        "content": None,
                        "is_binary": None,
                        "debug": debug_info,
                    }
                return {
                    "status": 500,
                    "message": "Failed to read file from S3.",
                    "content": None,
                    "is_binary": None,
                    "debug": debug_info,
                }
        else:
            # Read from the local file system
            with open(path, "rb") as file:
                content = file.read()

            # Determine if the file is binary or text
            is_binary = is_binary_file(content)

            return {
                "status": 200,
                "message": "File read successfully.",
                "content": content,
                "binary": is_binary,
                "debug": debug_info,
            }
    except Exception as exception:
        debug_info["exception"] = str(exception)
        if debug:
            return {
                "status": 500,
                "message": f"Failed to read file: {str(exception)}",
                "content": None,
                "binary": None,
                "debug": debug_info,
            }
        return {
            "status": 500,
            "message": "Failed to read file.",
            "content": None,
            "binary": None,
            "debug": debug_info,
        }