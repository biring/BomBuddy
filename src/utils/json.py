"""
Utility helpers for serializing/deserializing JSON and reading/writing JSON files.

This module includes helpers to:
 - Conversion between dicts (string keys) ↔ JSON strings (`dict_to_json_string`, `json_string_to_dict`)
 - Reading/writing JSON files (`load_json_file`, `save_json_file`)
 - Foundational JSON structure helpers with metadata and checksum support
 - Strict key–value text parser for `"Key" = "Value"` configuration formats

Typical uses include:
 - Centralized JSON I/O for configuration, small datasets, and test fixtures
 - Creating self-validating JSON objects with metadata and checksums
 - Parsing deterministic key–value text formats for configuration import

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
 - Standard Library: json, re, datetime, typing

Notes:
 - Keys are assumed to be strings; values must be JSON-serializable.
 - Files are read/written as UTF-8; `ensure_ascii=False` preserves Unicode characters.
 - `indent_spaces=None` emits compact JSON; set to an int for pretty-printing.
 - Functions raise `RuntimeError` with wrapped original exceptions for clearer diagnostics.
 - Strict key–value parsing enforces `"Key" = "Value"` format and rejects duplicates.
 - Functions raise `RuntimeError` with wrapped original exceptions for clear diagnostics.
 - Intended for internal use within the `utils` package to centralize JSON I/O.

License:
 - Internal Use Only
"""

import json
import re
from datetime import datetime, timezone
from typing import Any, TypedDict

LINE_KEY_VALUE_RE = re.compile(
    r'^\s*'  # Optional leading whitespace
    r'"([^"]+)"'  # "key" — one or more non-quote characters inside quotes
    r'\s*=\s*'  # Optional spaces around '='
    r'"([^"]*)"'  # "value" — zero or more non-quote characters inside quotes
    r'\s*$'  # Optional trailing whitespace
)


# FOUNDATIONAL SCHEMA
class JsonMeta(TypedDict):
    generated_utc: str
    source_file: str
    checksum: int  # uint32


class FoundationObject(TypedDict):
    meta: JsonMeta
    data: dict[str, Any]


def parse_strict_key_value_to_dict(source_path: str, text: str) -> dict[str, str]:
    """
    Parse a quoted key–value configuration text into a dictionary.

    Each non-empty, non-comment line must match the exact form `"Key" = "Value"`. Lines
    beginning with `#` are ignored, and trailing comments introduced by `#` are stripped
    before validation. Invalid lines are skipped with a WARNING log entry. Duplicate keys
    terminate parsing with an exception.

    Args:
        source_path (str): Logical name or file path used only for diagnostics in logs/errors.
        text (str): Entire input content to parse.

    Returns:
        dict[str, str]: Mapping of parsed keys to values.

    Raises:
        RuntimeError: If the same key appears more than once in the input.
    """
    result: dict[str, str] = {}

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        # Ignore empty lines exactly (after trimming whitespace).
        if raw_line.strip() == '':
            continue

        # Ignore lines that begin with '#' (no leading whitespace allowed by spec).
        if raw_line.startswith('#'):
            continue

        # Strip trailing comments and surrounding whitespace.
        content = raw_line.split('#', 1)[0].strip()
        if content == '':
            # Line reduced to nothing after removing a trailing comment.
            continue

        # Validate strict `"Key" = "Value"` format.
        match = LINE_KEY_VALUE_RE.match(content)
        if not match:
            # Non-conforming lines are not accepted; warn and skip
            print(f"Invalid key-value format at {source_path}:{line_no}; ignoring line: {raw_line!r}")
            continue

        # Extract key/value from regex groups (1 = key, 2 = value).
        key, value = match.group(1), match.group(2)

        # Enforce unique keys.
        if key in result:
            raise RuntimeError(f"Duplicate key '{key}' in {source_path} at line {line_no}.")

        result[key] = value

    return result


def now_utc_iso() -> str:
    """
    Get the current UTC time in ISO 8601 format with a 'Z' suffix.

    The output is accurate to the second (microseconds are removed) and uses the 'Z'
    suffix to indicate UTC, instead of an explicit offset.

    Returns:
        str: Current UTC timestamp in the form 'YYYY-MM-DDTHH:MM:SSZ'.
    """
    return (
        datetime.now(timezone.utc)  # Get current time in UTC
        .replace(microsecond=0)  # Remove microseconds for second precision
        .isoformat()  # Convert to ISO 8601
        .replace("+00:00", "Z")  # Replace '+00:00' with 'Z' for UTC
    )


def compute_dict_checksum_uint32(data: dict[str, Any]) -> int:
    """
    Compute a deterministic 32-bit unsigned checksum from a dictionary's contents.

    The checksum is calculated by:
      1. Sorting keys lexicographically to ensure consistent ordering.
      2. Concatenating each key and value with no separators.
      3. Encoding the concatenated string as UTF-8 bytes.
      4. Summing all byte values modulo 2^32.

    Args:
        data (dict[str, Any]): Dictionary whose keys and values are included in the checksum.
            Values will be converted to strings before concatenation.

    Returns:
        int: The checksum as an unsigned 32-bit integer.

    Example:
        # Ordered pairs: ("a", "1"), ("b", "2")
        # Concatenated string: "a1b2"
        # UTF-8 bytes: [97, 49, 98, 50]
        # Sum = 97 + 49 + 98 + 50 = 294 → 294 (within uint32 range)
        294
    """
    # Collect strings of keys and values in deterministic order
    parts: list[str] = []
    for key in sorted(data.keys()):
        value = data[key]
        parts.append(str(key))
        parts.append(str(value))

    # Convert concatenated string to UTF-8 bytes
    byte_seq = "".join(parts).encode("utf-8")

    # Sum bytes modulo 2^32 to fit into an unsigned 32-bit integer
    checksum = 0
    for byte in byte_seq:
        checksum = (checksum + byte) & 0xFFFFFFFF
    return checksum


def create_foundation_json(data: dict[str, Any], source_file: str) -> dict[str, Any]:
    """
    Build the foundational JSON object with metadata and provided data.

    The returned structure contains:
        {
            "meta": {
                "generated_utc": "<ISO 8601 UTC timestamp>",
                "source_file": "<original filename>",
                "checksum": <uint32 checksum of data>
            },
            "data": { ... }  # shallow copy of the provided data
        }

    Args:
        data (dict[str, Any]): Dictionary of data to include under the "data" key.
            Values will be shallow-copied into the output.
        source_file (str): Original filename or identifier for the data source.

    Returns:
        dict[str, Any]: The JSON-ready object containing metadata and the provided data.
    """
    # Assemble metadata
    meta_info = {
        "generated_utc": now_utc_iso(),
        "source_file": str(source_file),
        "checksum": compute_dict_checksum_uint32(data),
    }
    # Return JSON-ready structure with shallow copy of `data
    return {"meta": meta_info, "data": dict(data)}


def verify_foundation_json_checksum(obj: dict[str, Any]) -> bool:
    """
    Verify that the checksum in a foundational JSON object matches its data.

    This function compares the stored checksum in `obj["meta"]["checksum"]` against a
    newly computed checksum of `obj["data"]`. Returns True if they match, False otherwise.

    Args:
        obj (dict[str, Any]): JSON-like dictionary with the structure:
            {
                "meta": {
                    "checksum": <uint32>
                },
                "data": { ... }
            }

    Returns:
        bool: True if the computed checksum matches the stored checksum; False otherwise.
    """
    # Extract metadata and data
    meta_section = obj["meta"]
    data_section = obj["data"]

    # Parse stored checksum as int
    expected_checksum = int(meta_section["checksum"])

    # Compute checksum for data
    actual_checksum = compute_dict_checksum_uint32(data_section)

    # Return comparison result
    return actual_checksum == expected_checksum


def extract_foundation_data(foundation: dict[str, Any]) -> dict[str, Any]:
    """
    Return a shallow copy of the 'data' mapping from a foundation object.

    This function assumes the input object contains a 'data' key whose value can be
    converted to a dict. The returned dict is a shallow copy to avoid mutating the
    original structure.

    Args:
        foundation (dict[str, Any]): Foundation object expected to contain a 'data' mapping.

    Returns:
        dict[str, Any]: A shallow copy of obj['data'].
    """
    # Return a shallow copy so callers can't mutate the original 'data'
    return dict(foundation["data"])


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
