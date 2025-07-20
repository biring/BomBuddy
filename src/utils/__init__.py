"""
Public interfaces for the utility package.

This package provides reusable utility functions for data preprocessing,
string sanitization, and formatting.

Only explicitly exposed functions are available for external use; internal
logic should remain encapsulated within their respective modules and not
imported directly.

Intended usage:
    from src.utils import remove_all_whitespace

    import src.utils.text_sanitizer as sanitizer
    clean = sanitizer.remove_all_whitespace(raw_text)
"""

from .text_sanitizer import (
    normalize_spaces,
    normalize_to_string,
    remove_all_whitespace,
    remove_non_printable_ascii,
    remove_standard_spaces,
)

__all__ = [
    "normalize_spaces",
    "normalize_to_string",
    "remove_all_whitespace",
    "remove_non_printable_ascii",
    "remove_standard_spaces",
]

