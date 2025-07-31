"""
Unit tests for text sanitization utility functions.

This module verifies the correctness of core text cleaning helpers from
`src.utils.text_sanitizer`, including functions to:
 - Remove non-printable ASCII characters
 - Normalize internal and surrounding space characters
 - Strip all standard space characters
 - Eliminate all types of whitespace (tabs, newlines, etc.)

These tests ensure robust and consistent preprocessing behavior across a variety
of user input formats and edge cases.

Example Usage:
 > python -m unittest tests/utils/test_text_sanitizer.py
 > from src.utils.text_sanitizer import strip_non_printable_ascii

Dependencies:
 - Python >= 3.9
 - Standard Library: unittest, string

Notes:
 - Designed for integration with CI pipelines or local test workflows.
 - Assumes utility functions are pure and deterministic for given inputs.

License:
 - Internal Use Only
"""
import string
import unittest
import pandas as pd
import src.utils.text_sanitizer as sanitizer


class TestTextSanitizer(unittest.TestCase):

    def test_normalize_to_string(self):
        """
        Tests normalization of arbitrary input values to valid string representations.

        Validates that `normalize_to_string`:
         - Returns an empty string for None
         - Leaves string input unchanged
         - Converts integers, floats, booleans, lists, dicts, and other types to their string representation

        This ensures the function can safely be used in preprocessing pipelines
        that assume consistent string input.
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
            with self.subTest(input=repr(input_value)):
                result = sanitizer.normalize_to_string(input_value)
                self.assertEqual(result, expected_output)

    def test_remove_non_printable_ascii(self):
        """
        Tests removal of non-printable ASCII characters from input strings.

        Ensures that the `strip_non_printable_ascii` function removes all ASCII control
        characters (except those that are considered printable like \n and \t), while
        preserving all valid printable characters.
        """
        # Get all non-printable ASCII characters (excluding those in string.printable)
        non_printable = ''.join(
            chr(i) for i in list(range(0, 32)) + [127]
            if chr(i) not in string.printable
        )

        test_cases = [
            ("Hello, World!", "Hello, World!"),
            ("Hello\x00World", "HelloWorld"),
            ("Clean\x07Text", "CleanText"),
            ("\x01\x02Test\x03\x04", "Test"),
            ("Normal \n Tab\t", "Normal \n Tab\t"),
            ("Valid123!@#\x1F\x7F", "Valid123!@#"),
            ("", ""),
            ("\x00\x01\x02", ""),
            (string.ascii_letters, string.ascii_letters),
            (string.digits, string.digits),
            (string.punctuation, string.punctuation),
            (string.whitespace, string.whitespace),
            (non_printable, ""),
        ]

        for input_text, expected_output in test_cases:
            with self.subTest(input_text=repr(input_text)):
                actual = sanitizer.remove_non_printable_ascii(input_text)
                self.assertEqual(actual, expected_output)

    def test_normalize_spaces(self):
        """
        Tests normalization of excessive internal and surrounding spaces.

        Verifies that `normalize_spaces` collapses multiple internal spaces into a
        single space and trims leading/trailing spaces, preserving word order and
        content integrity.
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

        for input_text, expected_output in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(sanitizer.normalize_spaces(input_text), expected_output)

    def test_remove_standard_spaces(self):
        """
        Validates that only standard ASCII space characters (U+0020) are removed from the input string.

        This test ensures that the `remove_standard_spaces` function eliminates all instances
        of the standard space character (' '), while preserving all other characters — including
        tabs ('\\t'), newlines ('\\n'), carriage returns, and any non-ASCII whitespace or symbols.

        The test covers edge cases such as empty strings, strings with no spaces, strings with
        leading, trailing, and internal spaces, as well as strings containing mixed whitespace types.
        """
        test_cases = [
            ("", ""),
            ("NoSpacesHere", "NoSpacesHere"),
            ("     ", ""),
            ("Line\twith\nspaces and\tothers", "Line\twith\nspacesand\tothers"),
            ("  leading and trailing  ", "leadingandtrailing"),
            ("Multiple   internal   spaces", "Multipleinternalspaces"),
            ("Tēxt wīth spāces", "Tēxtwīthspāces"),
        ]

        for input_text, expected_output in test_cases:
            with self.subTest(input_text=input_text):
                actual = sanitizer.remove_standard_spaces(input_text)
                self.assertEqual(actual, expected_output)

    def test_remove_all_whitespace(self):
        """
        Tests complete removal of all forms of whitespace from input strings.

        Ensures that `remove_all_whitespace` strips out spaces, tabs, newlines,
        carriage returns, form feeds, and vertical tabs, leaving only non-whitespace content.
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

        for input_text, expected_output in test_cases:
            with self.subTest(input_text=input_text):
                self.assertEqual(sanitizer.remove_all_whitespace(input_text), expected_output)


if __name__ == "__main__":
    unittest.main()
