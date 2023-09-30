# utils.py
import boto3

def read_file(path: str, debug: bool = False, AWS_ACCESS_KEY_ID: str = None, AWS_SECRET_ACCESS_KEY: str = None) -> dict:
    debug_info = {}
    # Get AWS credentials if path is an S3 path
    if path.startswith('s3://'):
        aws_creds = get_aws_credentials(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        if aws_creds is None:
            return {'status': 403, 'content': None, 'is_binary': None, 'debug': {'error': 'AWS credentials not found'}}
        s3 = boto3.client('s3', aws_access_key_id=aws_creds['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=aws_creds['AWS_SECRET_ACCESS_KEY'])
        # Parse S3 bucket and object key from the path
        path_parts = path[5:].split('/', 1)
        bucket = path_parts[0]
        key = path_parts[1] if len(path_parts) > 1 else ''
        try:
            # Download the file from S3
            s3_object = s3.get_object(Bucket=bucket, Key=key)
            content = s3_object['Body'].read()
            is_binary = True  # S3 returns bytes
            return {'status': 200, 'content': content, 'is_binary': is_binary, 'debug': debug_info}
        except Exception as e:
            debug_info['exception'] = str(e)
            return {'status': 500, 'content': None, 'is_binary': None, 'debug': debug_info}
    # Local file logic (existing)
    else:
        # (existing code for reading local files, unchanged)
    Args:
        path (str): The path of the file to read.
        debug (bool, optional): Flag to enable debugging. Defaults to False.
    Returns:
        dict: A dictionary containing the file content and type.
    """



    pass











def write_file(file: str, path: str, debug: bool = False, AWS_ACCESS_KEY_ID: str = None, AWS_SECRET_ACCESS_KEY: str = None) -> dict:
    debug_info = {}

    # Get AWS credentials if path is an S3 path
    if path.startswith('s3://'):
        aws_creds = get_aws_credentials(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        if aws_creds is None:
            return {'status': 403, 'debug': {'error': 'AWS credentials not found'}}

        s3 = boto3.client('s3', aws_access_key_id=aws_creds['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=aws_creds['AWS_SECRET_ACCESS_KEY'])

        # Parse S3 bucket and object key from the path
        path_parts = path[5:].split('/', 1)
        bucket = path_parts[0]
        key = path_parts[1] if len(path_parts) > 1 else ''

        try:
            # Upload the file to S3
            s3.put_object(Body=file, Bucket=bucket, Key=key)
            return {'status': 200, 'debug': debug_info}

        except Exception as e:
            debug_info['exception'] = str(e)
            return {'status': 500, 'debug': debug_info}
            
    # Local file logic (existing)
    else:
        # (existing code for writing local files, unchanged)



    """



    Writes a file to a given path (local or S3).







    Args:



        file (str): The file content to write.



        path (str): The path where the file will be written.



        debug (bool, optional): Flag to enable debugging. Defaults to False.







    Returns:



        dict: A dictionary containing the status of the operation.



    """



    pass











def is_binary_file(file: str) -> bool:



    """



    Determines if a file is binary or text.







    Args:



        file (str): The file content.







    Returns:



        bool: True if the file is binary, False otherwise.



    """



    pass











def get_aws_credentials(



    AWS_ACCESS_KEY_ID: str = None,



    AWS_SECRET_ACCESS_KEY: str = None



) -> dict:



    """



    Retrieves AWS credentials from environment variables or given parameters.







    Args:



        AWS_ACCESS_KEY_ID (str, optional): AWS Access Key ID. Defaults to None.



        AWS_SECRET_ACCESS_KEY (str, optional): AWS Secret Access Key. Defaults to None.







    Returns:



        dict: A dictionary containing AWS credentials.



    """



    pass











import os



import mimetypes







def read_file(path: str, debug: bool = False) -> dict:



    """



    Reads a file from a given path (local or S3) and returns its content along with its type (binary or text).







    Args:



        path (str): The path of the file to read.



        debug (bool, optional): Flag to enable debugging. Defaults to False.







    Returns:



        dict: A dictionary containing the file content and type.



    """



    debug_info = {}



    



    # Check if the file exists



    if not os.path.exists(path):



        return {'status': 500, 'content': None, 'is_binary': None, 'debug': {'error': 'File not found'}}







    try:



        # Determine the file type



        mime_type, encoding = mimetypes.guess_type(path)



        is_binary = mime_type.startswith('text/') if mime_type else False







        # Read the file



        mode = 'rb' if is_binary else 'r'



        with open(path, mode) as f:



            content = f.read()







        return {'status': 200, 'content': content, 'is_binary': is_binary, 'debug': debug_info}







    except Exception as e:



        debug_info['exception'] = str(e)



        return {'status': 500, 'content': None, 'is_binary': None, 'debug': debug_info}











def write_file(file: str, path: str, debug: bool = False) -> dict:



    """



    Writes a file to a given path (local or S3).







    Args:



        file (str): The file content to write.



        path (str): The path where the file will be written.



        debug (bool, optional): Flag to enable debugging. Defaults to False.







    Returns:



        dict: A dictionary containing the status of the operation.



    """



    debug_info = {}







    try:



        # Determine if the file is binary



        is_binary = is_binary_file(file)







        # Write the file



        mode = 'wb' if is_binary else 'w'



        with open(path, mode) as f:



            f.write(file)







        return {'status': 200, 'debug': debug_info}







    except Exception as e:



        debug_info['exception'] = str(e)



        return {'status': 500, 'debug': debug_info}











import os







def is_binary_file(file: str) -> bool:



    """



    Determines if a file is binary or text.







    Args:



        file (str): The file content.







    Returns:



        bool: True if the file is binary, False otherwise.



    """



    # Check the first 1024 bytes for null bytes



    return b' ' in file[:1024]











def get_aws_credentials(



    AWS_ACCESS_KEY_ID: str = None,



    AWS_SECRET_ACCESS_KEY: str = None



) -> dict:



    """



    Retrieves AWS credentials from environment variables or given parameters.







    Args:



        AWS_ACCESS_KEY_ID (str, optional): AWS Access Key ID. Defaults to None.



        AWS_SECRET_ACCESS_KEY (str, optional): AWS Secret Access Key. Defaults to None.







    Returns:



        dict: A dictionary containing AWS credentials.



    """



    # Check parameters first



    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:



        return {'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY_ID, 'AWS_SECRET_ACCESS_KEY': AWS_SECRET_ACCESS_KEY}



    



    # Check environment variables



    env_aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID', None)



    env_aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY', None)







    if env_aws_access_key_id and env_aws_secret_access_key:



        return {'AWS_ACCESS_KEY_ID': env_aws_access_key_id, 'AWS_SECRET_ACCESS_KEY': env_aws_secret_access_key}



    



    return None
