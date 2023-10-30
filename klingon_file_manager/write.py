# write.py
import os
import boto3
from typing import Union, Dict, Optional
from .utils import get_aws_credentials, ProgressPercentage

def write_file(path: str, content: Union[str, bytes], md5: Optional[str] = None, metadata: Optional[Dict[str, str]] = None, debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    Writes content to a file at a given path, which can be either a local file or an S3 object.
    
    Args:
        path (str): The path where the file should be written. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        content (Union[str, bytes]): The content to write to the file.
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        
    Returns:
        dict: A dictionary containing the status of the write operation with the following schema:
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
            # Write to S3 if the path is an S3 URI
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
                # Write the content to S3 with progress callback
                s3 = boto3.resource('s3')
                file_size = len(content)
                progress = ProgressPercentage(file_size, '/tmp/temp_file')
                import hashlib
                if md5:
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    elif isinstance(content, int):
                        content = bytes(content)
                    calculated_md5 = hashlib.md5(content).hexdigest()
                    if calculated_md5 != md5:
                        return {
                            "status": 400,
                            "message": "Provided MD5 does not match calculated MD5.",
                            "debug": debug_info,
                        }
                    metadata["md5"] = calculated_md5

                s3.Bucket(bucket_name).upload_file('/tmp/temp_file', key, Callback=progress, ExtraArgs={'Metadata': metadata})
                os.remove('/tmp/temp_file')

                return {
                    "status": 200,
                    "message": "File written successfully to S3.",
                    "debug": debug_info,
                }
            except Exception as exception:
                debug_info["exception"] = str(exception)
                if debug:
                    return {
                        "status": 500,
                        "message": f"Failed to write file to S3: {str(exception)}",
                        "debug": debug_info,
                    }
                return {
                    "status": 500,
                    "message": "Failed to write file to S3.",
                    "debug": debug_info,
                }
        else:
            # Write to the local file system
            with open(path, "wb" if isinstance(content, bytes) else "w") as file:
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
                "debug": debug_info,
            }
        return {
            "status": 500,
            "message": "Failed to write file.",
            "debug": debug_info,
        }
