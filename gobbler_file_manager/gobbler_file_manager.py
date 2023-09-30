"""Gobbler File Manager

Manage file operations like 'get' and 'post' for both local and AWS S3 storage.

Args:
    action (str): The action to be performed ('get' or 'post').
    file (str): The file to be managed.
    path (str): The path for the file operation.
    debug (bool, optional): Flag to enable debugging. Defaults to False.
    aws_access_key_id (str, optional): AWS Access Key ID. Defaults to None.
    aws_secret_access_key (str, optional): AWS Secret Access Key. Defaults to None.

Returns:
    dict: A dictionary containing status, action, binary, file, path, and debug information.
"""

from .utils import read_file, write_file, is_binary_file, get_aws_credentials

# Use the get_aws_credentials function to get AWS credentials returned as a
# json object containing the following keys:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
aws_credentials = get_aws_credentials()
aws_access_key_id = aws_credentials['credentials']['AWS_ACCESS_KEY_ID']
aws_secret_access_key = aws_credentials['credentials']['AWS_SECRET_ACCESS_KEY']

def manage_file(
    action: str,
    file: str,
    path: str,
    debug: bool = False,
    aws_access_key_id: str = None,
    aws_secret_access_key: str = None,
) -> dict:

    """Manages file operations like 'get' and 'post' for both local and
    AWS S3 storage.

    Args:
        action (str): The action to be performed ('get' or 'post').
        file (str): The file to be managed.
        file_size_mb (int): The size of the file in megabytes.
        path (str): The path for the file operation.
        debug (bool, optional): Flag to enable debugging. Defaults to False.
        aws_access_key_id (str, optional): AWS Access Key ID. Defaults to None.
        aws_secret_access_key (str, optional): AWS Secret Access Key. Defaults to None.

    Returns:
        dict: A dictionary containing status, action, binary, file, path, and debug information.
    """

    debug_info = {}
    result = {
        'action': action,
        'file': None,
        'file_size_mb': None,
        'path': path,
        'binary': None,
        'debug': debug_info,
    }

    try:
        if action == 'get':
            read_result = read_file(path, debug, aws_access_key_id, aws_secret_access_key)
            result['status'] = read_result['status']
            result['file'] = read_result['content']
            # Calculate the size in megabytes of the result['file'] object
            result['file_size_mb'] = len(result['file']) / 1000000
            result['binary'] = is_binary_file(path, debug)

            # Add the debug info for the read_file() function
            if debug or result['status'] == 500:
                debug_info['read_file'] = read_result['debug']

        elif action == 'post':
            write_result = write_file(file, path, debug, aws_access_key_id, aws_secret_access_key)
            result['status'] = write_result['status']

            # Add the debug info for the write_file() function
            if debug or result['status'] == 500:
                debug_info['write_file'] = write_result['debug']

        else:
            result['status'] = 500
            debug_info['error'] = 'Invalid action'

    except Exception as exception:
        result['status'] = 500

        # Add the debug info for the exception
        debug_info['exception'] = str(exception)

    # If the debug flag is not set and there was no failure, remove the debug field
    if not debug and result['status'] != 500:
        del result['debug']

    return result
