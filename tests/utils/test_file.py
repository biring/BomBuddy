"""
Unit tests for file system utility functions.

This test suite validates the behavior of functions in `src.utils.file` related to
file path construction, string escaping, file presence checks, and directory listing.

Test Coverage Includes:
 - Path construction and validation (e.g., `build_file_path`)
 - Backslash escaping for display (e.g., `escape_backslashes`)
 - File presence and type checking (e.g., `is_existing_file`)
 - Listing and filtering directory contents (e.g., `get_files_in_directory`)
 - Validation of file/folder names based on Windows filesystem rules (e.g., `is_valid_file_path`)

Example Usage:
    # Run unittest discovery from project root:
    python -m unittest tests.utils.test_file_utils

    # Run individual class:
    python -m unittest tests.utils.test_file_utils.TestBuildFilePath

Dependencies:
 - Python >= 3.9
 - Standard Library: os, shutil, tempfile, unittest
 - Internal module: src.utils.file

Notes:
 - Temporary directories and files are created per test class and cleaned up in `tearDown` to ensure isolation.
 - Platform-specific logic (Windows file naming) is tested with `os.name` checks.
 - All test methods follow the Arrange-Act-Assert pattern and use subTest for multiple test cases.

License:
 - Internal Use Only
"""

import unittest
import os
import tempfile
import shutil

import src.utils.file as file_util


class TestBuildFilePath(unittest.TestCase):
    """
    Unit test for the `build_file_path` function in the file utility module.

    This test validates that the function correctly joins directory and file names
    into a full path, handles leading/trailing whitespace, and raises errors for invalid input.
    """

    def test_valid_path_joining(self):
        """
        Should return correctly joined path when given valid folder and file names.
        """
        # ARRANGE
        folder = "  C:\\Users\\Test  "
        file = "  document.txt "
        expected = os.path.join("C:\\Users\\Test", "document.txt")

        # ACT
        result = file_util.build_file_path(folder, file)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_empty_folder(self):
        """
        Should raise ValueError if folder is an empty string.
        """
        # ARRANGE
        folder = "     "
        file = "data.csv"
        expected = ValueError.__name__

        # ACT
        try:
            file_util.build_file_path(folder, file)
            result = None
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_empty_file(self):
        """
        Should raise ValueError if file name is an empty string.
        """
        # ARRANGE
        folder = "/tmp"
        file = "   "
        expected = ValueError.__name__

        # ACT
        try:
            file_util.build_file_path(folder, file)
            result = None
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_non_string_inputs(self):
        """
        Should raise ValueError if inputs are not strings.
        """
        test_cases = [
            (None, "file.txt"),
            ("folder", None),
            (123, "file.txt"),
            ("folder", 456),
        ]
        expected = ValueError.__name__

        for folder, file in test_cases:
            try:
                file_util.build_file_path(folder, file)
                result = None
            except Exception as e:
                result = type(e).__name__

            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestEscapeBackslashes(unittest.TestCase):
    """
    Unit test for the `escape_backslashes` function in the file utility module.

    This test ensures that backslashes in file paths are correctly escaped for display or logging,
    and that the function raises TypeError when given invalid input types.
    """

    def test_escaped_backslashes(self):
        """
        Should convert all single backslashes to double backslashes.
        """
        # ARRANGE
        test_cases = [
            ("C:\\Users\\Name\\Documents", "C:\\\\Users\\\\Name\\\\Documents"),
            ("\\network\\drive\\share", "\\\\network\\\\drive\\\\share"),
            ("no\\ending\\slash\\", "no\\\\ending\\\\slash\\\\"),
            ("no_backslashes_here", "no_backslashes_here"),
        ]

        for input_path, expected in test_cases:
            # ACT
            result = file_util.escape_backslashes(input_path)

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_empty_string(self):
        """
        Should return an empty string when input is empty.
        """
        # ARRANGE
        input_path = ""
        expected = ""

        # ACT
        result = file_util.escape_backslashes(input_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_type(self):
        """
        Should raise TypeError for non-string input types.
        """
        test_cases = [None, 123, 3.14, ["C:\\file.txt"], {"path": "C:\\file.txt"}]
        expected = TypeError.__name__

        for input_value in test_cases:
            try:
                file_util.escape_backslashes(input_value)  # type: ignore[arg-type]
                result = None
            except Exception as e:
                result = type(e).__name__
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestGetFilesInDirectory(unittest.TestCase):
    """
    Unit tests for the `get_files_in_directory` function.

    These tests verify that the function correctly lists files in a directory,
    applies extension-based filtering, and raises appropriate exceptions for
    invalid paths or access errors.
    """

    def setUp(self):
        """
        Creates a temporary directory with test files and subdirectories.
        """
        self.test_dir = os.path.join(os.getcwd(), "temp_test_dir")
        os.makedirs(self.test_dir, exist_ok=True)

        self.files = ["file1.txt", "file2.csv", "file3.TXT", "file4.docx"]
        self.subdir = os.path.join(self.test_dir, "subfolder")
        os.makedirs(self.subdir, exist_ok=True)

        for file in self.files:
            with open(os.path.join(self.test_dir, file), "w") as f:
                f.write("test content")

        # Add a file in subdirectory (should be ignored)
        with open(os.path.join(self.subdir, "nested.txt"), "w") as f:
            f.write("nested")

    def tearDown(self):
        """
        Cleans up the temporary directory and files after tests.
        """
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_list_all_files(self):
        """
        Should return all immediate files in the directory regardless of extension.
        """
        # ARRANGE
        expected = sorted(self.files)

        # ACT
        result = sorted(file_util.get_files_in_directory(self.test_dir))

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_filter_by_extensions_case_insensitive(self):
        """
        Should return only files matching specified extensions (case-insensitive).
        """
        # ARRANGE
        extensions = [".txt"]
        expected = sorted(["file1.txt", "file3.TXT"])

        # ACT
        result = sorted(file_util.get_files_in_directory(self.test_dir, extensions))

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_empty_extensions_returns_all_files(self):
        """
        Should return all files when extensions is an empty list.
        """
        # ARRANGE
        expected = sorted(self.files)

        # ACT
        result = sorted(file_util.get_files_in_directory(self.test_dir, []))

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_nonexistent_directory_raises(self):
        """
        Should raise FileNotFoundError when directory does not exist.
        """
        # ARRANGE
        bad_path = os.path.join(self.test_dir, "does_not_exist")
        expected = FileNotFoundError.__name__

        # ACT
        try:
            file_util.get_files_in_directory(bad_path)
            result = None  # Should not reach here
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_path_is_not_a_directory(self):
        """
        Should raise NotADirectoryError when path is not a directory.
        """
        # ARRANGE
        file_path = os.path.join(self.test_dir, "file1.txt")
        expected = NotADirectoryError.__name__

        # ACT
        try:
            file_util.get_files_in_directory(file_path)
            result = None  # Should not reach here
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestIsExistingFile(unittest.TestCase):
    """
    Unit test for the `is_existing_file` function in the file utility module.

    This test verifies that the function correctly identifies existing regular files,
    rejects directories and non-existent paths, and raises TypeError for invalid input types.
    """

    def setUp(self):
        """
        Create temporary files and directories for test isolation.
        """
        # Create a real temp file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()

        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_path = self.temp_dir.name

    def tearDown(self):
        """
        Clean up created resources after tests.
        """
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
        self.temp_dir.cleanup()

    def test_existing_file(self):
        """
        Should return True for a valid file.
        """
        # ARRANGE
        path = self.temp_file_path
        expected = True

        # ACT
        result = file_util.is_existing_file(path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_existing_directory(self):
        """
        Should return False for a directory path.
        """
        # ARRANGE
        path = self.temp_dir_path
        expected = False

        # ACT
        result = file_util.is_existing_file(path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_nonexistent_path(self):
        """
        Should return False for a path that does not exist.
        """
        # ARRANGE
        path = os.path.join(self.temp_dir_path, "nonexistent.txt")
        expected = False

        # ACT
        result = file_util.is_existing_file(path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_type_input(self):
        """
        Should raise TypeError if file_path is not a string.
        """
        test_cases = [None, 123, 3.14, ["file.txt"], {"path": "file.txt"}]
        expected = TypeError.__name__

        for input_value in test_cases:
            try:
                file_util.is_existing_file(input_value)  # type: ignore[arg-type]
                result = None  # Should not reach here
            except Exception as e:
                result = type(e).__name__
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)


class TestIsValidFilePath(unittest.TestCase):
    """
    Unit test for the `is_valid_file_path` function in the file utility module.

    This test verifies that file names are correctly validated against Windows
    naming rules, including reserved characters and platform-specific logic.
    """

    def test_invalid_type(self):
        """
        Should return False for non-string.
        """
        # ARRANGE
        test_cases = [123, 3.14, [], {}]
        expected = False

        for name in test_cases:
            # ACT
            result = file_util.is_valid_file_path(name)  # type: ignore[arg-type]
            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_empty(self):
        """
        Should return False for empty values.
        """
        # ARRANGE
        test_cases = [None, ""]
        expected = False

        for name in test_cases:
            # ACT
            result = file_util.is_valid_file_path(name)  # type: ignore[arg-type]
            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_valid_names(self):
        """
        Should return True for names that are valid on Windows.
        """
        # ARRANGE
        test_cases = [
            "report.txt",
            "folder_name",
            "data_123.csv",
            "nested_folder.backup",
        ]
        expected = True

        for name in test_cases:
            # ACT
            result = file_util.is_valid_file_path(name)
            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                if os.name == "nt":
                    self.assertTrue(result)
                else:
                    self.assertFalse(result)  # non-Windows always returns False

    def test_invalid_names(self):
        """
        Should return False for names with invalid characters on Windows.
        """
        # ARRANGE
        test_cases = [
            "invalid:name.txt",
            "bad|name.doc",
            "what*file?.txt",
            "<html>.txt",
            "semi>colon.txt",
            "quote\"name.txt",
            "back\\slash.txt",
            "forward/slash.txt",
        ]
        expected = False

        for name in test_cases:
            # ACT
            result = file_util.is_valid_file_path(name)
            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
