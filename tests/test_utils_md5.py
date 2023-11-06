import os
import tempfile
import hashlib
from klingon_file_manager.utils import get_md5_hash, get_md5_hash_filename

def test_get_md5_hash():
    # Test with string input
    assert get_md5_hash('hello') == hashlib.md5('hello'.encode('utf-8')).hexdigest()
    # Test with bytes input
    assert get_md5_hash(b'hello') == hashlib.md5(b'hello').hexdigest()

def test_get_md5_hash_filename():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(b'hello')
        temp_filename = temp.name

    # Test with the temporary file
    assert get_md5_hash_filename(temp_filename) == hashlib.md5(b'hello').hexdigest()

    # Clean up the temporary file
    os.remove(temp_filename)
