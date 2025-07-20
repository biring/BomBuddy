"""
Public interface for the utility package.

This package provides reusable utility functions for data preprocessing,
string sanitization, and formatting tasks.

Only explicitly exported functions are intended for external use. Internal
logic should remain encapsulated within their respective modules and should
not be imported directly.

Note:
    To ensure maintainability and encapsulation, always import utility functions
    from the `src.utils` package-level interface rather than from submodules.

    Preferred:
        from src.utils import remove_all_whitespace

    Avoid:
        from src.utils.text_sanitizer import remove_all_whitespace
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
