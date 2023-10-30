# klingon_file_manager.py
"""
Manages file operations like 'get', 'post', and 'delete' for both local and AWS S3 storage.

Args:
    action (str): The action to be performed ('get', 'post', or 'delete').
    path (str): The path for the file operation.
    content (Union[str, bytes], optional): The file content for 'post' action.
    md5 (str, optional): The md5 hash of the file content for 'post' action.
    debug (bool, optional): Flag to enable debugging. Defaults to False.
    
Returns:
    dict: A dictionary containing the result of the file operation with the following schema:
        {
            'action': str,         # Action performed ('get', 'post', or 'delete')
            'path': str,           # Path for the file operation
            'content': Union[str, bytes],  # File content for 'get' and 'post' actions
            'content_size_mb': float,  # Size of the content in megabytes
            'binary': bool,        # Flag indicating if the content is binary
            'md5': str,            # The md5 hash of the file content for 'get' and 'post' actions
            'status': int,         # HTTP-like status code (e.g., 200 for success, 500 for failure)
            'debug': Dict[str, str]  # Debug information (only included if 'debug' flag is True)
        }
"""
from typing import Union, Dict, Optional
from .utils import is_binary_file, get_aws_credentials, ProgressPercentage
from .delete import delete_file
from .write import write_file
from .read import read_file

# Use the get_aws_credentials function to get AWS credentials returned as a
# json object containing the following keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
aws_credentials = get_aws_credentials()
#AWS_ACCESS_KEY_ID = aws_credentials['credentials']['AWS_ACCESS_KEY_ID']
#AWS_SECRET_ACCESS_KEY = aws_credentials['credentials']['AWS_SECRET_ACCESS_KEY']

def manage_file(
    action: str,
    path: str,
    content: str = None,
    content_size: int = None,
    md5: Optional[str] = None,
    metadata: Optional[Dict[str, str]] = None,
    progress: bool(content_size),
    debug: bool = False,
) -> dict:

    debug_info = {}
    result = {
        'action': action,
        'path': path,
        'content': content[:10] if is_binary_file(content) else content,
        'content_size': len(content),
        'binary': is_binary_file(content),
        'md5': md5,
        'metadata': metadata,
        'debug': debug_info if debug else {},
    }

    try:
        if action == 'get':
            read_result = read_file(path, debug)
            result['status'] = read_result['status']
            result['content'] = read_result['content']
            result['binary'] = is_binary_file(result['content'], debug)
            # Add the debug info for the read_file() function
            if debug or result['status'] == 500:
                debug_info['read_file'] = read_result['debug']
        elif action == 'post':
            debug_info['write_file_start'] = f"Starting write_file with path={path}, content={content}, md5={md5}, metadata={metadata}"
            write_result = write_file(path, content, md5, metadata, debug)
            result['status'] = write_result['status']
            result['binary'] = is_binary_file(result['content'], debug)
            # Add the debug info for the write_file() function
            if debug or result['status'] == 500:
                debug_info['write_file'] = write_result['debug']
            return result
        elif action == 'delete':
            delete_result = delete_file(path, debug)
            result['status'] = delete_result['status']
            # Add the debug info for the delete_file() function
            if debug or result['status'] == 500:
                debug_info['delete_file'] = delete_result['debug']
        else:
            result['status'] = 500
            debug_info['error'] = 'Invalid action'
    except Exception as exception:
        result['status'] = 500
        result['error_message'] = str(exception)
        # Add the debug info for the exception
        debug_info['exception'] = str(exception) if debug else None
        debug_info['error_message'] = str(exception) if debug else None
    # If the debug flag is not set and there was no failure, remove the debug field
    # No need to delete the 'debug' key as it will be empty if debug is False

