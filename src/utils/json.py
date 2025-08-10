"""
Utility helpers for serializing/deserializing JSON and reading/writing JSON files.

This module includes helpers to:
 - Convert dicts (string keys) ↔ JSON strings (`dict_to_json_string`, `json_string_to_dict`)
 - Load a JSON file into a dict (`load_json_file`)
 - Save a dict to a JSON file with optional pretty-printing (`save_json_file`)

Common use cases include configuration I/O, small data caches, and test fixtures
where simple, UTF-8–safe JSON is preferred over custom formats.

Example Usage:
    # Preferred usage via package interface:
    from src.utils.json import load_json_file, save_json_file
    cfg = load_json_file("config.json")
    save_json_file("out.json", {"status": "ok"}, indent_spaces=2)

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils.json as json_util
    text = json_util.dict_to_json_string({"name": "Δ"}, indent_spaces=None)

Dependencies:
 - Python >= 3.10  (`dict[str, Any]` typing)
 - Standard Library: json, typing

Notes:
 - Keys are assumed to be strings; values must be JSON-serializable.
 - Files are read/written as UTF-8; `ensure_ascii=False` preserves Unicode characters.
 - `indent_spaces=None` emits compact JSON; set to an int for pretty-printing.
 - Functions raise `RuntimeError` with wrapped original exceptions for clearer diagnostics.
 - Intended for internal use within the `utils` package to centralize JSON I/O.

License:
 - Internal Use Only
"""

import json
from typing import Any


def dict_to_json_string(input_dict: dict[str, Any], *, indent_spaces: int | None = None) -> str:
    """
    Serializes a dictionary of string keys into a JSON-formatted string.

    Converts a Python dictionary with string keys and any JSON-compatible values
    into a UTF-8-safe JSON string. Supports optional pretty-printing via the
    `indent` parameter. Raises a descriptive error if serialization fails.

    Args:
        input_dict (dict[str, Any]): Dictionary with string keys to be converted into JSON.
        indent_spaces (int | None, optional): Number of spaces for indentation in the output.
            Defaults to None for compact formatting.

    Returns:
        str: JSON-formatted string representation of the input dictionary.

    Raises:
        RuntimeError: If the dictionary cannot be serialized to JSON.
    """
    try:
        # Convert dictionary to JSON string with optional pretty printing
        return json.dumps(input_dict, indent=indent_spaces, ensure_ascii=False)
    except Exception as err:
        # Wrap the original exception with a more descriptive RuntimeError
        raise RuntimeError(
            f"Failed to serialize dictionary to JSON string — data may contain unsupported types.\n"
            f"{type(err).__name__}: {err}"
        ) from err


def json_string_to_dict(json_string: str) -> dict[str, Any]:
    """
    Deserializes a JSON-formatted string into a Python dictionary.

    Parses a UTF-8-safe JSON string and returns a Python dictionary
    with string keys and any JSON-compatible values. Raises a
    descriptive error if parsing fails or the data is not valid JSON.

    Args:
        json_string (str): JSON-formatted string to be parsed.

    Returns:
        dict[str, Any]: Dictionary representation of the parsed JSON data.

    Raises:
        RuntimeError: If parsing fails or if the JSON is invalid.
    """
    try:
        # Parse the JSON string into a Python dictionary
        return json.loads(json_string)
    except Exception as err:
        # Wrap the original exception with a more descriptive RuntimeError
        raise RuntimeError(
            f"Failed to deserialize JSON string — input may be invalid or not represent a dictionary.\n"
            f"{type(err).__name__}: {err}"
        ) from err


def load_json_file(file_path: str) -> dict[str, Any]:
    """
    Loads and parses a JSON file into a Python dictionary.

    Opens the file in read-only mode using UTF-8 encoding, then parses
    its contents into a dictionary with string keys and JSON-compatible
    values. Raises a descriptive error if the file cannot be opened, read,
    or contains invalid JSON.

    Args:
        file_path (str): Absolute or relative path to the JSON file.

    Returns:
        dict[str, Any]: Dictionary representation of the parsed JSON file.

    Raises:
        RuntimeError: If reading or parsing fails for any reason.
    """
    try:
        # Open the JSON file for reading with UTF-8 encoding
        with open(file_path, mode="r", encoding="utf-8") as file:
            # Parse the file contents into a Python dictionary
            return json.load(file)
    except Exception as err:
        # Wrap the original error with a descriptive message
        raise RuntimeError(
            f"Failed to load JSON file from '{file_path}' — file may be missing, unreadable, or contain invalid JSON.\n"
            f"{type(err).__name__}: {err}"
        ) from err


def save_json_file(file_path: str, data_dict: dict[str, Any], *, indent_spaces: int | None = 2) -> None:
    """
    Writes a dictionary to disk as a JSON file.

    Serializes a dictionary with string keys and JSON-compatible values and writes
    it to the given path using UTF-8 encoding. By default, the output is pretty
    printed with indentation. Raises a descriptive error if the file cannot be
    created/written or if the data cannot be serialized.

    Args:
        file_path (str): Absolute or relative path to the target JSON file.
        data_dict (dict[str, Any]): Dictionary to serialize and save.
        indent_spaces (int | None, optional): Number of spaces used for indentation.
            Set to None for compact output. Defaults to 2.

    Returns:
        None: This function writes to disk and returns no value.

    Raises:
        RuntimeError: If the file cannot be created, opened, or written, or if
            serialization fails (e.g., due to non-serializable values).
    """
    try:
        # Open destination for writing (overwrites if the file exists)
        with open(file_path, mode="w", encoding="utf-8") as file:
            # Serialize the dictionary to JSON with optional pretty printing
            json.dump(data_dict, file, indent=indent_spaces, ensure_ascii=False)  # type: ignore[arg-type]
    except Exception as err:
        # Surface a clear, actionable error while preserving the original exception
        raise RuntimeError(
            f"Failed to save JSON file at '{file_path}' — directory may not exist, "
            f"file may be locked, or data contains non-serializable types.\n"
            f"{type(err).__name__}: {err}"
        ) from err
