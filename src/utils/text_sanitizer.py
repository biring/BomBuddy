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

License:
 - Internal Use Only
"""

import re
import pandas as pd

# CHARACTER CONSTANTS
EMPTY_STRING = ''  # No character
SPACE_CHAR = ' '  # One space character

# REGULAR EXPRESSIONS
WHITE_SPACE_REGEX = re.compile(r'\s+')  # Matches all Unicode whitespace characters (space, tab, newline, etc.)
MULTIPLE_SPACES_REGEX = re.compile(r' {2,}')  # Matches two or more consecutive space characters


def normalize_to_string(text) -> str:
    """
    Converts any input value into a valid string representation.

    Returns an empty string for null-like inputs (None, NaN, pd.NA, pd.NaT),
    preserves strings unchanged, and uses `str()` for all other data types.
    This normalization step ensures consistent and safe string input for
    downstream sanitization and parsing routines.

    Args:
        text (Any): Input value to normalize. Can be a string, None, float, int,
                    boolean, pandas NA/NaT, or any other type.

    Returns:
        str: Normalized string representation of the input, or an empty string if input is null-like.
    """
    # If the input is already a string, return it unchanged.
    if isinstance(text, str):
        return text

    # If the input is None, NaN, or pd.NA, treat it as null and return an empty string.
    if pd.isna(text):
        return ''  # Empty string for null input

    # For all other types (e.g., int, float, bool, datetime, etc.),
    # convert to string using str(). This ensures consistent string output.
    # Example: 1.23 becomes "1.23", True becomes "True"
    return str(text)


def normalize_spaces(text: str) -> str:
    """
    Collapses multiple consecutive spaces and trims surrounding whitespace.

    Replaces two or more adjacent ASCII space characters (' ') with a single space,
    and removes any leading or trailing spaces. Does not affect tabs, newlines, or
    other non-space whitespace characters.

    Useful for normalizing user input or cleaning up text with inconsistent spacing.

    Args:
        text (str): The input string containing irregular spacing.

    Returns:
        str: A cleaned string with single spaces between words and no leading/trailing spaces.
    """
    return MULTIPLE_SPACES_REGEX.sub(SPACE_CHAR, text).strip()


def remove_all_whitespace(text: str) -> str:
    """
    Removes all Unicode whitespace characters from the input string.

    This includes standard ASCII spaces (' '), tabs ('\\t'), newlines ('\\n'),
    carriage returns ('\\r'), vertical tabs ('\\v'), and form feeds ('\\f'),
    as well as any other Unicode-defined whitespace. Useful for compacting
    strings or preparing them for strict formatting or comparison.

    Args:
        text (str): The input string to clean.

    Returns:
        str: The input string with all whitespace characters removed.
    """
    return WHITE_SPACE_REGEX.sub(EMPTY_STRING, text)
