"""
Unit tests for text sanitization utility functions.

This module verifies the correctness of core text cleaning helpers from
`src.utils.text_sanitizer`. These tests ensure robust and consistent preprocessing
behavior across a variety of input types and edge cases.

Main capabilities tested:
 - `normalize_to_string`: Converts arbitrary inputs into safe string representations
 - `normalize_spaces`: Collapses multiple spaces and trims excess spacing
 - `remove_all_whitespace`: Removes all types of whitespace from a string

Example Usage:
    # From project root:
    python -m unittest tests/utils/test_text_sanitizer.py

Dependencies:
 - Python >= 3.9
 - Standard Library: unittest
 - External: pandas

Notes:
 - Assumes all utility functions are pure and deterministic.
 - Intended for use in automated test pipelines and local test runs.
 - Aligns with the public API exposed by `src.utils`.

License:
 - Internal Use Only
"""

import unittest
import pandas as pd
from src.utils import normalize_spaces, normalize_to_string, remove_all_whitespace


class TestTextSanitizer(unittest.TestCase):

    def test_normalize_to_string(self):
        """
        Verifies string normalization across a variety of input types.

        Ensures that `normalize_to_string` consistently returns a valid string
        representation for common data types. Specifically:
         - Converts `None`, NaN, `pd.NA`, and `pd.NaT` to empty strings.
         - Preserves input strings unchanged.
         - Converts integers, floats, booleans, and other types using `str()`.

        This test validates that the function is safe to use in data preprocessing
        pipelines that require all values to be string-normalized.
        """
        test_cases = [
            (None, ""),
            (float("nan"), ""),  # Python NaN
            (pd.NA, ""),  # Pandas NA
            (pd.NaT, ""),  # Pandas Not-a-Time
            ("Already a string", "Already a string"),
            (12345, "12345"),
            (3.14, "3.14"),
            (True, "True"),
            (False, "False")
        ]

        for input_value, expected_output in test_cases:
            result = normalize_to_string(input_value)
            with self.subTest(In=input_value, Out=result, Exp=expected_output):
                self.assertEqual(result, expected_output)

    def test_normalize_spaces(self):
        """
        Tests normalization of spacing in input strings.

        Ensures that `normalize_spaces`:
        - Collapses two or more consecutive spaces into a single space.
        - Removes leading and trailing spaces.
        - Preserves the original word order and meaning.

        This test confirms the function is suitable for cleaning user input or
        normalizing inconsistent whitespace in text data.
        """
        test_cases = [
            ("", ""),
            ("NoExtraSpaces", "NoExtraSpaces"),
            ("  Leading spaces", "Leading spaces"),
            ("Trailing spaces   ", "Trailing spaces"),
            ("  Both ends  ", "Both ends"),
            ("Multiple   internal   spaces", "Multiple internal spaces"),
            ("Single space between words", "Single space between words"),
            ("   Mixed  case  and  spacing   ", "Mixed case and spacing"),
            ("     ", ""),  # Only spaces
            (" A  B   C    D ", "A B C D"),
        ]

        for input_value, expected_output in test_cases:
            result = normalize_spaces(input_value)
            with self.subTest(In=input_value, Out=result, Exp=expected_output):
                self.assertEqual(result, expected_output)

    def test_remove_all_whitespace(self):
        """
        Tests complete removal of all standard whitespace characters from strings.

        Verifies that `remove_all_whitespace` strips out all forms of whitespace,
        including:
         - Standard space (' ')
         - Tabs ('\\t')
         - Newlines ('\\n')
         - Carriage returns ('\\r')
         - Form feeds ('\\f')
         - Vertical tabs ('\\v')

        Confirms the function preserves only non-whitespace characters, making it
        suitable for aggressive text normalization use cases.
        """
        test_cases = [
            ("", ""),
            ("NoWhitespace", "NoWhitespace"),
            (" ", ""),
            ("\t", ""),
            ("\n", ""),
            ("\r", ""),
            ("\f", ""),
            ("\v", ""),
            (" \t\n\r\f\v", ""),  # all common whitespace
            ("A B\tC\nD\rE\fF\vG", "ABCDEFG"),
            ("  Compact   all \twhitespace \nnow\r", "Compactallwhitespacenow"),
            ("Ends with space ", "Endswithspace"),
            (" Starts with space", "Startswithspace"),
            ("  Surrounding  ", "Surrounding"),
            ("Mix of words\tand\nnewlines", "Mixofwordsandnewlines"),
        ]

        for input_value, expected_output in test_cases:
            result = remove_all_whitespace(input_value)
            with self.subTest(In=input_value, Out=result, Exp=expected_output):
                self.assertEqual(result, expected_output)


if __name__ == "__main__":
    unittest.main()
