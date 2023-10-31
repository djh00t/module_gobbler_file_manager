# __init__.py
"""
# Klingon File Manager

File Management Module for Local and AWS S3 Storage. This module provides a set
of functions to manage files both locally and on AWS S3. It provides an
interface for reading, writing, and deleting files, with additional support for
debugging and AWS authentication.

Following are the core functions in this library:

## [manage_file](klingon_file_manager/manage.html)
Main function to manage files. It can handle operations like upload, download, delete, etc.

## [delete_file](/klingon_file_manager/delete.html)
Function to delete a file from local storage or AWS S3.

## [get_file](klingon_file_manager/get.html)
Function to get a file from local storage or AWS S3.

## [post_file](klingon_file_manager/post.html)
Function to post a file to local storage or AWS S3.

## [get_mime_type](klingon_file_manager/utils.html#get_mime_type)
Utility function to get the MIME type of a file.

## [get_aws_credentials](klingon_file_manager/utils.html#get_aws_credentials)
Utility function to get AWS credentials from environment variables.

## [is_binary_file](klingon_file_manager/utils.html#is_binary_file)
Utility function to check if a file is binary.

"""

from .manage import manage_file
from .delete import delete_file
from .get import get_file
from .post import post_file
from .utils import get_mime_type, get_aws_credentials, is_binary_file
