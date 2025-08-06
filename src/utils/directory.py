"""
Path resolution and directory management utilities.

This module provides utilities to:
 - Normalize and validate filesystem paths
 - Determine whether the application is running as a frozen executable
 - Resolve the application's root directory in both development and production (frozen) modes
 - Create directories with safety and existence checks

These functions are useful during application startup for configuring data locations,
loading resources, or setting up output folders in a robust and portable way.

Example Usage:
    # Preferred usage via public package interface:
    from src.utils import create_dir
    app_root = resolve_app_root()

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils.directory as dir
    app_root = dir.resolve_app_root()

Dependencies:
 - Python >= 3.8
 - Standard Library: os, sys, typing

Notes:
 - Assumes development environments organize source under a `src` folder
 - Automatically distinguishes between dev and packaged binary execution modes (e.g., PyInstaller)
 - All paths are normalized for cross-platform behavior

License:
 - Internal Use Only
"""

import os
import sys
from typing import Final

# CONSTANTS
SOURCE_CODE_FOLDER_NAME: Final = 'src'


def construct_directory_path(base_path: str, subfolders: tuple[str, ...]) -> str:
    """
    Constructs a fully normalized directory path from a base path and a sequence of subfolders.

    Each subfolder is joined in order to the base path using `os.path.join`. The final result
    is passed through `normalize_dir_path` to ensure consistent formatting across platforms,
    such as resolving redundant separators or adding a trailing slash if required.

    Args:
        base_path (str): The starting directory path.
        subfolders (tuple[str, ...]): A sequence of subdirectory names to append to the base path.

    Returns:
        str: The final normalized directory path.
    """
    # Iteratively join each subfolder to the base path
    for folder in subfolders:
        base_path = os.path.join(base_path, folder)

    # Normalize the final path to ensure consistent formatting across platforms
    base_path = normalize_dir_path(base_path)

    return base_path


def create_directory_if_missing(dir_path: str) -> bool:
    """
    Creates a directory at the specified path if it does not already exist.

    This function uses `os.makedirs` to create the directory and any necessary parent
    directories. It first checks whether the directory already exists. If creation fails,
    or if the directory still does not exist after the attempt, an `OSError` is raised.

    Args:
        dir_path (str): The full directory path to create.

    Returns:
        bool: True if the directory exists after the operation.

    Raises:
        OSError: If the directory cannot be created due to permission issues,
                 invalid paths, or other filesystem-related errors.
    """

    # Skip creation if the directory already exists
    if is_directory_path(dir_path):
        # TODO f"Directory '{path}' exists before creation attempt.")
        return True

    try:
        # Try creating the directory and any necessary parent directories
        os.makedirs(dir_path, exist_ok=True)
    except OSError as e:
        # Raise error with context if creation fails
        raise OSError(
            f"Failed to create directory '{dir_path}'."
            f"\nReason: {e.strerror or str(e)}."
            f"\nPossible causes: invalid path, permission denied, or name conflict with a file."
        ) from e

    # Confirm directory now exists
    if not is_directory_path(dir_path):
        raise OSError(
            f"Directory '{dir_path}' does not exist after creation attempt."
            f"\nThis may indicate a race condition, a transient filesystem error, or permission issue."
        )

    return True


def is_directory_path(dir_path: str) -> bool:
    """
    Checks whether the specified path exists and is a directory.

    This function determines if the given path exists on the filesystem and refers to
    a directory. It returns False if the path does not exist or if it points to a file,
    symbolic link, or other non-directory object.

    Args:
        dir_path (str): The filesystem path to check.

    Returns:
        bool: True if the path exists and is a directory, False otherwise.
    """
    # Return True only if the path exists and is a directory
    return os.path.isdir(dir_path)


def is_running_as_executable() -> bool:
    """
    Checks whether the application is running as a frozen executable.

    This is used to differentiate between development mode (executing Python source files)
    and production mode where the application is packaged as a standalone binary using tools
    like PyInstaller. These tools typically set the `sys.frozen` attribute.

    Returns:
        bool: True if the application is running as a frozen executable, False otherwise.
    """
    # Check if the 'frozen' attribute is set on the sys module (used by PyInstaller)
    return getattr(sys, 'frozen', False)


def list_immediate_subdirectories(dir_path: str) -> tuple[str, ...]:
    """
    Returns the names of all immediate subdirectories within a given directory path.

    This function lists only the subdirectories directly under the specified directory.
    It raises an error if the path does not exist or is not a directory.

    Args:
        dir_path (str): The directory path to scan for subdirectories.

    Returns:
        tuple[str, ...]: A tuple containing the names of immediate subdirectories.

    Raises:
        FileNotFoundError: If the path does not exist or is not a directory.
    """

    # Verify that the given path exists and is a directory
    if not is_directory_path(dir_path):
        raise FileNotFoundError(f"'{dir_path}' is not a valid directory")

    # List all entries (files and directories) in the directory
    all_entries = os.listdir(dir_path)

    # Keep only entries that are subdirectories
    sub_dirs = [
        entry for entry in all_entries
        if os.path.isdir(os.path.join(dir_path, entry))
    ]

    # Return subdirectory names as an immutable tuple
    return tuple(sub_dirs)


def normalize_dir_path(raw_path: str) -> str:
    """
    Normalizes a filesystem path by expanding the home directory and simplifying the structure.

    This function expands user home references (e.g., `~`) and simplifies the path by resolving
    redundant components such as `.` (current directory), `..` (parent directory), and multiple
    separators. It does not verify whether the resulting path exists on the filesystem.

    Args:
        raw_path (str): A relative or absolute filesystem path to normalize.

    Returns:
        str: A normalized path with user expansion and cleaned structure.

    Raises:
        TypeError: If the input is not a string.
    """
    # Ensure the input is a string
    if not isinstance(raw_path, str):
        raise TypeError(f"Expected '{raw_path}' as a string path, but got type: " + type(raw_path).__name__)

    # Expand user directory symbols like ~ to full home path
    expanded_path = os.path.expanduser(raw_path)

    # Clean the path by removing redundant slashes, ".", and ".."
    normalized_path = os.path.normpath(expanded_path)

    return normalized_path


def find_root() -> str:
    """
    Determines and returns the application's root directory based on the execution context.

    In a packaged (frozen) application, this function returns the directory containing the
    executable. In development mode, it returns the root of the source project. The returned
    path is normalized and absolute. An error is raised if the root cannot be resolved.

    Returns:
        str: Normalized absolute path to the application's root directory.

    Raises:
        FileNotFoundError: If the root directory cannot be resolved or does not exist.
    """
    try:
        # Determine resolution strategy based on packaging state
        if is_running_as_executable():
            # Running from a frozen executable (e.g., PyInstaller)
            app_root_dir = resolve_exe_dir()
        else:
            # Running from source (development mode)
            app_root_dir = resolve_dev_dir()

        return app_root_dir

    except Exception as e:
        # Raise a more informative error if resolution fails
        raise FileNotFoundError(f"Unable to resolve application root directory: {e}") from e


def resolve_dev_dir() -> str:
    """
    Resolves the project root directory when running in development mode.

    This function determines the root of the project by inspecting the location of
    the source file. If the `src` folder is part of the current path, it assumes
    the root is one level above it. The returned path is normalized and checked
    for existence.

    Returns:
        str: Normalized absolute path to the project root directory.

    Raises:
        FileNotFoundError: If the determined project root directory does not exist.
    """
    script_dir: str
    dev_dir: str

    # Get the absolute path of the current script's directory
    script_dir = os.path.dirname(__file__)

    # If the script resides in the source code folder, treat its parent as the root
    while SOURCE_CODE_FOLDER_NAME in script_dir:
        script_dir = os.path.split(script_dir)[0]

    # Normalize for consistent cross-platform behavior
    dev_dir = normalize_dir_path(script_dir)

    # Verify the resolved path exists and is a directory
    if not is_directory_path(dev_dir):
        raise FileNotFoundError(f"Path = '{dev_dir}' is not a directory")

    return dev_dir


def find_drive() -> str:
    """
    Determines and returns the drive letter of the application root directory.

    This function resolves the application's root path using `resolve_app_root()` and
    extracts the drive component (e.g., 'C:/') from it. It is designed for use on
    Windows systems where drive letters are required. On non-Windows platforms,
    a ValueError is raised.

    Returns:
        str: Normalized drive letter with a trailing slash (e.g., 'C:/').

    Raises:
        ValueError: If the function is called on a non-Windows platform or
                    if the drive letter cannot be determined.
    """
    # Ensure the platform supports drive letters
    if os.name != "nt":
        raise ValueError("resolve_drive() is only supported on Windows systems.")

    # Extract the drive component from the resolved application root
    drive, _ = os.path.splitdrive(find_root())

    # Validate that a drive letter was successfully found
    if not drive:
        raise ValueError(
            "Drive letter could not be determined from the application root path. "
            "Ensure the application is running on a Windows system with a valid root path."
        )

    # Normalize the drive path (e.g., 'C:/' instead of 'C:')
    return normalize_dir_path(drive + os.sep)


def resolve_exe_dir() -> str:
    """
    Retrieves the directory of the currently executing binary in frozen mode.

    This function returns the directory that contains the executable file when the application
    is packaged as a standalone binary (e.g., via PyInstaller). It normalizes the path for
    cross-platform compatibility and verifies that the resolved directory exists.

    Returns:
        str: Normalized absolute path to the executable's parent directory.

    Raises:
        FileNotFoundError: If the resolved path does not exist or is not a directory.
    """
    # Get the directory where the current executable resides
    exe_dir = os.path.dirname(sys.executable)

    # Normalize the path for consistent formatting across platforms
    normalized_exe_dir = normalize_dir_path(exe_dir)

    # Confirm the resolved path exists and is a directory
    if not is_directory_path(normalized_exe_dir):
        raise FileNotFoundError(
            f"Executable directory '{normalized_exe_dir}' does not exist or is not a valid directory. "
            "This may indicate a packaging error or incorrect frozen execution context."
        )

    return normalized_exe_dir


if __name__ == "__main__":
    pass
