# This script will search and run all unit tests located in the "tests" folder

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
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', tests_dir, '-p', 'test_*.py'],
            check=False, capture_output=True, text=True)
        if result.returncode == 0:
            print("Unit test passed.")
            return 0  # Indicate success
        else:
            print("Unit tests failed.")
            print(result.stderr)
            return 1  # Indicate failure
    except subprocess.CalledProcessError as e:
        print(f"Unit tests failed: {e}")
        return e.returncode

if __name__ == "__main__":
    if run_tests() != 0:
        sys.exit(1)
