import os
import shutil
import stat
import tempfile
import unittest

import pandas as pd
import src.utils.excel as excel


class TestMapExcelSheetsToStringDataFrames(unittest.TestCase):
    """
    Unit tests for the `map_excel_sheets_to_string_dataframes` function.

    This test verifies that:
      1) All sheets are read and returned in a dict keyed by sheet name
      2) All cell values are preserved as strings (including blanks as "")
      3) Cell-by-cell values match what was written
    """

    def setUp(self):
        """Create a temporary directory for test artifacts."""
        self.tmpdir = tempfile.mkdtemp(prefix="excel_to_dict_")

    def tearDown(self):
        """Clean up all temporary artifacts created by the tests."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_multi_sheet_map(self):
        """
        Should read multiple sheets and return DataFrames with all values as strings.
        """
        # ARRANGE
        # Sheet A: single column with mixed types and an empty string
        name_a = "SheetA"
        data_a = [
            True,  # Boolean
            42,  # Integer
            3.14159,  # Float
            "",  # Empty string
            "Hello",  # String
            "2025-08-08",  # Date-like string
        ]

        # Sheet B: 2D rows with mixed types, includes an empty string cell
        name_b = "SheetB"
        data_b = [
            [
                False,  # Boolean
                -987,  # Negative integer
                0.000123,  # Small float
                "World",  # String
                "$99.99",  # Currency-like string
            ],
            ["Extra", 123, "$9.99", "", "#$%"],  # Row 2
        ]

        # Create DataFrames to write (headers are kept so pandas reads them cleanly)
        df_a = pd.DataFrame(data_a)  # -> 1 column
        df_b = pd.DataFrame(data_b)  # -> 5 columns

        # Expected raw data by sheet (will compare after string-conversion)
        expected = {name_a: data_a, name_b: data_b}

        # Write the workbook with two sheets
        file_path = os.path.join(self.tmpdir, "sample.xlsx")
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df_a.to_excel(writer, sheet_name=name_a, index=False)
            df_b.to_excel(writer, sheet_name=name_b, index=False)

        # ACT
        # Open as ExcelFile and pass the *open workbook* into the function
        with pd.ExcelFile(file_path, engine="openpyxl") as workbook:
            result = excel.map_excel_sheets_to_string_dataframes(workbook)

        # ASSERT
        # Compare keys (sheet names) and flattened values as strings
        for (result_key, result_value), (expected_key, expected_value) in zip(result.items(), expected.items()):
            with self.subTest(Out=result_key, Exp=expected_key):
                self.assertEqual(result_key, expected_key)
            # Flatten and compare all values cell-by-cell as strings
            flat_result_value = result_value.to_numpy().flatten().tolist()
            flat_expected_value = pd.DataFrame(expected_value).to_numpy().flatten().astype(str).tolist()
            for result, expected in zip(flat_result_value, flat_expected_value):
                with self.subTest(Out=result, Exp=expected):
                    self.assertEqual(result, expected)

    def test_not_excel_file(self):
        """
        Should raise an Exception if the input is not a `pd.ExcelFile` instance.
        """
        # ARRANGE
        bad_inputs = [
            None,  # Empty
            123,  # int
            "path.xlsx",  # str
            pd.DataFrame({"A": [1]}),  # DataFrame
        ]
        expected = True  # True means an exception was raised

        # ACT & ASSERT
        for bad in bad_inputs:
            try:
                excel.map_excel_sheets_to_string_dataframes(bad)  # type: ignore[arg-type]
                result = False  # No exception → failure case
            except AttributeError:
                result = True  # Exception occurred → success case

            # Use subTest to show which input failed, using your Out/Exp format
            with self.subTest(In=type(bad).__name__, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestReadExcelFile(unittest.TestCase):
    """
    Unit test for the `read_excel_file` function.

    This test ensures that:
      - An Excel file with multiple sheets is correctly read into DataFrames with all columns as strings.
      - The function raises a RuntimeError when given an invalid file path.
    """

    def setUp(self):
        """
        Create a temporary Excel file for testing.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="read_excel_")

    def tearDown(self):
        """
        Clean up the temporary directory.
        """
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_reads_excel_and_returns_dict(self):
        """
        Should read the Excel file and return a dict of DataFrames with all string values.
        """
        # ARRANGE
        # Create sample sheet names and mixed-type data for testing
        name_a = "SheetA"
        data_a = [
            True,  # Boolean
            42,  # Integer
            3.14159,  # Float
            "",  # Empty string
            "Hello",  # String
            "2025-08-08"  # Date-like string
        ]

        name_b = "SheetB"
        data_b = [
            [
                False,  # Boolean
                -987,  # Negative integer
                0.000123,  # Small float
                "World",  # String
                "$99.99"  # Currency-like string
            ],
            ["Extra", 123, 4.56, "$9.99", ""]  # Row 2
        ]

        # Convert lists into DataFrames for writing to Excel
        df_a = pd.DataFrame(data_a)
        df_b = pd.DataFrame(data_b)

        # Expected dictionary mapping sheet names to raw data lists
        expected = {name_a: data_a, name_b: data_b}

        # Create a temporary Excel file with the above sheets
        file_path = os.path.join(self.tmpdir, "sample.xlsx")
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df_a.to_excel(writer, sheet_name=name_a, index=False)
            df_b.to_excel(writer, sheet_name=name_b, index=False)

        # ACT
        # Call the function under test
        result = excel.read_excel_file(file_path)

        # ASSERT
        # Compare keys (sheet names) and flattened values as strings
        for (result_key, result_value), (expected_key, expected_value) in zip(result.items(), expected.items()):
            with self.subTest(Out=result_key, Exp=expected_key):
                self.assertEqual(result_key, expected_key)

                # Flatten and compare all values cell-by-cell as strings
                flat_result_value = result_value.to_numpy().flatten().tolist()
                flat_expected_value = pd.DataFrame(expected_value).to_numpy().flatten().astype(str).tolist()
                for result, expected in zip(flat_result_value, flat_expected_value):
                    with self.subTest(Out=result, Exp=expected):
                        self.assertEqual(result, expected)

    def test_invalid_path_raises_runtime_error(self):
        """
        Should raise RuntimeError when given a non-existent file path.
        """
        # ARRANGE
        invalid_path = os.path.join(self.tmpdir, "non_existent.xlsx")
        expected_error = RuntimeError.__name__

        # ACT
        try:
            excel.read_excel_file(invalid_path)
            result = None  # No exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestSanitizeSheetName(unittest.TestCase):
    """
    Unit test for the `sanitize_sheet_name` function.

    This test ensures that Excel sheet names are correctly sanitized to:
      - Remove disallowed characters
      - Truncate to a maximum length of 31 characters
      - Convert any non-string input to a string
    """

    def test_various_inputs(self):
        """
        Should sanitize names by removing invalid characters, truncating to 31 chars,
        and converting non-string inputs to strings.
        """
        # ARRANGE
        test_cases = [
            # (Input, Expected)
            ("ValidName", "ValidName"),
            ("NameWith:Colon", "NameWithColon"),
            ("Slash/Question?Star*", "SlashQuestionStar"),
            ("Brackets[Name]", "BracketsName"),
            ("A" * 35, "A" * 31),  # Longer than 31 chars → truncate
            (12345, "12345"),  # Non-string input → str conversion
            ("Mix:Of/All?*Chars[Here]", "MixOfAllCharsHere"),
        ]

        for input_val, expected in test_cases:
            # ACT
            result = excel.sanitize_sheet_name_for_excel(input_val)

            # ASSERT
            with self.subTest(In=input_val, Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestWriteFrameToExcel(unittest.TestCase):
    """
    Unit test for the `write_frame_to_excel` function.

    Purpose:
      - Verify that a DataFrame is written to an `.xlsx` file without the index column.
      - Verify that failures during write are wrapped into `RuntimeError` with context.

    Scope:
      - Focuses on input → output behavior (file created and readable) as written in the function:
        * Uses openpyxl engine
        * Does not write the index
        * Wraps any exception into RuntimeError

      - Assumes valid DataFrame inputs (per instructions). No mocking is used.
    """

    def setUp(self):
        """Create a temporary directory for writing files."""
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base = self.tmpdir.name

        # Sample, realistic DataFrame (mixed types, including an empty string)
        self.df = pd.DataFrame(
            {
                "Part": ["R1", "C2", "U3"],
                "Value": ["10k", "1uF", "LM7805"],
                "Qty": [10, 5, 1],
            }
        )

    def tearDown(self):
        """Clean up temporary files and directory."""
        self.tmpdir.cleanup()

    def test_write_roundtrip(self):
        """
        Should write an Excel file and allow reading it back with identical content.
        """
        # ARRANGE
        out_path = os.path.join(self.base, "bom.xlsx")
        expected_columns = list(self.df.columns)  # index should NOT be written as a column

        # ACT
        # Execute the function under test
        excel.write_frame_to_excel(out_path, self.df)

        # Read the file back to validate outcomes (independent verification)
        with (pd.ExcelFile(out_path, engine="openpyxl") as workbook):
            read_back = pd.read_excel(workbook)

        # ASSERT
        # 1) File existence
        exists = os.path.exists(out_path)
        with self.subTest(Out=exists, Exp=True):
            self.assertTrue(exists)

        # 2) Column headers should match original (no index column present)
        with self.subTest(Out=list(read_back.columns), Exp=expected_columns):
            self.assertEqual(list(read_back.columns), expected_columns)

        # 3) Row count should match
        with self.subTest(Out=len(read_back), Exp=len(self.df)):
            self.assertEqual(len(read_back), len(self.df))

        # 4) Cell-by-cell content equality
        # Flatten and compare all values cell-by-cell as strings
        result_value = read_back.astype(str).values
        expected_value = self.df.astype(str).values
        flat_result_value = result_value.flatten().tolist()
        flat_expected_value = pd.DataFrame(expected_value).to_numpy().flatten().astype(str).tolist()
        for result, expected in zip(flat_result_value, flat_expected_value):
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_invalid_directory_raises_runtime_error(self):
        """
        Should raise RuntimeError when the target directory does not exist.
        """
        # ARRANGE
        # Path points to a non-existent subdirectory; pandas/openpyxl won't create parent dirs.
        bad_path = os.path.join(self.base, "no_such_dir", "out.xlsx")
        expected = RuntimeError.__name__

        # ACT
        try:
            excel.write_frame_to_excel(bad_path, self.df)
            result = None  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestWriteSheetsToExcel(unittest.TestCase):
    """
    Unit tests for the `write_sheets_to_excel` function.

    Verifies that:
      - Multiple DataFrames round-trips correctly to separate worksheets.
      - Non-empty DataFrames are written; empty ones are skipped.
      - Sheet names are sanitized as per `sanitize_sheet_name_for_excel`.
      - Default sheet name is assigned when sheet name is not provided.
      - Non-string `file_path` raises RunTimeError.
      - Empty input data raises RunTimeError.
      - Overwrite behavior: `overwrite=False` raises RunTimeError; `overwrite=True` succeeds.
    Scope:
      - Tests observable input→output behavior only (files, sheet names, cell values).
      - No mocks; relies on pandas/openpyxl reading to validate results.
    """

    def setUp(self):
        """
        Create a temp workspace and sample DataFrames.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="excel_write_dict_win_")
        self.base = self.tmpdir
        self.out_path = os.path.join(self.base, "out.xlsx")

        # Realistic DataFrames
        self.df_a = pd.DataFrame({"id": [1, 2], "name": ["alpha", "beta"]})
        self.df_b = pd.DataFrame({"k": [10, 20, 30], "v": [0.1, 0.2, 0.3]})
        self.df_empty = pd.DataFrame()  # completely empty (no cols, no rows)
        self.df_empty_rows = pd.DataFrame(columns=["A", "B"])  # no rows
        self.df_empty_cols = pd.DataFrame()  # no rows, no cols

    def tearDown(self):
        """
        Clean up temp workspace.
        """
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_writes_multiple_sheets(self):
        """
        Should write multiple DataFrames, one per sheet, applying Excel-safe sheet names.
        """
        # ARRANGE
        # Include some nasty/long names to exercise sanitization
        bad_name = "Bracket:[/\\?*]ets"  # contains invalid chars
        long_name = "A" * 40  # > 31 chars
        mix_name = "Sales:Q1/2025?*"  # mixed invalid chars

        sheets = {
            "OK": self.df_a,
            bad_name: self.df_b,
            long_name: self.df_a,
            mix_name: self.df_b,
        }

        out_path = os.path.join(self.tmpdir, "multi.xlsx")

        expected_written_sheets = {
            "OK": self.df_a,
            excel.sanitize_sheet_name_for_excel(bad_name): self.df_b,
            excel.sanitize_sheet_name_for_excel(long_name): self.df_a,
            excel.sanitize_sheet_name_for_excel(mix_name): self.df_b,
        }

        # ACT
        excel.write_sheets_to_excel(out_path, sheets, overwrite=False)

        # ASSERT: file exists
        exists = os.path.isfile(out_path)
        with self.subTest(Out=exists, Exp=True):
            self.assertTrue(exists)

        # ASSERT: verify sheet names and data via round-trip

        with pd.ExcelFile(out_path, engine="openpyxl") as xls:
            actual_sheet_names = tuple(xls.sheet_names)
            expected_sheet_names = tuple(expected_written_sheets.keys())

            with self.subTest(Out=actual_sheet_names, Exp=expected_sheet_names):
                self.assertEqual(actual_sheet_names, expected_sheet_names)

            # Validate each sheet’s content
            for sheet_name, expected_df in expected_written_sheets.items():
                with pd.ExcelFile(out_path, engine="openpyxl") as workbook:
                    read_df = pd.read_excel(workbook, sheet_name=sheet_name)
                equal = read_df.equals(expected_df)
                with self.subTest(Sheet=sheet_name, Out=equal, Exp=True):
                    self.assertTrue(equal)

    def test_skips_empty_frames_but_writes_nonempty(self):
        """
        Should skip empty DataFrames; only non-empty sheets are created.
        """
        # ARRANGE
        sheets_in = {
            "NonEmpty": self.df_a,
            "EmptyRows": self.df_empty_rows,
            "EmptyCols": self.df_empty_cols,
        }
        expected = ValueError.__name__

        try:
            # ACT
            excel.write_sheets_to_excel(self.out_path, sheets_in, overwrite=True)
            result = None
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_falsy_sheet_name_uses_pandas_default(self):
        """
        Should allow a falsy sheet name (e.g., "") and let pandas assign a default like 'Sheet1'.
        """
        # ARRANGE
        sheets_in = {"": self.df_a}  # falsy key triggers default name
        expected_default = "Sheet1"  # pandas default when no name provided and first sheet

        # ACT
        excel.write_sheets_to_excel(self.out_path, sheets_in, overwrite=True)
        with pd.ExcelFile(self.out_path, engine="openpyxl") as xl:
            sheet_names = xl.sheet_names

        # ASSERT
        # Only one sheet should exist and be pandas default 'Sheet1'
        with self.subTest(Out=len(sheet_names), Exp=1):
            self.assertEqual(len(sheet_names), 1)
        with self.subTest(Out=sheet_names[0], Exp=expected_default):
            self.assertEqual(sheet_names[0], expected_default)

    def test_non_string_path(self):
        """
        Should raise RunTimeError when `file_path` is not a string (delegated validation).
        """
        # ARRANGE
        inputs = [None, 123, 4.5, ["x.xlsx"], {"p": "x.xlsx"}]
        sheets = {"OK": self.df_a}
        expected = RuntimeError.__name__

        for val in inputs:
            # ACT
            try:
                excel.write_sheets_to_excel(val, sheets)  # type: ignore[arg-type]
                result = None
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(In=val, Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_empty_input(self):
        """
        Should raise ValueError when the input dict is empty.
        """
        # ARRANGE
        sheets_in: dict[str, pd.DataFrame] = {}  # Empty
        expected = ValueError.__name__

        # ACT
        try:
            excel.write_sheets_to_excel(self.out_path, sheets_in, overwrite=True)
            result = None
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_all_empty_after_filter(self):
        """
        Should raise ValueError when all provided DataFrames are empty after filtering.
        """
        # ARRANGE
        out_path = os.path.join(self.tmpdir, "nothing.xlsx")
        sheets = {"E1": self.df_empty, "E2": self.df_empty_cols}
        expected = ValueError.__name__

        # ACT
        try:
            excel.write_sheets_to_excel(out_path, sheets)
            result = None
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_overwrite_false(self):
        """
        Should raise RunTimeError when file exists and overwrite=False.
        """
        # ARRANGE
        out_path = os.path.join(self.tmpdir, "exists.xlsx")
        # Create initial workbook
        excel.write_sheets_to_excel(out_path, {"OK": self.df_a}, overwrite=False)
        self.assertTrue(os.path.isfile(out_path))

        expected = RuntimeError.__name__

        # ACT
        try:
            excel.write_sheets_to_excel(out_path, {"OK": self.df_b}, overwrite=False)
            result = None
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_overwrite_true(self):
        """
        Should succeed when file exists and overwrite=True, replacing contents.
        """
        # ARRANGE
        out_path = os.path.join(self.tmpdir, "rewrite.xlsx")
        excel.write_sheets_to_excel(out_path, {"OK": self.df_a}, overwrite=False)
        self.assertTrue(os.path.isfile(out_path))

        # ACT
        excel.write_sheets_to_excel(out_path, {"OK": self.df_b}, overwrite=True)

        # ASSERT: verify content replaced
        with pd.ExcelFile(out_path, engine="openpyxl") as workbook:
            read_back = pd.read_excel(workbook, sheet_name="OK")
        equal = read_back.equals(self.df_b)
        with self.subTest(Out=equal, Exp=True):
            self.assertTrue(equal)

    def test_write_to_read_only_file(self):
        """
        Should raise RunTimeError when attempting to overwrite a read-only Excel file.
        """
        # ARRANGE
        ro_path = os.path.join(self.tmpdir, "readonly.xlsx")

        # Create initial file, then mark read-only
        excel.write_sheets_to_excel(ro_path, {"OK": self.df_a}, overwrite=False)
        os.chmod(ro_path, stat.S_IREAD)  # set read-only attribute

        expected = RuntimeError.__name__

        # ACT
        try:
            # This attempts to open in 'x' or 'w' mode depending on overwrite (use True to focus the overwrite path)
            excel.write_sheets_to_excel(ro_path, {"OK": self.df_b}, overwrite=True)
            result = None
        except Exception as e:
            result = type(e).__name__
        finally:
            # Restore permissions to allow cleanup
            try:
                os.chmod(ro_path, stat.S_IWRITE | stat.S_IREAD)
            finally:
                pass

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
