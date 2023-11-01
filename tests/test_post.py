import io
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock, mock_open
from klingon_file_manager import post_file, _post_to_s3, _post_to_local  # Importing functions from your post.py module
from klingon_file_manager import get_mime_type  # Importing get_mime_type function from utils.py module

# A pytest fixture to manage temporary files for the test.
@pytest.fixture(params=['text', 'binary'])
def temp_file(request):
    mode = 'w+' if request.param == 'text' else 'wb+'
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode=mode, delete=False) as f:
        if request.param == 'text':
            f.write("This is a test file.")
        else:
            f.write(b'\x00\x01\x02\x03')
        temp_name = f.name
    yield temp_name  # Yield control to test function
    #os.unlink(temp_name)  # Cleanup: delete the temporary file

# Test for function post_file
def test_post_file(temp_file):
    import pdb; pdb.set_trace()  # Add a breakpoint here for debugging
    
    print("Starting test_post_file")  # Debug print

    # Use patch as a context manager
    with patch("klingon_file_manager._post_to_s3") as mock_post_to_s3, patch("klingon_file_manager._post_to_local") as mock_post_to_local:
        
        # Mock the return values
        mock_post_to_s3.return_value = {"status": 200, "message": "OK"}
        mock_post_to_local.return_value = {"status": 200, "message": "OK"}
        
        print("Mocks should be active here")  # Debug print

        # Open the temp file and read its contents
        with open(temp_file, "rb") as f:
            content = f.read()

        # Call the function under test
        result = post_file(
            path="s3://bucket/file",
            content=content,
            debug=True
        )
        print(f"Result from post_file when posting to S3: {result}")  # Debug print

        # Assertions
        assert result["status"] == 200