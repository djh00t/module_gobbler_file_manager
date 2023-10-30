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


l


class ProgressPercentage(object):
    """
    A utility class to show the upload/download progress in percentage.
    
    Attributes:
        _total_size (int): The total size of the file being transferred in bytes.
        _seen_so_far (int): The amount of bytes transferred so far.
        _filename (str): The name of the file being transferred.
        _lock (threading.Lock): A lock to ensure thread safety.
        
    Input Schema:
        total_size: int
        filename: str
    """
    
    def __init__(self, total_size: int, filename: str):
        """
        Initializes the ProgressPercentage class.
        
        Args:
            total_size (int): The total size of the file being transferred in bytes.
            filename (str): The name of the file being transferred.
            
        Input Schema:
            total_size: int
            filename: str
        """
        self._total_size = total_size
        self._seen_so_far = 0
        self._filename = filename
        self._lock = threading.Lock()

    def __call__(self, bytes_amount: int):
        """
        Callable method to update the progress percentage.
        
        Args:
            bytes_amount (int): The amount of bytes transferred so far.
            
        Input Schema:
            bytes_amount: int
            
        Output:
            Writes the progress percentage to stdout.
        """
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._total_size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._total_size,
                    percentage))
            sys.stdout.flush()


