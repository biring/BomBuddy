"""
Utility functions for safe and minimal file path operations.

This module provides reusable, stateless helpers for working with file paths.
It is designed for use across application layers, especially where low-level
file operations are needed without business logic coupling.

Main Capabilities:
 - Join and normalize file paths
 - Check if a path exists and is a file
 - Escape backslashes for safe display/logging
 - Validate file for Windows compatibility
 - List files in a directory with optional extension filtering

Example Usage:
    # Preferred usage via package interface:
    from src.utils import file
    paths = file.get_files_in_directory("data", extensions=[".txt"])

    # Direct module usage (acceptable for tests or internal scripts):
    import src.utils.file_utils as fu
    if fu.is_existing_file("config/settings.yaml"):
        print("Valid config file found.")

Dependencies:
 - Python >= 3.10
 - Standard Library: os, typing

Notes:
 - This module assumes caller responsibility for input validation and higher-level error handling.
 - All functions are stateless and do not maintain any internal context.
 - Designed for cross-layer utility use, including in CLI tools, UI layers, and service/controllers.

License:
 - Internal Use Only
"""

import os
from typing import Optional
from pathlib import Path

# MODULE CONSTANTS
TEXT_FILE_TYPE = ".txt"
EXCEL_FILE_TYPE = ".xlsx"
JSON_FILE_EXT = ".json"


def assert_filename_with_extension(file_path: str, expected_ext: str) -> None:
    """
    Ensures that a file's name has exactly one dot and matches the required extension.

    This function validates that the filename portion of the provided path:
      - Contains exactly one dot, separating the name and extension.
      - Has an extension that exactly matches the specified `expected_ext`
        (comparison is case-sensitive).

    Args:
        file_path (str): Absolute or relative path to the file.
        expected_ext (str): Required file extension including the leading dot (e.g., ".txt").

    Returns:
        None: This function only validates the filename and raises exceptions for violations.

    Raises:
        RuntimeError: If validation cannot be completed due to errors
    """
    try:
        path_obj = Path(file_path)  # Convert string path to a Path object for easy name/suffix access
        file_name = path_obj.name  # Extract just the filename (without directories)
        file_ext = path_obj.suffix  # Extract the extension

        # Check that the filename contains exactly one dot
        if file_name.count(".") != 1:
            raise ValueError(f"Invalid filename '{file_name}': must contain exactly one dot.")

        # Validate the file extension matches the expected one (case-sensitive)
        if file_ext != expected_ext:
            raise ValueError(
                f"Invalid extension for '{file_name}': expected '{expected_ext}', got '{file_ext}'."
            )
    except Exception as err:
        # Wrap and raise a RuntimeError with the original exception details
        raise RuntimeError(
            f"Failed file name and extension check '{file_path}'\n"
            f"{type(err).__name__} - {err}"
        ) from err


def build_file_path(folder: str, file: str) -> str:
    """
    Joins a folder path and file name into a full file system path.

    Strips leading/trailing whitespace from both inputs and combines them using
    the appropriate OS-specific separator.

    Args:
        folder (str): The directory portion of the path.
        file (str): The file name or relative file path to append.

    Returns:
        str: The combined full file path.

    Raises:
        ValueError: If either `folder` or `file` is empty or not a string.
    """
    if not isinstance(folder, str) or not folder.strip():
        raise ValueError("The folder path must be a non-empty string.")
    if not isinstance(file, str) or not file.strip():
        raise ValueError("The file name must be a non-empty string.")

    # Validate inputs and strip whitespace before joining paths
    return os.path.join(folder.strip(), file.strip())


def escape_backslashes(file_path: str) -> str:
    """
    Escapes backslashes in a file path for display or logging.

    Converts all single backslashes to double backslashes so the path
    resembles a raw string literal. Useful for logging or serialization on
    Windows systems where backslashes are common in paths.

    Args:
        file_path (str): The original file path string.

    Returns:
        str: The file path with all backslashes escaped.

    Raises:
        TypeError: If the input is not a string.
    """
    if not isinstance(file_path, str):
        raise TypeError(f"'{file_path}' is not a string.")

    # Replace single backslashes with double for safe string display/logging
    return file_path.replace("\\", "\\\\")


def get_files_in_directory(dir_path: str, extensions: Optional[list[str]] = None) -> tuple[str, ...]:
    """
    Lists immediate files in a directory, optionally filtering by extension.

    Scans the given directory and returns all non-directory files found at the top level.
    If `extensions` are provided, only files matching those extensions are included
    (case-insensitive).

    Args:
        dir_path (str): The directory path to scan for files.
        extensions (Optional[list[str]]): List of file extensions to filter by
            (e.g., ['.txt', '.csv']). If None or empty, all files are returned.

    Returns:
        tuple[str, ...]: Names of files directly inside the directory, optionally filtered.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        NotADirectoryError: If the given path is not a directory.
        PermissionError: If access to the directory is denied.
    """
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The directory '{dir_path}' does not exist.")
    if not os.path.isdir(dir_path):
        raise NotADirectoryError(f"The path '{dir_path}' is not a directory.")

    # List all entries in the directory
    try:
        dir_entries = os.listdir(dir_path)
    except PermissionError as e:
        raise PermissionError(f"Permission denied for directory '{dir_path}'.") from e

    # Filter to include only files (ignore subdirectories)
    immediate_files = [
        entry for entry in dir_entries
        if os.path.isfile(os.path.join(dir_path, entry))
    ]

    # If extensions are specified, filter files by matching extensions
    if extensions:
        extensions = [ext.lower() for ext in extensions]  # Normalize extensions
        matched_files = [
            filename for filename in immediate_files
            if any(filename.lower().endswith(ext) for ext in extensions)
        ]
    else:
        matched_files = immediate_files

    return tuple(matched_files)


def is_existing_file(file_path: str) -> bool:
    """
    Determines if a given path exists and is a regular file.

    This function checks whether the specified filesystem path exists and refers to
    a regular file (not a directory, symbolic link, or special file type).

    Args:
        file_path (str): The absolute or relative path to check.

    Returns:
        bool: True if the path exists and is a regular file, False otherwise.

    Raises:
        TypeError: If file_path is not a string.
    """
    if not isinstance(file_path, str):
        raise TypeError("file_path must be a string.")

    # Check if the given path exists and refers to a regular file (not a directory or symlink)
    return os.path.isfile(file_path)


def is_valid_file_path(name: str) -> bool:
    """
    Checks whether a given file path name contains only safe characters on Windows.

    This function validates that the name contains no invalid characters and does not
    match any reserved system names. On non-Windows platforms, it returns False.

    Args:
        name (str): The file path name to validate.

    Returns:
        bool: True if the name is valid on Windows, False otherwise.
    """
    # Windows forbidden characters (source: https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)
    INVALID_CHARS_WINDOWS = {'<', '>', ':', '"', '/', '\\', '|', '?', '*'}

    if not name or not isinstance(name, str):
        return False

    if os.name != 'nt':
        # This utility is Windows-specific
        return False

    if any(char in INVALID_CHARS_WINDOWS for char in name):
        return False

    return True
