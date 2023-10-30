# utils.py
import os
import boto3
from typing import Union, Dict
import threading
import sys
import magic

def get_mime_type(file_path: str) -> str:
    """
    Gets the mime type of a file.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        str: The mime type of the file.
    """
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)


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


import chardet

def is_binary_file(content: bytes, debug: bool = False) -> bool:
    """
    Checks if content is binary or text.
    
    Args:
        content (bytes): The content to check.
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        
    Returns:
        bool: True if the content is binary, False otherwise.
    """

    try:
        # Detect the encoding of the content
        result = chardet.detect(content)

        # If the detected encoding is None or 'ISO-8859-1', the content is likely binary
        return result['encoding'] is None or result['encoding'] == 'ISO-8859-1'
    except:
        return False




