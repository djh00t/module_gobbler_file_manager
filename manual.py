import json
from klingon_file_manager import manage_file

# Set file names for testing
TEST_GET_LOCAL_TXT_FILE='tests/manual.txt'
TEST_GET_LOCAL_BIN_FILE='tests/audio.wav'

#                   Action, File, Path,                    Debug, AWS Access Key ID, AWS Secret Access Key                
result = manage_file('get', None, TEST_GET_LOCAL_TXT_FILE, False)
#result = manage_file('get', None, TEST_GET_LOCAL_BIN_FILE, False)

# Print whole result dictionary when debugging
# print(f"Result: {result}")

# If the result['binary'] key is True, then the file is binary and we need to
# replace the file contents with the string 'Binary File - {size} MB' where {size} is
# the calculated size of the file in megabytes.
# If the result['binary'] key is False, then the file is not binary and we need
# to return the file contents as a string.
if result['binary']:
    result['file'] = "binary"
else:
    result['file'] = result['file'].decode('utf-8')

# Add a "types" key to the result dictionary which contains the name of each
# key and its type as a value.
result['types'] = {}
for key in result:
    result['types'][key] = type(result[key]).__name__

# print the whole json object using pretty formatting
print(json.dumps(result, indent=4, sort_keys=True))