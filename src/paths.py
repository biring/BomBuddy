# manage paths to files and folders

import os


def get_sample_folder_path():
    # Get path to directory of current file
    path = os.path.dirname(__file__)
    # Split path to get to project folder. Based on project folder this is once level above 'src'
    if "src" in path:
        path = os.path.split(path)[0]
    # Build path to sample folder. Based on project folder arrangement this is in folder 'sample'
    path = os.path.join(path, "sample")
    # Good practice to make path OS independent
    path = os.path.normpath(path)
    # test the file path
    check_path_to_folder_is_valid(path)
    return path


def build_path_to_outputs_file(folder_path, file_name="Temp.xlsx"):
    path = os.path.join(folder_path, file_name)
    # Good practice to make path OS independent
    path = os.path.normpath(path)
    return path


def sample_file_path(name):
    # Build path to sample data file
    path = os.path.join(get_sample_folder_path(), name)
    # make path OS independent
    path = os.path.normpath(path)
    # test the file path
    check_path_to_folder_is_valid(path)
    return path


def check_path_to_folder_is_valid(folder_path):
    """
    Check if the specified folder path exists.

    Parameters:
    - folder_path (str): The path of the folder to be checked.

    Returns:
    - bool: True if the folder exists, False otherwise.

    Usage:
    - Call this function with the folder path you want to check.
      Example: check_path_to_folder_is_valid("/path/to/your/folder")
    """

    import os
    import sys

    try:
        # Check if the specified folder path exists
        path_exists = os.path.exists(folder_path)
        # If the path exists, return True
        if path_exists:
            return True

        # If the path doesn't exist, raise FileNotFoundError
        else:
            raise FileNotFoundError

    except FileNotFoundError:
        # Print error message and details
        print("Path to folder does not exist")
        print(folder_path)
        print("Application end")

        # Exit the program
        sys.exit()


def get_input_file_path():
    """
    Prompt the user to enter the full path to an Excel file or 'X' or 'x' to exit.

    Returns:
        str: The file path as an 'r' string if provided by the user.

    Example:
        excel_path = get_excel_file_path_or_exit()
        print("Excel file path:", excel_path)
    """
    # Keep trying until we get an Excel file or the user decides to exit
    while True:
        # Prompt user for input
        file_path_or_exit = input("Enter the full path to the Excel file or 'X' or 'x' to exit: ")
        # Check if user wants to exit
        if file_path_or_exit.upper() == 'X' or file_path_or_exit.upper() == 'x':
            print("Exiting the application.")
            exit()
        # Check if the file exists
        elif os.path.exists(file_path_or_exit):
            print("File exists.")
            return fr"{file_path_or_exit}"  # Convert the file path to 'r' string format
        # When file does not exist
        else:
            print("File not found. Please enter a valid file path.")


def get_path_to_inputs_folder():
    """
    Retrieve the path to the input data folder within the project directory structure.

    Returns:
        str: Path to the input data folder.
    """

    import os

    # Get path to current directory
    path = os.path.dirname(__file__)  # Get the directory of the current script

    # Split path to get to project folder. Based on project folder structure this is once level above 'src'
    if "src" in path:  # If "src" directory exists in the path
        path = os.path.split(path)[0]  # Move up one level to get to the project folder
    # Build path to input data folder. Based on project folder structure, this will be $project\data\input
    path = os.path.join(path, "data")  # Append "data" to the path
    path = os.path.join(path, "inputs")  # Append "input" to the path

    # Good practice to make path OS independent
    path = os.path.normpath(path)  # Normalize the path to ensure consistency across different operating systems

    return path


def get_excel_file_path(folder_path):
    """
    Prompts the user to select an Excel file from the specified folder.

    Args:
    - folder_path (str): The path to the folder containing the Excel files.

    Returns:
    - str: The full path to the selected Excel file as a raw string.

    Raises:
    - FileNotFoundError: If no Excel files are found in the specified folder.
    """

    import os
    import re

    # get the list of files in the folder
    files = os.listdir(folder_path)

    # filter only Excel files
    excel_files = [file for file in files if re.match(r'.*\.xlsx?$', file, re.IGNORECASE)]

    if not excel_files:
        raise FileNotFoundError("No Excel files found in the folder.")

    # print Excel files with numbers for the user to select
    for i, file in enumerate(excel_files, 1):
        print(f"[{i}] {file}")

    while True:
        choice = input("Enter the number of the file to open (or 'x' to exit): ")
        if choice.lower() == 'x':
            print("Exiting...")
            exit()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(excel_files):
                selected_file = excel_files[index - 1]
                full_path = os.path.join(folder_path, selected_file)
                return rf"{full_path}"  # return full path as a raw string
        else:
            print("Invalid input. Please enter a valid number or 'x' to exit.")


def get_path_to_outputs_folder():
    """
    Retrieve the path to the output data folder within the project directory structure.
    If the folder does not exist, it will be created.

    This function assumes a specific project directory structure where the script is located
    within a directory named "src", and the project folder contains a "data" directory with an
    "outputs" subdirectory.

    Returns:
        str: Path to the output data folder.
    """

    import os

    # Get path to current directory
    path = os.path.dirname(__file__)  # Get the directory of the current script

    # Split path to get to project folder. Based on project folder structure this is once level above 'src'
    if "src" in path:  # If "src" directory exists in the path
        path = os.path.split(path)[0]  # Move up one level to get to the project folder

    # Build path to output data folder. Based on project folder structure, this will be $project/data/outputs
    path = os.path.join(path, "data", "outputs")

    # Ensure that the folder exists, if not, create it
    if not os.path.exists(path):
        os.makedirs(path)

    # Good practice to make path OS independent
    path = os.path.normpath(path)  # Normalize the path to ensure consistency across different operating systems

    return path
