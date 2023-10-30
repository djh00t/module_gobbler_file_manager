# write.py
import os
import boto3
from typing import Union, Dict
from .utils import get_aws_credentials, ProgressPercentage

from typing import Union, Optional, Dict
import os
import hashlib
import base64
import boto3
from botocore.config import Config


def write_file(path: str, content: Union[str, bytes], md5: Optional[str] = None, metadata: Optional[Dict] = None, debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    Writes content to a file at a given path, which can be either a local file or an S3 object.
    
    Args:
        path (str): The path where the file should be written. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        content (Union[str, bytes]): The content to write to the file.
        md5 (Optional[str]): The MD5 hash of the content. If provided, the function will check if the hash matches the content's MD5 hash before writing to the file.
        metadata (Optional[Dict]): The metadata to be added to the file. If provided, the function will add the metadata to the file.
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        
    Returns:
        dict: A dictionary containing the status of the write operation with the following schema:
            {
                "status": int,          # HTTP-like status code (e.g., 200 for success, 500 for failure)
                "message": str,         # Message describing the outcome
                "md5": str,             # The MD5 hash of the content
                "debug": Dict[str, str] # Debug information (only included if 'debug' flag is True)
            }
    """
    try:
        debug_info = {}

        # Check if md5 is provided and if it matches with the content's md5
        if md5 is not None:
            content_md5 = hashlib.md5(content.encode() if isinstance(content, str) else content).hexdigest()
            if content_md5 != md5:
                return {
                    "status": 400,
                    "message": "MD5 hash does not match the given file.",
                    "debug": debug_info,
                }
            else:
                # If md5 matches, add it to the debug_info
                debug_info["md5"] = content_md5

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
                "s3",
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                config=Config(s3={'addressing_style': 'path'})
            )
            if md5 is not None:
                # Add Content-MD5 header if md5 is provided
                content_md5_base64 = base64.b64encode(hashlib.md5(content.encode() if isinstance(content, str) else content).digest()).decode()
                extra_args = {'ContentMD5': content_md5_base64}
            else:
                extra_args = None

            try:
                # Write the content to a temporary file
                with open('/tmp/temp_file', 'wb') as temp_file:
                    # Check if content is a string and encode it to bytes if it is
                    if isinstance(content, str):
                        content = content.encode()
                    temp_file.write(content)
                # Write the content to S3 with progress callback
                s3 = boto3.resource('s3')
                progress = ProgressPercentage(len(content), key)
                if metadata is not None:
                    extra_args = {'Metadata': metadata}
                s3.Bucket(bucket_name).upload_file('/tmp/temp_file', key, ExtraArgs=extra_args, Callback=progress)
                os.remove('/tmp/temp_file')

                # Get the metadata of the uploaded file
                uploaded_file_metadata = get_s3_object_metadata(s3, bucket_name, key)
                uploaded_file_md5 = uploaded_file_metadata['Metadata'].get('md5chksum')
                if md5 != uploaded_file_md5:
                    return {
                        "status": 400,
                        "message": "MD5 hash does not match the uploaded file.",
                        "debug": debug_info,
                    }

                return {
                    "status": 200,
                    "message": "File written successfully to S3.",
                    "md5": content_md5,
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
            if metadata is not None:
                metadata_file_path = os.path.splitext(path)[0] + '.metadata.json'
                with open(metadata_file_path, 'w') as metadata_file:
                    json.dump(metadata, metadata_file)
            if md5 is not None:
                # Save a file containing the MD5 hash next to the file
                md5_file_path = os.path.splitext(path)[0] + '.md5'
                with open(md5_file_path, 'w') as md5_file:
                    md5_file.write(md5)

            return {
                "status": 200,
                "message": "File written successfully.",
                "md5": content_md5,
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
        
def get_s3_object_metadata(s3, bucket_name, key):
    """
    Retrieves the metadata of an S3 object.

    Args:
        s3 (boto3.resource): The S3 resource.
        bucket_name (str): The name of the S3 bucket.
        key (str): The key of the S3 object.

    Returns:
        dict: The metadata of the S3 object.
    """
    try:
        response = s3.meta.client.head_object(Bucket=bucket_name, Key=key)
        return response
    except Exception as e:
        print(f"Error getting metadata for S3 object {bucket_name}/{key}: {e}")
        return None
