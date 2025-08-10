"""
Unit tests for text file I/O utilities in `src.utils.text`.

This test module verifies:
 - Writing UTF-8 encoded text to a file via `save_text_file`
 - Reading full UTF-8 file contents via `load_text_file`
 - Proper handling of error cases (invalid paths, non-existent files)
 - Preservation of original exception details within RuntimeError

The tests create temporary directories and files to avoid modifying
real data. All resources are cleaned up after each test to maintain
isolation between test runs.

Example Usage:
    # Run with unittest discovery:
    python -m unittest tests/utils/test_text.py

    # Run directly:
    python tests/utils/test_text.py

Dependencies:
 - Python >= 3.9
 - Standard Library: os, tempfile, unittest
 - Local Module: src.utils.text

Notes:
 - This test suite uses `setUp`/`tearDown` for temp directory management.
 - Paths and file content are explicitly UTF-8 encoded/decoded.
 - Windows invalid path test may require adjustment on non-Windows systems.

License:
 - Internal Use Only
"""

import os
import tempfile
import unittest

import src.utils.text as file_util


class TestSaveTextFile(unittest.TestCase):
    """
    Unit test for the `save_text_file` function in the `utils` module.

    This test ensures that text content is correctly written to a specified file path
    using UTF-8 encoding, and that an appropriate `RuntimeError` is raised if the file
    cannot be written.
    """

    def setUp(self):
        """
        Create a temporary directory for file writing tests.
        """
        self.temp_dir = tempfile.mkdtemp(prefix="test_save_text_file_")

    def tearDown(self):
        """
        Remove the temporary directory and any files created during testing.
        """
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_write(self):
        """
        Should write given text to a file and verify the file content matches.
        """
        # ARRANGE
        temp_file_path = os.path.join(self.temp_dir, "test_file.txt")
        test_content = "Hello, this is a test.\nWith multiple lines.\n✓ UTF-8 check."

        # ACT
        file_util.save_text_file(temp_file_path, test_content)

        # ASSERT
        with open(temp_file_path, mode="r", encoding="utf-8") as f:
            result_content = f.read()
        with self.subTest(Out=result_content, Exp=test_content):
            self.assertEqual(result_content, test_content)

    def test_invalid_path(self):
        """
        Should raise RuntimeError if the file cannot be written (e.g., invalid path).
        """
        # ARRANGE
        invalid_path = "Z:\\non_existent_folder\\file.txt"  # Likely invalid on Windows
        test_content = "This will fail."

        expected_exception = RuntimeError.__name__

        # ACT
        try:
            file_util.save_text_file(invalid_path, test_content)
            result = ""  # No exception raised
        except RuntimeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_exception):
            self.assertEqual(result, expected_exception)


class TestLoadTextFile(unittest.TestCase):
    """
    Unit test for the `load_text_file` function in the `utils` module.

    This test ensures that a file's entire contents are correctly read as a string
    using UTF-8 encoding, and that an appropriate `RuntimeError` is raised if the
    file cannot be read.
    """

    def setUp(self):
        """
        Create a temporary directory for test files.
        """
        self.temp_dir = tempfile.mkdtemp(prefix="test_load_text_file_")

    def tearDown(self):
        """
        Clean up all files and the temporary directory after each test.
        """
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_read(self):
        """
        Should read the file and return its exact text content.
        """
        # ARRANGE
        temp_file_path = os.path.join(self.temp_dir, "test_file.txt")
        expected_content = "Hello, world!\nThis is a UTF-8 test\n✓"
        with open(temp_file_path, mode="w", encoding="utf-8") as f:
            f.write(expected_content)

        # ACT
        result_content = file_util.load_text_file(temp_file_path)

        # ASSERT
        with self.subTest(Out=result_content, Exp=expected_content):
            self.assertEqual(result_content, expected_content)

    def test_non_existent_file(self):
        """
        Should raise RuntimeError when attempting to read a non-existent file.
        """
        # ARRANGE
        non_existent_file = os.path.join(self.temp_dir, "does_not_exist.txt")
        expected_exception = RuntimeError.__name__

        # ACT
        try:
            file_util.load_text_file(non_existent_file)
            result = ""  # No exception raised
        except RuntimeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_exception):
            self.assertEqual(result, expected_exception)


if __name__ == "__main__":
    unittest.main()
