"""
Unit tests for label matching utilities in _common.py.

This module tests the behavior of internal functions that:
 - Locate the DataFrame row with the highest number of normalized label matches
 - Identify unmatched labels from the best-matching row based on exact normalized match

Tests cover a wide range of scenarios, including:
 - Full, partial, and no matches
 - Case and whitespace-insensitive normalization
 - Edge cases like empty DataFrames and empty label lists

Example Usage:
 > python -m unittest tests.parsers.test_label_matching_utils

Dependencies:
 - Python >= 3.10
 - Standard Library: unittest
 - External: pandas

Notes:
 - These tests directly target internal-use functions prefixed with `_`
 - Designed for use with in-memory DataFrames typical of CSV parsing pipelines

License:
 - Internal Use Only
"""

import unittest
import pandas as pd

# noinspection PyProtectedMember
import src.parsers._common as common


class TestFindRowWithMostLabelMatches(unittest.TestCase):
    """
    Unit tests for the _find_row_with_most_label_matches function.

    This test suite verifies that the function correctly identifies the row index
    with the highest number of matching labels, accounting for perfect, partial,
    and no-match scenarios.
    """

    def test_perfect_match(self):
        """
        Tests that the correct row index is returned when one row matches all labels exactly.
        """
        # Test data
        df = pd.DataFrame([
            ["Hello"],
            ["Amount", "Date"],
            ["Account", "Amount", "Date"],
            ["acct", "amt", "dt"]
        ])
        labels = ["Account", "Amount", "Date"]
        expected = 2
        # Run the functions
        result = common.find_row_with_most_label_matches(df, labels)
        # Check the result
        with self.subTest("Perfect match"):
            self.assertEqual(result, expected)

    def test_partial_match(self):
        """
        Tests that the row with the highest number of partial matches is correctly identified.
        """
        # Test data
        df = pd.DataFrame([
            [],
            ["Amount", "Date", "Comment"],
            ["Name", "Amount", "Extra"],
            ["Account", "Value", "Comment"]
        ])
        labels = ["Account", "Amount", "Date"]
        expected = 1
        # Run the functions
        result = common.find_row_with_most_label_matches(df, labels)
        # Check the result
        with self.subTest("Partial match"):
            self.assertEqual(result, expected)

    def test_no_match(self):
        """
        Tests that the function returns NO_BEST_MATCH_ROW when no labels match any row.
        """
        # Test data
        df = pd.DataFrame([
            [],
            ["Empty"],
            ["Name", "Value", "Extra"],
            ["Other", "Misc", "Notes"]
        ])
        labels = ["Account", "Amount", "Date"]
        expected = common.NO_BEST_MATCH_ROW
        # Run the functions
        result = common.find_row_with_most_label_matches(df, labels)
        # Check the result
        with self.subTest("No match"):
            self.assertEqual(result, expected)


class TestGetUnmatchedLabelsFromBestRow(unittest.TestCase):
    """
    Unit tests for the _find_unmatched_labels_in_best_row function.

    This test suite verifies that unmatched labels are correctly identified
    from the row that best matches the input labels using normalized string matching.
    """

    def test_all_labels_matched_in_best_row(self):
        """
        Tests that an empty list is returned when all labels are matched in the best row.
        """
        # Test data
        df = pd.DataFrame([
            ["Hello"],
            ["X", "Y", "Z"],
            ["Account", "Amount", "Date"],
            ["Something", "Other"],
            []
        ])
        labels = ["account", "amount", "date"]
        expected = []
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("All labels matched in best row"):
            self.assertEqual(result, expected)

    def test_some_labels_unmatched_in_best_row(self):
        """
        Tests that only unmatched labels are returned when the best row partially matches.
        """
        # Test data
        df = pd.DataFrame([
            ["Name", "Amount", "Comment"],  # best match (2 out of 3)
            ["Other", "Misc"],
            ["Account", "Extra"]
        ])
        labels = ["account", "amount", "date"]
        expected = ["account", "date"]
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("Some labels unmatched in best row"):
            self.assertEqual(result, expected)

    def test_no_labels_matched(self):
        """
        Tests that all labels are returned when no row contains any matching label.
        """
        # Test data
        df = pd.DataFrame([
            ["Foo", "Bar"],
            ["Alpha", "Beta", "Gamma"],
            ["", "Nile"]
        ])
        labels = ["account", "amount"]
        expected = labels
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("No labels matched at all"):
            self.assertEqual(result, expected)

    def test_whitespace_and_case_insensitive_match(self):
        """
        Tests that label matching is case-insensitive and ignores surrounding whitespace.
        """
        # Test data
        df = pd.DataFrame([
            ["  AcCouNT\n", "  Amount ", "DaTe  "]
        ])
        labels = ["account", "amount", "date"]
        expected = []
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("Match with normalization"):
            self.assertEqual(result, expected)

    def test_empty_dataframe(self):
        """
        Tests that all labels are returned if the DataFrame is empty.
        """
        # Test data
        df = pd.DataFrame([])
        labels = ["account"]
        expected = labels
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("Empty DataFrame"):
            self.assertEqual(result, expected)

    def test_empty_labels(self):
        """
        Tests that an empty list is returned when the label list is empty.
        """
        # Test data
        df = pd.DataFrame([
            ["Account", "Amount", "Date"]
        ])
        labels = []
        expected = []
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("Empty label list"):
            self.assertEqual(result, expected)

    def test_nan_and_none_cells(self):
        """
        Tests that the function correctly handles None, NaN, and numeric values in the best-matching row.
        Verifies that only valid string cells are considered during label comparison.
        """
        # Test data
        df = pd.DataFrame([
            [None, float("nan"), 42],
            ["Account", "Amount", "Date"]
        ])
        labels = ["account", "amount", "date"]
        expected = []
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("Nan and None cells"):
            self.assertEqual(result, expected)

    def test_labels_with_whitespace_and_control_chars(self):
        """
        Tests that required labels with leading/trailing whitespace or control characters
        are correctly normalized and matched in the best-matching row.
        """
        # Test data
        df = pd.DataFrame([
            ["Account", "Amount", "Date"]
        ])
        labels = [" account\n", "  amount\t", "\x0bdate  "]
        expected = []
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("Labels with whitespaces and control characters"):
            self.assertEqual(result, expected)

    def test_large_dataframe_no_crash(self):
        """
        Tests that the function executes without errors on a large DataFrame (10,000 rows × 50 columns)
        and correctly returns all labels as unmatched when no cells match.
        This test is focused on performance and robustness.
        """
        # Test data
        # 10,000 rows, 50 columns — none matching
        df = pd.DataFrame([["col"] * 50] * 10000)
        labels = ["account", "amount", "date"]
        expected = labels
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        with self.subTest("Large dataframe no crash"):
            self.assertEqual(result, expected)

    def test_non_string_labels(self):
        """
        Tests that required labels with non-string types (e.g., int, None) are handled gracefully.
        Verifies that only the string-equivalent labels are matched and others are returned as unmatched.
        """
        # Test data
        df = pd.DataFrame([
            ["Account", "Amount", "Date"]
        ])
        labels = ["Account", 123, None]
        expected = [123, None]
        # Run the functions
        result = common.find_unmatched_labels_in_best_row(df, labels)
        # Check the result
        with self.subTest("Non string labels"):
            self.assertEqual(result, expected)  # "Account" should match, others won't