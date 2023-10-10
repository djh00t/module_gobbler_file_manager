# klingon_file_manager.py
"""Klingon File Manager

Manage file operations like 'get', 'post' and 'delete' for both local and AWS S3 storage.

Args:
    action (str): The action to be performed ('get', 'post' or 'delete').
    path (str): The path for the file operation.
    content (str): The file content.
    debug (bool, optional): Flag to enable debugging. Defaults to False.

Returns:
    dict: A dictionary containing status, action, binary, file, path, and debug information.
"""

from .utils import read_file, write_file, delete_file, is_binary_file, get_aws_credentials

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
    content: str,
    debug: bool = False,
) -> dict:

    """Manages file operations like 'get' and 'post' for both local and
    AWS S3 storage.

    Args:
        action (str): The action to be performed ('get' or 'post').
        path (str): The path for the file operation.
        content (str): The file content.
        content_size_mb (int): The size of the content in megabytes.
        debug (bool, optional): Flag to enable debugging. Defaults to False.

    Returns:
        dict: A dictionary containing status, action, binary, file, path, and debug information.
    """

    debug_info = {}
    result = {
        'action': action,
        'path': path,
        'content': content,
        'content_size_mb': None,
        'binary': None,
        'debug': debug_info,
    }

    try:
        if action == 'get':
            read_result = read_file(path, debug)
            result['status'] = read_result['status']
            result['content'] = read_result['content']
            # Calculate the size in megabytes rounded to 6 decimal places of
            # the result['content'] object
            result['content_size_mb'] = round(len(result['content']) / 1000000, 6)
            result['binary'] = is_binary_file(path, debug)
            # Add the debug info for the read_file() function
            if debug or result['status'] == 500:
                debug_info['read_file'] = read_result['debug']
        elif action == 'post':
            write_result = write_file(path, content, debug)
            result['status'] = write_result['status']
            # Calculate the size in megabytes rounded to 6 decimal places of
            # the file object
            result['content_size_mb'] = round(len(content) / 1000000, 6)
            result['binary'] = is_binary_file(path, debug)
            # Add the debug info for the write_file() function
            if debug or result['status'] == 500:
                debug_info['write_file'] = write_result['debug']
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
        debug_info['exception'] = str(exception)
        debug_info['error_message'] = str(exception)
    # If the debug flag is not set and there was no failure, remove the debug field
    if not debug and result['status'] != 500:
        del result['debug']
    return result
