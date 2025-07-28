# This script will search and run all unit tests located in the "tests" folder

# NOTE:
# To ensure accurate discovery of all unit tests under the "tests" directory and its subdirectories,
# every subfolder containing unit tests must be a Python module. This requires that each folder within
# the "tests" hierarchy include an `__init__.py` file. Without these files, the `unittest` discovery
# mechanism may fail to locate and execute all test cases correctly.


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
