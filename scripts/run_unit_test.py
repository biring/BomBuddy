"""
This script discovers and runs all unit tests located in the "tests" folder.

NOTE:
To ensure proper test discovery and import resolution with `unittest`:

1. Both "src" and "tests" must be regular folders in PyCharm
   (i.e., NOT marked as "Source Root" or "Test Root").

2. The "tests" folder should mirror the module structure of "src".
   - If `src/parsers/foo.py` exists, then the corresponding test should be placed in
     `tests/parsers/test_foo.py`.
   - This parallel structure enables clean separation of source and test logic
     while preserving consistent import paths.

3. Every folder under "tests" that contains test modules must include an `__init__.py` file.
   - This allows the folder to be treated as a proper Python package.
   - Without these files, `unittest` may fail to import and run the test modules.
"""


import os
import subprocess
import sys

# Function to run the tests
def run_tests():
    print()
    print("Running unit tests...")
    try:
        # Get the absolute path to the tests directory
        tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tests')

        # Run unittest and capture output
        result = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', tests_dir, '-p', 'test_*.py'])
        if result.returncode == 0:
            print("Unit test passed.")
            return 0  # Indicate success
        else:
            print("Unit tests FAILED.")
            return 1  # Indicate failure
    except subprocess.CalledProcessError as e:
        print(f"ERROR during unit test: {e}")
        return e.returncode

if __name__ == "__main__":
    if run_tests() != 0:
        sys.exit(1)
