"""
Utility functions for sanitizing and normalizing text inputs.

This module includes helpers to:
 - Remove non-printable characters (e.g., control codes)
 - Normalize space characters (collapse multiple spaces, trim)
 - Remove all space characters or all types of whitespace

These are commonly used in data cleansing pipelines,
file parsers, or any user-generated text input processing.

Example Usage:
    # Preferred usage via public package interface:
    from src.utils import remove_all_whitespace

    # Direct module usage (acceptable in unit tests or internal scripts only):
    import src.utils.text_sanitizer as sanitizer
    clean = sanitizer.remove_all_whitespace(raw_text)

Dependencies:
 - Python >= 3.9
 - Standard Library: re, string

Notes:
 - This module is intended for internal use within the `utils` package.
 - Public functions should be imported via `src.utils` where possible to preserve API boundaries.
 - Designed for use in BOM parsing and other text preprocessing utilities.
 - Keeps separation of concerns between structure parsing and text cleanup.
"""

import re
import string
import pandas as pd

# CHARACTER CONSTANTS
EMPTY_STRING = ''  # No character
SPACE_CHAR = ' '  # One space character

# REGULAR EXPRESSIONS
WHITE_SPACE_REGEX = re.compile(r'\s+')  # Matches all Unicode whitespace characters (space, tab, newline, etc.)
MULTIPLE_SPACES_REGEX = re.compile(r' {2,}')  # Matches two or more consecutive space characters


def normalize_to_string(text) -> str:
    """
    Normalize input to a valid string.

    - Returns an empty string for None, NaN, or pd.NA.
    - Converts non-string types using str().
    - Leaves string inputs unchanged.

    This helper ensures that downstream string sanitizers can operate safely.

    Args:
        text: Any input value (str, None, float, int, NaN, pd.NA, etc.)

    Returns:
        str: A valid string representation, or "" if input was null-like.
    """
    # If the input is already a string, return it unchanged.
    if isinstance(text, str):
        return text

    # If the input is None, NaN, or pd.NA, treat it as null and return an empty string.
    if pd.isna(text):
        return '' # Empty string for null input

    # For all other types (e.g., int, float, bool, datetime, etc.),
    # convert to string using str(). This ensures consistent string output.
    # Example: 1.23 becomes "1.23", True becomes "True"
    return str(text)


def remove_non_printable_ascii(text: str) -> str:
    """
    Remove all non-printable ASCII characters from the input string.

    This includes control characters and special formatting codes outside the
    standard printable ASCII range. Useful for sanitizing strings from logs,
    user inputs, or external files where hidden or corrupted characters may exist.

    Handles None and non-string inputs gracefully by converting them to strings.

    Args:
        text (str): The input string to sanitize.

    Returns:
        str: A cleaned string containing only printable ASCII characters.
    """
    text = normalize_to_string(text)
    printable = set(string.printable)
    return ''.join(ch for ch in text if ch in printable)


def normalize_spaces(text: str) -> str:
    """
    Normalize spacing by collapsing multiple spaces into one and trimming edges.

    This function replaces two or more consecutive space characters with a
    single space and removes leading and trailing spaces. It is useful for
    cleaning user input or text data with irregular spacing.

    Handles None and non-string inputs gracefully by converting them to strings.

    Args:
        text (str): The input string to normalize.

    Returns:
        str: A string with normalized spacing (single spaces between words).
    """
    text = normalize_to_string(text)
    return MULTIPLE_SPACES_REGEX.sub(SPACE_CHAR, text).strip()


def remove_standard_spaces(text: str) -> str:
    """
    Removes all standard ASCII space characters (U+0020) from the input string.

    This function deletes only the standard space character (' ', Unicode U+0020),
    while preserving all other characters, including non-ASCII whitespace such as
    tabs ('\\t'), newlines ('\\n'), carriage returns ('\\r'), and other Unicode
    space characters (e.g., non-breaking space, em-space).

    Handles None and non-string inputs gracefully by converting them to strings.

    Args:
        text (str): The input string from which standard space characters will be removed.

    Returns:
        str: A string with all standard ASCII space characters removed; all other characters remain unchanged.
    """
    text = normalize_to_string(text)
    return text.replace(SPACE_CHAR, EMPTY_STRING)


def remove_all_whitespace(text: str) -> str:
    """
    Remove all whitespace characters from the input string.

    This function eliminates all types of Unicode whitespace characters, including
    spaces (' '), tabs ('\\t'), newlines ('\\n'), carriage returns ('\\r'),
    vertical tabs ('\\v'), and form feeds ('\\f'). It is useful for compacting
    a string or preparing it for strict formatting or validation.

    Handles None and non-string inputs gracefully by converting them to strings.

    Args:
        text (str): The input string to clean.

    Returns:
        str: A string with all whitespace characters removed.
    """
    text = normalize_to_string(text)
    return WHITE_SPACE_REGEX.sub(EMPTY_STRING, text)
