# write.py
import os
import boto3
from typing import Union, Dict, Optional
from .utils import get_aws_credentials, ProgressPercentage
import logging
from botocore.exceptions import ClientError
import hashlib


def write_file(path: str, content: Union[str, bytes], md5: Optional[str] = None, metadata: Optional[Dict[str, str]] = None, debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
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
                "debug": Dict[str, str] # Debug information (only included if 'debug' flag is True)
            }
    """
    print("path:            ", path)
    # Print first 10 chars of content
    print("content:         ", content[:10])
    print("md5:             ", md5)
    print("metadata:        ", metadata)
    print("debug:           ", debug)
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
                # Get file size in bytes
                file_size = len(content)
                # Set file name from key
                file_name = os.path.basename(key)
                # Set progress callback
                progress = ProgressPercentage(file_size, content)
                # Set metadata
                if md5:
                    if not isinstance(content, (str, bytes)):
                        content = str(content)
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    calculated_md5 = hashlib.md5(content).hexdigest()
                    if calculated_md5 != md5:
                        return {
                            "status": 400,
                            "message": "Provided MD5 does not match calculated MD5.",
                            "debug": debug_info,
                        }
                    metadata["md5"] = calculated_md5

                #s3.Bucket(bucket_name).upload_file('/tmp/temp_file', key, Callback=progress, ExtraArgs={'Metadata': metadata})

                # Convert content into binary if it's a string
                if isinstance(content, str):
                    content = content.encode('utf-8')

                print("###################################################################")
                print(" Upload content to S3")
                print("###################################################################")
                print("Bucket Name:    ", bucket_name)
                # Pull the file name out of the key
                file_name = os.path.basename(key)
                print("File Name:      ", file_name)
                print("Key:            ", key)
                print("Content:        ", content[:10])
                print("Metadata:       ", metadata)
                print("###################################################################")

                s3_client = boto3.client('s3')
                import io
                if isinstance(content, str):
                    content = content.encode('utf-8')
                with io.BytesIO(content) as f:
                    s3_client.upload_fileobj(
                        Bucket=bucket_name,
                        Key=key,
                        Body=f,
                        ContentMD5=md5,
                        Callback=progress,
                        ExtraArgs={'Metadata': metadata}
                    )


                #os.remove('/tmp/temp_file')

                

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
                "debug": debug_info,
            }
        return {
            "status": 500,
            "message": "Failed to write file.",
            "debug": debug_info,
        }
