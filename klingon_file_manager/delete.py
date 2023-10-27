# delete.py
import os
import boto3
from typing import Union, Dict
from .utils import get_aws_credentials

def delete_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    Deletes a file at a given path, which can be either a local file or an S3 object.
    
    Args:
        path (str): The path where the file should be deleted. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        debug (bool, optional): Flag to enable debugging. Defaults to False.

    Returns:
        dict: A dictionary containing the status of the delete operation with the following schema:
            {
                "status": int,          # HTTP-like status code (e.g., 200 for success, 500 for failure)
                "message": str,         # Message describing the outcome
                "debug": Dict[str, str] # Debug information (only included if 'debug' flag is True)
            }
    """
    try:
        debug_info = {}

        if path.startswith("s3://"):
            AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
            AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
            # Delete from S3 if the path is an S3 URI
            if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
                aws_credentials = get_aws_credentials()
                if aws_credentials["status"] != 200:
                    return {
                        "status": 403,
                        "message": "AWS credentials not found",
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
                # Delete the file from S3
                s3.delete_object(Bucket=bucket_name, Key=key)

                return {
                    "status": 200,
                    "message": "File deleted successfully from S3.",
                    "debug": debug_info,
                }
            except Exception as exception:
                debug_info["exception"] = str(exception)
                if debug:
                    return {
                        "status": 500,
                        "message": f"Failed to delete file from S3: {str(exception)}",
                        "debug": debug_info,
                    }
                return {
                    "status": 500,
                    "message": "Failed to delete file from S3.",
                    "debug": debug_info,
                }
        else:
            # Delete from the local file system
            try:
                os.remove(path)

                return {
                    "status": 200,
                    "message": "File deleted successfully.",
                    "debug": debug_info,
                }
            except Exception as exception:
                debug_info["exception"] = str(exception)
                if debug:
                    return {
                        "status": 500,
                        "message": f"Failed to delete file: {str(exception)}",
                        "debug": debug_info,
                    }
                return {
                    "status": 500,
                    "message": "Failed to delete file.",
                    "debug": debug_info,
                }
    except Exception as exception:
        debug_info["exception"] = str(exception)
        if debug:
            return {
                "status": 500,
                "message": f"Failed to delete file: {str(exception)}",
                "debug": debug_info,
            }
        return {
            "status": 500,
            "message": "Failed to delete file.",
            "debug": debug_info,
        }