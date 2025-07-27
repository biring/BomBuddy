"""
Unit tests for parser package _common.py module.

This test suite verifies helper functions for parsing semi-structured tabular data,
such as BOM (Bill of Materials) sheets, where headers may vary in row placement,
formatting, or completeness. These functions are key to resiliently detecting
headers, validating label presence, and extracting metadata or component tables.

Test coverage includes:
 - `_normalize_label_text` for whitespace, case, and control character cleanup
 - `_search_label_index` for normalized label position lookup
 - `find_row_with_most_label_matches` for fuzzy header row detection
 - `find_unmatched_labels_in_best_row` and `has_all_labels_in_a_row` for strict validation
 - `extract_header`, `extract_table`, `extract_label_value`, and `extract_row_cell`
 - `create_dict_from_row` and `flatten_dataframe` for metadata handling and export

These tests use synthetic DataFrames with edge cases, such as:
 - Non-printable or Unicode characters
 - Label/value mismatches
 - Empty frames and mixed data types

Example Usage:
 > python -m unittest tests.parsers.test__common

Dependencies:
 - Python >= 3.10
 - Standard Library: unittest
 - External: pandas

Notes:
 - Validates internal-use utilities that support robust BOM parsing
 - Designed to run against in-memory pandas DataFrames as typically produced by Excel/CSV readers
 - Relies on text normalization functions from `src.utils.text_sanitizer`

License:
 - Internal Use Only
"""

import unittest
import pandas as pd
from pandas.testing import assert_frame_equal

# noinspection PyProtectedMember
import src.parsers._common as common


class TestCreateDictFromRow(unittest.TestCase):
    """
    Verifying that keys are normalized and corresponding values are preserved as-is.
    """

    def test_basic(self):
        """
        Test normalization of standard column labels with extra whitespace.
        """
        # Test data
        df = pd.Series({
            " Component ": "MCU",
            "Qty": 2,
            " ": "#"
        })
        expected = {
            "component": "MCU",
            "qty": 2,
            "": "#"
        }
        # Run the function
        result = common.create_dict_from_row(df)
        # Check the result
        with self.subTest("Basic"):
            self.assertEqual(result, expected)

    def test_special_characters(self):
        """
        Test normalization of column labels containing line breaks and tabs.
        """
        # Test data
        df = pd.Series({
            "U/P \n(USD W/ VAT)": "$1.000",
            "Sub-Total\t(USD W/ VAT)": "$2.000"
        })
        expected = {
            "u/p(usdw/vat)": "$1.000",
            "sub-total(usdw/vat)": "$2.000"
        }
        # Run the function
        result = common.create_dict_from_row(df)
        # Check the result
        with self.subTest("Special Characters"):
            self.assertEqual(result, expected)

    def test_non_string_headers(self):
        """
        Test normalization of non-string headers like integers and None.
        """
        # Test data
        df = pd.Series({
            123: "A",
            None: "B"
        })
        expected = {
            "123.0": "A",  # pandas converts int column headers to float
            "nan": "B"  # None becomes NaN -> normalized to "nan"
        }
        # Run the function
        result = common.create_dict_from_row(df)
        # Check the result
        with self.subTest("Non-String Headers"):
            self.assertEqual(result, expected)

    def test_empty_row(self):
        """
        Test that an empty Series returns an empty dictionary.
        """
        # Test data
        df = pd.Series({})
        expected = {}
        # Run the function
        result = common.create_dict_from_row(df)
        # Check the result
        with self.subTest("Empty Row"):
            self.assertEqual(result, expected)


class TestExtractHeader(unittest.TestCase):
    """
    Unit tests for `extract_header`, verifying metadata section extraction
    above the BOM table and correct error handling when no match is found.
    """

    def test_successful_extraction(self):
        """
        Test correct extraction of metadata rows above the BOM header.
        """
        # Test data: first 2 rows are metadata, 3rd row is BOM header
        data = [
            ["Rev A", "", ""],
            ["Build: EVT", "", ""],
            ["Qty", "Part", "Value"],
            ["1", "R1", "10k"]
        ]
        df = pd.DataFrame(data)
        labels = ["qty", "part", "value"]

        # Expected result: rows above the BOM header
        expected = pd.DataFrame(data[:2])

        # Run the function
        result = common.extract_header(df, labels)

        # Check the result
        with self.subTest("Successful Extraction"):
            assert_frame_equal(result.reset_index(drop=True), expected)

    def test_empty_header_block_raises(self):
        """
        Test ValueError when header block is empty (header found in first row).
        """
        # Test data: header is in first row, so no metadata above
        data = [
            ["Qty", "Part", "Value"],
            ["1", "R1", "10k"]
        ]
        df = pd.DataFrame(data)
        labels = ["qty", "part", "value"]

        # Run the function and check that it raises ValueError (any message)
        with self.subTest("Empty Header Block"):
            with self.assertRaises(ValueError):
                common.extract_header(df, labels)

    def test_no_match_raises(self):
        """
        Test ValueError when no matching header row is found.
        """
        # Test data: no row matches the expected labels
        data = [
            ["Some", "Random", "Stuff"],
            ["Still", "Not", "BOM"]
        ]
        df = pd.DataFrame(data)
        labels = ["qty", "part", "value"]

        # Run the function and check that it raises ValueError (any message)
        with self.subTest("No Match Found"):
            with self.assertRaises(ValueError):
                common.extract_header(df, labels)


class TestExtractLabelValue(unittest.TestCase):
    """
    Unit tests for `extract_label_value`, verifying correct value extraction
    and proper error handling for unmatched or incomplete label-value pairs.
    """

    def test_successful_exact_match(self):
        """
        Test value extraction with a direct label match.
        """
        # Test data
        data = ["Part", "ABC123", "Qty", "5"]
        label = "Qty"
        expected = "5"

        # Run the function
        result = common.extract_label_value(data, label)

        # Check the result
        with self.subTest("Exact Match"):
            self.assertEqual(result, expected)

    def test_normalized_match(self):
        """
        Test matching with label formatting differences (case, spaces).
        """
        # Test data
        data = [" part number ", "XYZ", "Build\nStage", "EVT"]
        label = "build stage"
        expected = "EVT"

        # Run the function
        result = common.extract_label_value(data, label)

        # Check the result
        with self.subTest("Normalized Match"):
            self.assertEqual(result, expected)

    def test_label_not_found_returns_empty(self):
        """
        Test that missing label returns empty string without raising.
        """
        # Test data
        data = ["Part", "123", "Qty", "10"]
        label = "Revision"
        expected = ""

        # Run the function
        result = common.extract_label_value(data, label)

        # Check the result
        with self.subTest("Label Not Found"):
            self.assertEqual(result, expected)

    def test_label_found_but_no_value_raises(self):
        """
        Test that a label at the end of the list raises ValueError.
        """
        # Test data
        data = ["Rev", "A", "Build", "EVT", "Stage"]
        label = "Stage"

        # Run the function and expect ValueError
        with self.subTest("Label Found but No Value"):
            with self.assertRaises(ValueError):
                common.extract_label_value(data, label)

    def test_empty_input_returns_empty(self):
        """
        Test empty list input returns empty string.
        """
        # Test data
        data = []
        label = "Part"

        # Run the function
        result = common.extract_label_value(data, label)

        # Check the result
        with self.subTest("Empty Input"):
            self.assertEqual(result, "")


class TestExtractRowCell(unittest.TestCase):
    """
    Verifying header normalization, value extraction, and graceful handling of edge cases.
    """

    def test_exact_match(self):
        """
        Test extraction with exact column headers.
        """
        # Test data
        row = pd.Series({
            "Qty": '5',
            "Component": "MCU"
        })
        header = "Qty"
        expected = '5'
        # Run the function
        result = common.extract_row_cell(row, header)
        # Check the result
        with self.subTest("Exact Match"):
            self.assertEqual(result, expected)

    def test_normalized_header(self):
        """
        Test extraction with headers containing spaces, newlines, or case issues.
        """
        # Test data
        row = pd.Series({
            " Component\n ": "Diode",
            " quantity ": "10"
        })
        header = "\n component"
        expected = "Diode"
        # Run the function
        result = common.extract_row_cell(row, header)
        # Check the result
        with self.subTest("Normalized Header"):
            self.assertEqual(result, expected)

    def test_non_printable_header(self):
        """
        Test extraction where header contains non-printable ASCII characters.
        """
        # Test data
        row = pd.Series({
            "Val\u0000ue": "R23"
        })
        header = "VALUE"
        expected = "R23"
        # Run the function
        result = common.extract_row_cell(row, header)
        # Check the result
        with self.subTest("Non-Printable Header"):
            self.assertEqual(result, expected)

    def test_missing_column(self):
        """
        Test safe fallback to empty string when column is not found.
        """
        # Test data
        row = pd.Series({
            "Qty": 1
        })
        header = "Description"
        expected = ""
        # Run the function
        result = common.extract_row_cell(row, header)
        # Check the result
        with self.subTest("Missing Header"):
            self.assertEqual(result, expected)

    def test_none_value(self):
        """
        Test handling of None cell value.
        """
        # Test data
        row = pd.Series({
            "Component": None
        })
        header = "Component"
        expected = ""
        # Run the function
        result = common.extract_row_cell(row, header)
        # Check the result
        with self.subTest("None Cell Value"):
            self.assertEqual(result, expected)


class TestExtractTable(unittest.TestCase):
    """
    Unit tests for `extract_table`, verifying BOM table extraction
    and proper error handling for header detection failures.
    """

    def test_successful_extraction(self):
        """
        Test extracting table from header row onward.
        """
        # Test data: header in row 2
        data = [
            ["Doc ID", "Rev", "Name"],
            ["Build", "Stage", "Date"],
            ["Qty", "Part", "Value"],
            ["1", "R1", "10k"],
            ["2", "C1", "1uF"]
        ]
        df = pd.DataFrame(data)
        labels = ["qty", "part", "value"]

        # Expected result: all rows from index 2 and down
        expected = pd.DataFrame(data[2:])

        # Run the function
        result = common.extract_table(df, labels)

        # Check the result
        with self.subTest("Successful Extraction"):
            assert_frame_equal(
                result.reset_index(drop=True),
                expected.reset_index(drop=True)
            )

    def test_table_header_not_found_raises(self):
        """
        Test ValueError when BOM table header row is not found.
        """
        # Test data: no matching row
        data = [
            ["Title", "Date", "Author"],
            ["Config", "Settings", "Meta"]
        ]
        df = pd.DataFrame(data)
        labels = ["qty", "part", "value"]

        # Run the function and expect ValueError
        with self.subTest("No Header Found"):
            with self.assertRaises(ValueError):
                common.extract_table(df, labels)

    def test_extracted_table_is_empty_raises(self):
        """
        Test ValueError when header row is at the very end (no rows after it).
        """
        # Test data: header is the last row
        data = [
            ["Metadata", "", ""],
            ["Qty", "Part", "Value"]  # index 1
        ]
        df = pd.DataFrame(data)
        labels = ["qty", "part", "value"]

        # Run the function and expect ValueError
        with self.subTest("Empty Table"):
            with self.assertRaises(ValueError):
                common.extract_table(df, labels)

    def test_empty_dataframe_raises(self):
        """
        Test behavior when input DataFrame is empty.
        """
        # Test data: completely empty DataFrame
        df = pd.DataFrame()
        labels = ["qty", "part", "value"]

        # Run the function and expect ValueError
        with self.subTest("Empty DataFrame"):
            with self.assertRaises(ValueError):
                common.extract_table(df, labels)


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


class TestFlattenDataFrame(unittest.TestCase):
    """
    Unit tests for `flatten_dataframe`, validating header and cell flattening logic.
    """

    def test_simple_dataframe(self):
        """
        Test flattening a small DataFrame with no NaNs.
        """
        # Test data: 2 columns with 2 rows of non-null values
        df = pd.DataFrame({
            "A": [1, 2],
            "B": ["x", "y"]
        })

        # Expected output: list with column headers first, followed by row values in row-major order
        expected = ["A", "B", 1, "x", 2, "y"]

        # Run the function
        result = common.flatten_dataframe(df)

        # Check that output matches expected flat list
        with self.subTest("Simple DataFrame"):
            self.assertEqual(result, expected)

    def test_nan_handling(self):
        """
        Test that NaNs in the DataFrame are replaced with EMPTY_CELL_REPLACEMENT.
        """
        # Test data: DataFrame with None and NaN values in different positions
        df = pd.DataFrame({
            "Col1": [None, "data"],
            "Col2": [3.14, None]
        })

        # Expected output: NaNs replaced with EMPTY_CELL_REPLACEMENT, headers included at start
        expected = ["Col1", "Col2", common.EMPTY_CELL_REPLACEMENT, 3.14, "data", common.EMPTY_CELL_REPLACEMENT]

        # Run the function
        result = common.flatten_dataframe(df)

        # Validate flattened list has NaNs replaced properly and data order preserved
        with self.subTest("NaN Replacement"):
            self.assertEqual(result, expected)

    def test_mixed_types(self):
        """
        Test flattening with a mix of integers, floats, and strings in DataFrame cells.
        """
        # Test data: Columns with integer, float, and string types
        df = pd.DataFrame({
            "Int": [1, 2],
            "Float": [1.1, 2.2],
            "Str": ["a", "b"]
        })

        # Expected output: headers followed by mixed-type values in row-major order
        expected = ["Int", "Float", "Str", 1, 1.1, "a", 2, 2.2, "b"]

        # Run the function
        result = common.flatten_dataframe(df)

        # Validate mixed data types are preserved and flattened correctly
        with self.subTest("Mixed Data Types"):
            self.assertEqual(result, expected)

    def test_empty_dataframe(self):
        """
        Test behavior when an empty DataFrame (no columns, no rows) is passed.
        """
        # Test data: completely empty DataFrame
        df = pd.DataFrame()

        # Expected result: empty list, since there are no headers or cell values
        expected = []

        # Run the function
        result = common.flatten_dataframe(df)

        # Ensure the result is an empty list
        with self.subTest("Empty DataFrame"):
            self.assertEqual(result, expected)

    def test_dataframe_with_index(self):
        """
        Test that DataFrame index values are not included in the flattened output.
        """
        # Test data: DataFrame with string index labels; these should be ignored
        df = pd.DataFrame({
            "X": [10, 20],
            "Y": ["foo", "bar"]
        }, index=["row1", "row2"])

        # Expected output: column headers + cell values only; index labels excluded
        expected = ["X", "Y", 10, "foo", 20, "bar"]

        # Run the function
        result = common.flatten_dataframe(df)

        # Confirm only headers and values are included, not index labels
        with self.subTest("Index Ignored"):
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


class TestHasAllLabelsInARow(unittest.TestCase):
    """
    Unit tests for `has_all_labels_in_a_row`, validating detection of all required labels
    present in a single row of the DataFrame.
    """

    def test_all_labels_in_single_row(self):
        """
        Test when all required labels are present in one row.
        """
        # Test data: row 2 contains all required labels
        df = pd.DataFrame([
            ["misc", "header", "stuff"],
            ["qty", "part", "value"],
            ["1", "R1", "10k"]
        ])
        required_labels = ["qty", "part", "value"]

        # Expected result: all labels found in row 1 (zero-based)
        expected = True

        # Run the function
        result = common.has_all_labels_in_a_row("TestSheet", df, required_labels)

        # Check the result
        with self.subTest("All Labels Present"):
            self.assertEqual(result, expected)

    def test_missing_one_label(self):
        """
        Test when only some of the required labels are present in the best row.
        """
        # Test data: only 'qty' and 'part' are present in the best row
        df = pd.DataFrame([
            ["qty", "part", "extra"],
            ["1", "R1", "X"]
        ])
        required_labels = ["qty", "part", "value"]

        # Expected result: False, since 'value' is missing
        expected = False

        # Run the function
        result = common.has_all_labels_in_a_row("PartialSheet", df, required_labels)

        # Check the result
        with self.subTest("Missing One Label"):
            self.assertEqual(result, expected)

    def test_labels_split_across_rows(self):
        """
        Test when all labels are present but split across multiple rows.
        """
        # Test data: each row has only a subset of labels
        df = pd.DataFrame([
            ["qty", "misc"],
            ["part", "extra"],
            ["value", "junk"]
        ])
        required_labels = ["qty", "part", "value"]

        # Expected result: False, since no single row contains all labels
        expected = False

        # Run the function
        result = common.has_all_labels_in_a_row("SplitSheet", df, required_labels)

        # Check the result
        with self.subTest("Split Across Rows"):
            self.assertEqual(result, expected)

    def test_empty_dataframe(self):
        """
        Test behavior when the DataFrame is empty.
        """
        # Test data: empty DataFrame with no rows
        df = pd.DataFrame()
        required_labels = ["qty", "part", "value"]

        # Expected result: False, nothing to match
        expected = False

        # Run the function
        result = common.has_all_labels_in_a_row("EmptySheet", df, required_labels)

        # Check the result
        with self.subTest("Empty DataFrame"):
            self.assertEqual(result, expected)

    def test_empty_required_labels(self):
        """
        Test behavior when no required labels are provided.
        """
        # Test data: any DataFrame
        df = pd.DataFrame([
            ["qty", "part", "value"]
        ])
        required_labels = []

        # Expected result: True (trivially satisfied)
        expected = True

        # Run the function
        result = common.has_all_labels_in_a_row("NoLabels", df, required_labels)

        # Check the result
        with self.subTest("Empty Required Labels"):
            self.assertEqual(result, expected)


class TestNormalizeLabelText(unittest.TestCase):
    """
    Unit tests for `_normalize_label_text`, verifying normalization of input text
    including stripping whitespace, removing non-printable characters, and converting to lowercase.
    """

    def test_whitespace_and_case(self):
        """
        Test normalization of text with mixed case and whitespace.
        """
        # Test data
        input_text = "  Part\nNumber\t "
        expected = "partnumber"
        # Run the function
        result = common._normalize_label_text(input_text)
        # Check the result
        with self.subTest("Whitespace and Case"):
            self.assertEqual(result, expected)

    def test_numeric_input(self):
        """
        Test normalization of numeric input.
        """
        # Test data
        input_text = 123.45
        expected = "123.45"
        # Run the function
        result = common._normalize_label_text(input_text)
        # Check the result
        with self.subTest("Numeric Input"):
            self.assertEqual(result, expected)

    def test_none_input(self):
        """
        Test normalization of None input.
        """
        # Test data
        input_text = None
        expected = ""
        # Run the function
        result = common._normalize_label_text(input_text)
        # Check the result
        with self.subTest("None Input"):
            self.assertEqual(result, expected)

    def test_non_printable_ascii(self):
        """
        Test removal of non-printable ASCII characters.
        """
        # Test data
        input_text = "U/P \n(USD \x00W/ VAT)"
        expected = "u/p(usdw/vat)"
        # Run the function
        result = common._normalize_label_text(input_text)
        # Check the result
        with self.subTest("Non-Printable ASCII"):
            self.assertEqual(result, expected)

    def test_clean_input(self):
        """
        Test that a clean, lowercase string is unchanged.
        """
        # Test data
        input_text = "value"
        expected = "value"
        # Run the function
        result = common._normalize_label_text(input_text)
        # Check the result
        with self.subTest("Clean Input"):
            self.assertEqual(result, expected)


class TestSearchLabelIndex(unittest.TestCase):
    """
    Unit tests for `_search_label_index`, validating normalized substring matching
    across candidate strings to identify index of a label.
    """

    def test_exact_match(self):
        """
        Test finding an exact match for a normalized label.
        """
        # Test data
        data = ["Component", "Quantity", "Value"]
        label = "Quantity"
        expected = 1
        # Run the function
        result = common._search_label_index(data, label)
        # Check the result
        with self.subTest("Exact Match"):
            self.assertEqual(result, expected)

    def test_substring_match(self):
        """
        Test matching when label is a substring in a normalized entry.
        """
        # Test data
        data = ["  Component (Type)", "Qty", "Nominal\nValue"]
        label = "component"
        expected = common.NO_MATCH_IN_LIST
        # Run the function
        result = common._search_label_index(data, label)
        # Check the result
        with self.subTest("Substring Match"):
            self.assertEqual(result, expected)

    def test_whitespace_and_case_insensitivity(self):
        """
        Test matching with varying cases, tabs, and newline formatting.
        """
        # Test data
        data = ["\tTotal Cost", "DESCRIPTION\n", "supplier\nname"]
        label = "description"
        expected = 1
        # Run the function
        result = common._search_label_index(data, label)
        # Check the result
        with self.subTest("Whitespace And Case Insensitive"):
            self.assertEqual(result, expected)

    def test_unicode_and_symbols(self):
        """
        Test label match when symbols or Unicode are present in data.
        """
        # Test data
        data = ["Ω Part ID", "⚙ Manufacturer", "Voltage (V)"]
        label = "manufacturer"
        expected = 1
        # Run the function
        result = common._search_label_index(data, label)
        # Check the result
        with self.subTest("Unicode And Symbols"):
            self.assertEqual(result, expected)

    def test_label_not_found(self):
        """
        Test fallback behavior when label is not present.
        """
        # Test data
        data = ["Qty", "Part", "Cost"]
        label = "Description"
        expected = common.NO_MATCH_IN_LIST
        # Run the function
        result = common._search_label_index(data, label)
        # Check the result
        with self.subTest("Not Found"):
            self.assertEqual(result, expected)

    def test_empty_data_list(self):
        """
        Test behavior when searching an empty list.
        """
        # Test data
        data = []
        label = "Qty"
        expected = common.NO_MATCH_IN_LIST
        # Run the function
        result = common._search_label_index(data, label)

        with self.subTest("Empty List"):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
