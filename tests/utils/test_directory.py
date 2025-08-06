"""
Unit tests for the directory utility functions used in filesystem path resolution and validation.

This module verifies the correctness and robustness of the functions in `src.utils.directory`,
which provide a platform-independent interface for path normalization, directory creation,
subdirectory listing, and execution context resolution.

Main Capabilities Tested:
 - Path construction and normalization (e.g., user home expansion, dot path cleanup)
 - Directory creation (including nested and pre-existing paths)
 - Environment detection (frozen executable vs. development mode)
 - Subdirectory discovery
 - Root and drive resolution (dev and frozen modes)

Example Usage:
    # Run unittest discovery from project root:
    python -m unittest tests/utils/test_directory.py


Dependencies:
 - Python >= 3.9
 - Standard Library: os, sys, shutil, tempfile, unittest

Notes:
 - Tests cover edge cases such as invalid paths, non-string inputs, and simulated frozen execution.
 - Platform-specific logic is handled via conditional skips (e.g., drive resolution on Windows).
 - Temporary files and directories are safely cleaned up using `setUp`/`tearDown` or context managers.

License:
 - Internal Use Only
"""

import unittest
import os
import sys
import shutil
import tempfile

import src.utils.directory as directory


class TestConstructDirectoryPath(unittest.TestCase):
    """
    Unit test for the `construct_directory_path` function in the `directory` module.

    This test ensures that a base path and a sequence of subfolders are properly joined and
    normalized into a consistent, platform-independent directory path.
    """

    def test_windows_style_drive_path(self):
        """
        Should normalize a Windows-style drive path with subfolders and redundant slashes.
        """
        # ARRANGE
        base_path = "C:/home"
        subfolders = ("test", "folder")

        # Expected output after join and normalization
        expected = directory.normalize_dir_path(os.path.join("C:/home", "test", "folder"))

        # ACT
        result = directory.construct_directory_path(base_path, subfolders)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_constructs_correct_normalized_path(self):
        """
        Should join base path with subfolders and return a normalized directory path.
        """
        # ARRANGE
        # Input data setup
        base_path = "/home/user"
        subfolders = ("projects", "data")

        # Expected output
        expected = directory.normalize_dir_path(os.path.join(base_path, *subfolders))

        # ACT
        # Call the function under test
        result = directory.construct_directory_path(base_path, subfolders)

        # ASSERT
        # Validate results
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_with_empty_subfolders(self):
        """
        Should return normalized base path when no subfolders are provided.
        """
        # ARRANGE
        base_path = "/var/log"
        subfolders = ()

        expected = directory.normalize_dir_path(base_path)

        # ACT
        result = directory.construct_directory_path(base_path, subfolders)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestCreateDirectoryIfMissing(unittest.TestCase):
    """
    Unit test for the `create_directory_if_missing` function in the `directory` module.

    This test ensures that a directory is created if it does not exist,
    and that the function returns `True` if the directory already exists.
    """

    def setUp(self):
        """
        Prepare temporary directory paths for testing.
        """
        self.test_dir = os.path.join(os.getcwd(), "temp_test_dir")
        self.nested_dir = os.path.join(self.test_dir, "nested", "path")

        # Ensure cleanup before test
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def tearDown(self):
        """
        Clean up any directories created during tests.
        """
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_create_new_directory(self):
        """
        Should create the directory path when it does not already exist.
        """
        # ARRANGE
        dir_path = self.nested_dir

        # ASSERT pre-condition
        self.assertFalse(os.path.exists(dir_path))

        # ACT
        result = directory.create_directory_if_missing(dir_path)
        exists = os.path.exists(dir_path)

        # ASSERT
        with self.subTest(Out=result, Exp=True):
            self.assertTrue(result)

        # Confirm that the directory actually exists on disk after function call,
        # even though the function performs this check internally.
        # This makes the test independent and validates the expected side effect.
        with self.subTest(Out=exists, Exp=True):
            self.assertTrue(os.path.isdir(dir_path))

    def test_directory_already_exists(self):
        """
        Should return True and make no changes when directory already exists.
        """
        # ARRANGE
        os.makedirs(self.nested_dir)
        self.assertTrue(os.path.isdir(self.nested_dir))

        # ACT
        result = directory.create_directory_if_missing(self.nested_dir)
        still_exists = os.path.exists(self.nested_dir)

        # ASSERT
        with self.subTest(Out=result, Exp=True):
            self.assertTrue(result)
        with self.subTest(Out=still_exists, Exp=True):
            self.assertTrue(os.path.isdir(self.nested_dir))

    def test_invalid_path_raises_error(self):
        """
        Should raise OSError if the path is invalid (e.g., forbidden characters on Windows).
        """
        # ARRANGE
        # Use known-invalid path: reserved name on Windows or a protected path on Unix
        if os.name == "nt":
            invalid_path = "CON\\invalid"
        else:
            invalid_path = "/dev/null/invalid"

        expected = OSError.__name__

        # ACT
        # Capture the raised exception type without stopping the test
        try:
            directory.create_directory_if_missing(invalid_path)
            result = ""  # No exception raised
        except OSError as e:
            result = type(e).__name__

        # ASSERT
        # Compare exception type name to expected
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestIsDirectoryPath(unittest.TestCase):
    """
    Unit test for the `is_directory_path` function in the directory module.

    This test ensures that various types of paths (valid directory, file path, non-existent)
    are correctly evaluated to determine if they are existing directories.
    """

    def test_directory_path(self):
        """
        Should return True when given an existing directory path.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            # ACT
            result = directory.is_directory_path(temp_dir)

            # ASSERT
            with self.subTest(Out=result, Exp=True):
                self.assertTrue(result)

    def test_file_path(self):
        """
        Should return False when given a path to an existing file.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "file.txt")
            with open(file_path, "w") as f:
                f.write("test")

            # ACT
            result = directory.is_directory_path(file_path)

            # ASSERT
            with self.subTest(Out=result, Exp=False):
                self.assertFalse(result)

    def test_non_existent_path(self):
        """
        Should return False when given a non-existent path.
        """
        # ARRANGE
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent = os.path.join(temp_dir, "does_not_exist")

            # ACT
            result = directory.is_directory_path(non_existent)

            # ASSERT
            with self.subTest(Out=result, Exp=False):
                self.assertFalse(result)

    def test_empty_string_path(self):
        """
        Should return False when given an empty string as path.
        """
        # ACT
        result = directory.is_directory_path("")

        # ASSERT
        with self.subTest(Out=result, Exp=False):
            self.assertFalse(result)


class TestIsRunningAsExecutable(unittest.TestCase):
    """
    Unit test for the `is_running_as_executable` function in the directory module.

    This test verifies that the function correctly detects whether the script is
    running in a frozen executable context by checking the `sys.frozen` attribute.
    """

    def test_sys_frozen_is_set(self):
        """
        Should return True when 'sys.frozen' is explicitly set to True.
        """
        # ARRANGE
        original = getattr(sys, 'frozen', None)
        setattr(sys, 'frozen', True)

        # ACT
        result = directory.is_running_as_executable()

        # ASSERT
        with self.subTest(Out=result, Exp=True):
            self.assertTrue(result)

        # CLEANUP
        if original is None:
            delattr(sys, 'frozen')
        else:
            setattr(sys, 'frozen', original)

    def test_sys_frozen_is_missing(self):
        """
        Should return False when 'sys.frozen' is not set at all.
        """
        # ARRANGE
        original = getattr(sys, 'frozen', None)
        if hasattr(sys, 'frozen'):
            del sys.frozen

        # ACT
        result = directory.is_running_as_executable()

        # ASSERT
        with self.subTest(Out=result, Exp=False):
            self.assertFalse(result)

        # CLEANUP
        if original is not None:
            sys.frozen = original

    def test_sys_frozen_is_false(self):
        """
        Should return False when 'sys.frozen' is explicitly set to False.
        """
        # ARRANGE
        original = getattr(sys, 'frozen', None)
        setattr(sys, 'frozen', False)

        # ACT
        result = directory.is_running_as_executable()

        # ASSERT
        with self.subTest(Out=result, Exp=False):
            self.assertFalse(result)

        # CLEANUP
        if original is None:
            delattr(sys, 'frozen')
        else:
            setattr(sys, 'frozen', original)

    def test_in_python_environment(self):
        """
        Should return False in normal (non-frozen) Python environments.
        """
        # ACT
        result = directory.is_running_as_executable()

        # ASSERT
        with self.subTest(Out=result, Exp=False):
            self.assertFalse(result)


class TestListImmediateSubdirectories(unittest.TestCase):
    """
    Unit test for the `list_immediate_subdirectories` function in the directory module.

    This test ensures the function returns the correct set of immediate subdirectories,
    and raises appropriate errors for invalid paths.
    """

    def setUp(self):
        """
        Create a temporary directory structure for testing.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = self.temp_dir.name

        # Create subdirectories and files
        os.mkdir(os.path.join(self.base_path, "subdir1"))
        os.mkdir(os.path.join(self.base_path, "subdir2"))
        with open(os.path.join(self.base_path, "file1.txt"), "w") as f:
            f.write("dummy")

    def tearDown(self):
        """
        Clean up the temporary directory structure.
        """
        self.temp_dir.cleanup()

    def test_subdirectories(self):
        """
        Should return only the names of immediate subdirectories, excluding files.
        """
        # ARRANGE
        expected = ("subdir1", "subdir2")

        # ACT
        result = directory.list_immediate_subdirectories(self.base_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertCountEqual(result, expected)

    def test_no_subdirectories(self):
        """
        Should return an empty tuple when the directory has no subdirectories.
        """
        # ARRANGE
        empty_dir = os.path.join(self.base_path, "empty")
        os.mkdir(empty_dir)

        # ACT
        result = directory.list_immediate_subdirectories(empty_dir)

        # ASSERT
        with self.subTest(Out=result, Exp=()):
            self.assertEqual(result, ())

    def test_not_directory_path(self):
        """
        Should raise FileNotFoundError when the given path is not a directory.
        """
        # ARRANGE
        file_path = os.path.join(self.base_path, "file1.txt")
        expected = FileNotFoundError.__name__

        # ACT
        try:
            directory.list_immediate_subdirectories(file_path)
            result = None  # No exception raised
        except FileNotFoundError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_existent_path(self):
        """
        Should raise FileNotFoundError when the path does not exist.
        """
        # ARRANGE
        non_existent = os.path.join(self.base_path, "does_not_exist")
        expected = FileNotFoundError.__name__

        # ACT
        try:
            directory.list_immediate_subdirectories(non_existent)
            result = None
        except FileNotFoundError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestNormalizeDirPath(unittest.TestCase):
    """
    Unit test for the `normalize_dir_path` function in the directory module.

    This test verifies that various raw paths are normalized correctly and that
    invalid inputs raise appropriate errors.
    """

    def test_expand_directory(self):
        """
        Should expand '~' to the absolute home directory and normalize the result.
        """
        # ARRANGE
        raw_path = "~/test/folder"
        expected = os.path.normpath(os.path.expanduser(raw_path))

        # ACT
        result = directory.normalize_dir_path(raw_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_redundant_path_components(self):
        """
        Should normalize paths with one dot, two dots and duplicate slashes.
        """
        # ARRANGE
        raw_path = "./a/./b/../c//./../c/d/../e///"
        expected = os.path.normpath("a/c/e")

        # ACT
        result = directory.normalize_dir_path(raw_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_normalized_paths(self):
        """
        Should leave already normalized absolute paths unchanged.
        """
        # ARRANGE
        abs_path = os.path.join(os.sep, "usr", "local", "bin")
        expected = os.path.normpath(abs_path)

        # ACT
        result = directory.normalize_dir_path(abs_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_string_input(self):
        """
        Should raise TypeError if input is not a string.
        """
        # ARRANGE
        bad_input = 12345
        expected = TypeError.__name__

        # ACT
        try:
            directory.normalize_dir_path(bad_input)
            result = None
        except TypeError as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestResolveAppRoot(unittest.TestCase):
    """
    Unit test for the `resolve_app_root` function in the directory module.

    This test verifies the development-mode resolution of the application root
    and ensures an appropriate error is raised when root resolution fails.
    """

    def test_dev_mode(self):
        """
        Should return a valid and existing path in development mode (non-frozen).
        """
        # ARRANGE
        # Dev mode is assumed because sys.frozen is not set
        expected = directory.resolve_dev_dir()

        # ACT
        result = directory.find_root()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test__raise(self):
        """
        Should raise FileNotFoundError if resolution fails due to underlying errors.

        This test temporarily replaces resolve_dev_dir() with a broken version.
        """
        # ARRANGE
        original = directory.resolve_dev_dir

        def broken():
            raise RuntimeError("Boom")

        directory.resolve_dev_dir = broken

        expected = FileNotFoundError.__name__

        # ACT
        try:
            directory.find_root()
            result = None  # No error raised
        except FileNotFoundError as e:
            result = type(e).__name__

        # CLEANUP
        directory.resolve_dev_dir = original

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_exe_mode_(self):
        """
        Should return the executable directory when 'sys.frozen' is True.

        This simulates a frozen environment by setting `sys.frozen = True`,
        which forces `resolve_app_root()` to follow the executable path.
        """
        # ARRANGE
        original = getattr(sys, 'frozen', None)
        setattr(sys, 'frozen', True)  # avoid direct sys.frozen = True to suppress warnings
        expected = directory.resolve_exe_dir()  # This is what resolve_app_root() should call

        # ACT
        result = directory.find_root()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

        # CLEANUP
        if original is None:
            delattr(sys, 'frozen')
        else:
            setattr(sys, 'frozen', original)


class TestResolveDevDir(unittest.TestCase):
    """
    Unit test for the `resolve_dev_dir` function in the directory module.

    This test ensures the function correctly resolves the development root directory
    relative to the test file.
    """

    def test_returns_valid_root(self):
        """
        Should return a valid root directory in dev mode.
        """
        # ARRANGE
        # No setup needed — test runs in development mode
        expected = os.path.normpath(os.path.dirname(__file__))  # Default expectation
        # If the script resides in the text folder, treat its parent as the root
        while "tests" in expected:
            expected = os.path.split(expected)[0]

        # ACT
        result = directory.resolve_dev_dir()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestResolveDrive(unittest.TestCase):
    """
    Unit test for the `resolve_drive` function in the directory module.

    This test ensures the function extracts the correct drive letter when running
    on Windows, and raises appropriate errors on unsupported platforms.
    """

    def test_on_windows(self):
        """
        Should return the correct normalized drive letter when running on Windows.
        """
        if os.name != "nt":
            self.skipTest("resolve_drive() is only supported on Windows systems.")

        # ARRANGE
        root_path = directory.find_root()
        expected_drive, _ = os.path.splitdrive(root_path)
        expected = directory.normalize_dir_path(expected_drive + os.sep)

        # ACT
        result = directory.find_drive()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_windows(self):
        """
        Should raise ValueError when called on a non-Windows system.
        """
        if os.name == "nt":
            self.skipTest("This test is only applicable to non-Windows systems.")

        # ARRANGE
        expected = ValueError.__name__

        # ACT
        try:
            directory.find_drive()
            result = None  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestResolveExeDir(unittest.TestCase):
    """
    Unit test for the `resolve_exe_dir` function in the directory module.

    This test ensures the function correctly returns the directory of the Python executable
    (in dev mode), and raises a FileNotFoundError when the resolved path is invalid.
    """

    def test_returns_valid_executable_directory(self):
        """
        Should return the directory containing the Python executable as a path.
        """
        # ARRANGE
        expected = directory.normalize_dir_path(os.path.dirname(sys.executable))

        # ACT
        result = directory.resolve_exe_dir()

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_raises_error_when_executable_directory_invalid(self):
        """
        Should raise FileNotFoundError if the executable directory does not exist or is invalid.

        This simulates an error by temporarily overriding `sys.executable`.
        """
        # ARRANGE
        original_executable = sys.executable
        sys.executable = "/invalid/fake/path/to/executable"
        expected = FileNotFoundError.__name__

        # ACT
        try:
            directory.resolve_exe_dir()
            result = None  # No exception raised
        except FileNotFoundError as e:
            result = type(e).__name__
        finally:
            # CLEANUP
            sys.executable = original_executable

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
