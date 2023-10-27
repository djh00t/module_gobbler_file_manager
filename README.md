# Klingon File Manager

## Introduction
The Klingon File Manager is a Python module designed for managing files both locally and on AWS S3 storage. 
It provides functionalities to 'get' and 'post' files using a unified interface.

## Installation
Run the following command to install the package:
```bash
pip install klingon-file-manager
```
The module looks for the following environment variables:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## Features
- Supports both local and AWS S3 storage
- Single function interface (`manage_file`) to handle 'get' and 'post' operations
- Debugging support

## Usage Examples
### Using `manage_file` function
Here's a basic example to get you started:

#### GET example

GET is the same as reading/downloading a file either locally or on S3.
```python
from klingon_file_manager import manage_file

result = manage_file(action='get', path='path/to/local/file.txt')

print(result)
```

When the 'get' action is used with the `manage_file` function, the output is a dictionary (which can be converted to a JSON object) with the following schema:
```json
{
    "status": "integer",
    "action": "string",
    "path": "string",
    "content": "string or bytes or null",
    "content_size_mb": "float or null",
    "binary": "boolean or null",
    "debug": "object or null"
}
```

Here is a description of each field:

- `status`: An integer representing the status of the operation. A status of 200 indicates success, while a status of 500 indicates an error.
- `action`: A string representing the action performed. In this case, it will be 'get'.
- `path`: A string representing the path of the file that was read.
- `content`: A string or bytes representing the content of the file that was read, or `null` if the file could not be read.
- `content_size_mb`: A float representing the size of the content in megabytes, or `null` if the file could not be read.
- `binary`: A boolean indicating whether the file is binary (`true`) or text (`false`), or `null` if the file could not be read.
- `debug`: An object containing debug information, or `null` if debugging is not enabled.

#### POST example

POST is the same as saving/uploading a file either locally or on S3.
```python
from klingon_file_manager import manage_file

# POST a file to S3
result = manage_file(action='post', path='s3://your-bucket/your-key', content='Your content here')

print(result)
```

When the 'post' action is used with the `manage_file` function, the output is a dictionary (which can be converted to a JSON object) with the following schema:

```json
{
    "status": "integer",
    "action": "string",
    "path": "string",
    "content": "string or bytes or null",
    "content_size_mb": "float or null",
    "binary": "boolean or null",
    "debug": "object or null"
}
```
Here is a description of each field:

- `status`: An integer representing the status of the operation. A status of 200 indicates success, while a status of 500 indicates an error.
- `action`: A string representing the action performed. In this case, it will be 'post'.
- `path`: A string representing the path of the file that was written.
- `content`: A string or bytes representing the content that was written to the file, or `null` if the file could not be written.
- `content_size_mb`: A float representing the size of the content in megabytes, or `null` if the file could not be written.
- `binary`: A boolean indicating whether the file is binary (`true`) or text (`false`), or `null` if the file could not be written.
- `debug`: An object containing debug information, or `null` if debugging is not enabled.

#### DELETE example

DELETE allows you to delete files either locally or stored on S3.

```python
from klingon_file_manager import manage_file

# To delete a file from local storage
result = manage_file(action='delete', path='path/to/local/file.txt')

print(result)
```

When the 'delete' action is used with the `manage_file` function, the output is a dictionary (which can be converted to a JSON object) with the following schema:

```json
{
    "status": "integer",
    "action": "string",
    "path": "string",
    "debug": "object or null"
}
```

Here is a description of each field:

- `status`: An integer representing the status of the operation. A status of 200 indicates success, while a status of 500 indicates an error.
- `action`: A string representing the action performed. In this case, it will be 'delete'.
- `path`: A string representing the path of the file that was deleted.
- `debug`: An object containing debug information, or `null` if debugging is not enabled.

## Contribution Guidelines
If you wish to contribute to this project, please submit a pull request.

## Running Tests
To run tests, execute the following command:
```bash
pytest
```
