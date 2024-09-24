# this script will increment the build number in version file located in the "src" folder

import os
import re
import sys

ERROR = 1
NO_ERROR = 0

def increment_build():

    print()
    print("Incrementing build number...")

    version_file_name = "version.py"

    # Get the absolute path to the src directory
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
    file_path = os.path.join(src_dir, version_file_name)

    try:
        with open(file_path, 'r') as fileIn:
            lines = fileIn.readlines()

        for i, line in enumerate(lines):
            if line.startswith("BUILD ="):
                # Extract the current build number
                match = re.search(r'=(\s*\d+)', line)
                if match:
                    current_build = int(match.group(1))
                    # Increment the build number
                    new_build = current_build + 1
                    # Update the line with the new build number
                    lines[i] = f"BUILD = {new_build}\n"
                    break
        else:
            print(f"No 'BUILD' number found in {version_file_name}")
            return ERROR

        with open(file_path, 'w') as fileOut:
            fileOut.writelines(lines)

        print(f"Build number incremented from {current_build} to {new_build}")
        return NO_ERROR

    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return ERROR
    except IOError as e:
        print(f"Error reading or writing to file: {e}")
        return ERROR
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ERROR

if __name__ == "__main__":
    if increment_build() == ERROR:
        sys.exit(1)

