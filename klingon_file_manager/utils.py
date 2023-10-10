# utils.py
import os
import boto3
from typing import Union, Dict

def read_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, bytes, bool, Dict[str, str]]]:
    """
    Reads a file from a given path, which can be either a local file or an S3 object.
    
    Args:
        path (str): The path of the file to read. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        
    Returns:
        dict: A dictionary containing the file content and type.
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
                # Read the file from S3
                response = s3.get_object(Bucket=bucket_name, Key=key)
                content = response["Body"].read()
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

def write_file(path: str, content: Union[str, bytes], debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    Writes content to a file at a given path, which can be either a local file or an S3 object.
    
    Args:
        path (str): The path where the file should be written. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        content (Union[str, bytes]): The content to write to the file.
        debug (bool, optional): Flag to enable debugging. Defaults to False.

    Returns:
        dict: A dictionary containing the status of the write operation.
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
                # Write the content to S3
                s3.put_object(Bucket=bucket_name, Key=key, Body=content)

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

def delete_file(path: str, debug: bool = False) -> Dict[str, Union[int, str, Dict[str, str]]]:
    """
    Deletes a file at a given path, which can be either a local file or an S3 object.
    
    Args:
        path (str): The path where the file should be deleted. Can be a local path or an S3 URI (e.g., 's3://bucket/key').
        debug (bool, optional): Flag to enable debugging. Defaults to False.

    Returns:
        dict: A dictionary containing the status of the delete operation.
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

def get_aws_credentials(debug: bool = False) -> dict:
    """
    Fetches AWS credentials from environment variables or provided arguments.
    
    Args:
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        
    Returns:
        dict: A dictionary containing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
    """
    AWS_ACCESS_KEY_ID  = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    if AWS_ACCESS_KEY_ID is None or AWS_SECRET_ACCESS_KEY is None:
        if debug:
            return {
                "status": 403,
                "message": "AWS credentials not found",
                "debug": {"error": "AWS credentials not found"},
            }
        return {
            "status": 403,
            "message": "AWS credentials not found",
        }

    return {
        "status": 200,
        "message": "AWS credentials retrieved successfully.",
        "credentials": {
            "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
            "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        },
    }


def is_binary_file(file_path: str, debug: bool = False) -> bool:
    """
    Checks if a file is binary or text.
    
    Args:
        file_path (str): The path to the file.
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        
    Returns:
        bool: True if the file is binary, False otherwise.
    """

    try:
        with open(file_path, "rb") as file:
            # Read the first few bytes from the file
            num_bytes_to_check = 1024  # You can adjust this value
            content = file.read(num_bytes_to_check)
            
            # Check for null bytes (often found in binary files)
            if b'\x00' in content:
                return True
            
            # Check for non-printable characters (common in binary files)
            if not content.isascii():
                return True
            
            # If none of the above conditions matched, it's likely a text file
            return False
    except:
        return False
