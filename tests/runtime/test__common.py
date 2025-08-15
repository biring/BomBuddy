"""
Unit tests for `src.runtime._common` runtime JSON utilities.

This test module verifies core validation/load helpers that back the runtime resource system. It covers success and failure paths for:
    - `_assert_all_values_are_strings(map)`  → accepts only str values
    - `_assert_required_keys_are_present(map, required_keys)`  → enforces presence
    - `_resolve_json_file_path(resource_name, base_dir=...)`  → path resolution
    - `load_runtime_json(resource_name, required_keys)`  → end‑to‑end load + validate

The suite uses real temporary directories/files (no external mocking library) to exercise I/O, checksum verification, and error wrapping semantics.

Example Usage:
    # Preferred usage — run all tests in this module using unit test discovery:
    python -m unittest tests/runtime/test__common.py

Dependencies:
    - Python >= 3.9
    - Standard Library: os, tempfile, shutil, unittest
    - Internal: src.utils.json (create/save foundation JSON), src.runtime._common (functions under test)

Notes:
    - Tests intentionally reach into underscore-prefixed functions in `_common`
        because they are treated as package-internal APIs for the runtime package.
    - `TestResolveJsonFilePathWithBaseDir` uses a real temp folder; no monkeypatch
        framework is required.
    - `TestLoadRuntimeJson` patches `_resolve_json_file_path` by assignment during
        setUp/tearDown to route lookups into a temp directory; it validates:
        * success path with a well-formed foundation JSON
        * checksum mismatch is surfaced as `RuntimeError`
        * missing required keys wrapped as `RuntimeError`
        * non-string values wrapped as `RuntimeError`
    - `TestAssertRequiredKeysArePresent` asserts that an empty `required_keys`
        list raises `KeyError` (intentional contract).
    - Keep tests isolated; all temp artifacts are cleaned up in tearDown.

License:
 - Internal Use Only
"""
import os
import tempfile
import shutil
import unittest
import src.utils.json as json_util

# noinspection PyProtectedMember
from src.runtime import _common as common


class TestCache(unittest.TestCase):
    """
    Unit tests for the `Cache` class.

    These tests validate correct loading, retrieval, and state-checking behavior
    of the runtime resource cache, as well as proper error handling for invalid
    inputs and resource/key mismatches.
    """

    def setUp(self):
        """
        Create a new Cache instance before each test.
        """
        self.cache = common.Cache()

    def test_new_resource(self):
        """
        Should load a resource and retrieve values for valid keys.
        """
        # ARRANGE
        resource_name = "_info"
        data_map = {"WELCOME": "Hello!", "BYE": "Goodbye"}
        test_key = "BYE"
        expected = "Goodbye"

        # ACT
        self.cache.load_resource(resource_name, data_map)
        result = self.cache.get_value(resource_name, test_key)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_is_loaded_behavior(self):
        """
        Should correctly indicate whether a given resource is loaded.
        """
        # ARRANGE
        resource_name = "_info"
        data_map = {"KEY": "VALUE"}
        self.cache.load_resource(resource_name, data_map)

        # ACT
        result_match = self.cache.is_loaded("_info")
        result_mismatch = self.cache.is_loaded("_config")

        # ASSERT
        with self.subTest(Out=result_match, Exp=True):
            self.assertTrue(result_match)
        with self.subTest(Out=result_mismatch, Exp=False):
            self.assertFalse(result_mismatch)

    def test_load_resource_with_invalid_type(self):
        """
        Should raise TypeError if data_map is not dict[str, str].
        """
        # ARRANGE
        resource_name = "_info"
        invalid_data_maps = [
            {"KEY": 123},  # value not str
            {123: "VALUE"},  # key not str
            [("KEY", "VALUE")],  # not a dict
        ]
        expected = TypeError.__name__

        for bad_map in invalid_data_maps:
            # ACT
            try:
                self.cache.load_resource(resource_name, bad_map)  # type: ignore[index]
                result = ""  # Unexpected: no exception
            except Exception as e:
                result = type(e).__name__

            # ASSERT
            with self.subTest(Out=result, Exp=expected):
                self.assertEqual(result, expected)

    def test_get_with_no_resource(self):
        """
        Should raise KeyError when get_value is called before loading a resource.
        """
        # ARRANGE
        resource_name = "_any_name"
        expected = KeyError.__name__

        # ACT
        try:
            self.cache.get_value(resource_name, "ANY_KEY")
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_with_wrong_resource(self):
        """
        Should raise KeyError if requesting a different resource than the one loaded.
        """
        # ARRANGE
        loaded_resource_name = "_typeA"
        wrong_resource_name = "_typeB"
        self.cache.load_resource(loaded_resource_name, {"KEY": "VALUE"})
        expected = KeyError.__name__

        # ACT
        try:
            self.cache.get_value(wrong_resource_name, "ANY_KEY")
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_get_with_missing_key(self):
        """
        Should raise KeyError if the requested key is not in the loaded resource.
        """
        # ARRANGE
        resource_name = "_typeA"
        correct_key = "KEY"
        incorrect_key = "OTHER_KEY"
        self.cache.load_resource(resource_name, {correct_key: "VALUE"})
        expected = KeyError.__name__

        # ACT
        try:
            self.cache.get_value(resource_name, incorrect_key)
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestAssertAllValuesAreStrings(unittest.TestCase):
    """
    Unit test for the `_assert_all_values_are_strings` function in `src.runtime._common`.

    This test ensures that:
      - The function completes without error when all values in the dictionary are strings.
      - A `TypeError` is raised when any value is not a string, with a clear message
        indicating the offending key and value type.
    """

    def test_strings(self):
        """
        Should not raise exception when all values are strings.
        """
        # ARRANGE
        key_value_map = {
            "KEY1": "Value1",
            "KEY2": "Value2",
            "KEY3": ""
        }

        # ACT & ASSERT
        try:
            common._assert_all_values_are_strings(key_value_map)
            result = None  # No exception raised
        except Exception as e:
            result = type(e).__name__

        with self.subTest(Out=result, Exp=None):
            self.assertIsNone(result)

    def test_non_string(self):
        """
        Should raise TypeError when any value is not a string.
        """
        # ARRANGE
        key_value_map = {
            "KEY1": "Valid",
            "KEY2": 123,  # Non-string value
            "KEY3": "Also valid"
        }
        expected_error = TypeError.__name__

        # ACT
        try:
            common._assert_all_values_are_strings(key_value_map)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestAssertRequiredKeysArePresent(unittest.TestCase):
    """
    Unit tests for the `_assert_required_keys_are_present` function in `src.runtime._common`.

    This suite ensures that:
      - The function completes silently when all required keys are present.
      - A `KeyError` is raised when one or more required keys are missing.
      - An empty `required_keys` list imposes no requirements (no exception).
    """

    def test_all_required_present(self):
        """
        Should pass without raising when every required key exists in the map.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
            "VERSION": "1.0.0",
        }
        required_keys = ["APP_NAME", "WELCOME"]

        # ACT
        try:
            common._assert_required_keys_are_present(key_value_map, required_keys)
            result = None  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=None):
            self.assertIsNone(result)

    def test_missing_single_key_raises(self):
        """
        Should raise KeyError when one required key is missing.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
        }
        required_keys = ["APP_NAME", "WELCOME", "VERSION"]
        expected_error = KeyError.__name__

        # ACT
        try:
            common._assert_required_keys_are_present(key_value_map, required_keys)
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_missing_multiple_keys_raises(self):
        """
        Should raise KeyError when multiple required keys are missing.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
        }
        required_keys = ["APP_NAME", "WELCOME", "VERSION"]
        expected_error = KeyError.__name__

        # ACT
        try:
            common._assert_required_keys_are_present(key_value_map, required_keys)
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_empty_required_keys(self):
        """
        Should raise KeyError when `required_keys` is empty.
        """
        # ARRANGE
        key_value_map = {
            "APP_NAME": "MyApp",
            "WELCOME": "Hello",
            "VERSION": "1.0.0"
        }
        required_keys: list[str] = []
        expected_error = KeyError.__name__

        # ACT
        try:
            common._assert_required_keys_are_present(key_value_map, required_keys)
            result = None  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestExportKeys(unittest.TestCase):
    """
    Unit test for the `export_keys` function in `src.runtime._common`.

    This test ensures that:
      - Only uppercase constant names are included.
      - Only string values are included (e.g., excludes lists, ints, etc.).
      - Returns an empty list if no matching constants are found.
    """

    def test_with_uppercase_string_constants(self):
        """
        Should return only uppercase names whose values are strings.
        """
        # ARRANGE
        module_globals = {
            "FOO": "foo",  # valid
            "BAR": "bar",  # valid
            "baz": "baz",  # lowercase, excluded
            "REQUIRED_KEYS": ["X"],  # uppercase but not string, excluded
            "NUM": 123,  # uppercase but not string, excluded
        }
        expected = ["FOO", "BAR"]

        # ACT
        result = common.export_keys(module_globals)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(sorted(result), sorted(expected))

    def test_without_uppercase_strings(self):
        """
        Should return an empty list if there are no uppercase string constants.
        """
        # ARRANGE
        module_globals = {
            "lower": "value",
            "MixedCase": "value",
            "LIST": [1, 2, 3],
            "NUM": 42
        }
        expected = []

        # ACT
        result = common.export_keys(module_globals)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestLoadRuntimeJson(unittest.TestCase):
    """
    Unit tests for `load_runtime_json` in `src.runtime._common`.

    Focus:
      - Success path: loads a valid foundation JSON, verifies checksum, validates keys,
        asserts all values are strings, and returns the `data` mapping.
      - Failure paths wrapped as `RuntimeError`:
          * Missing file or unreadable JSON
          * Checksum verification failure
          * Missing required keys
          * Non-string values present in the `data` mapping

    Notes:
      - No mocking libraries are used. We write real temp files.
      - We temporarily patch `_resolve_json_file_path` to point into a temp directory.
      - Tests follow Arrange–Act–Assert and use `subTest` for clear result vs expected output.
    """

    def setUp(self):
        """
        Create a temporary runtime directory and patch `_resolve_json_file_path`
        so it resolves into this directory for the duration of each test.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="runtime_json_")
        self.orig_resolver = common._resolve_json_file_path

        # Patch the path resolver to always return a file within our temp directory.
        def _resolver(resource_name: str):
            filename = resource_name + common.file_util.JSON_FILE_EXT
            return os.path.join(self.tmpdir, filename)

        common._resolve_json_file_path = _resolver  # simple, library-free patch

        # Convenience: name for our resource (e.g., "_info")
        self.resource = "_info"
        self.filename = self.resource + common.file_util.JSON_FILE_EXT
        self.filepath = os.path.join(self.tmpdir, self.filename)

    def tearDown(self):
        """
        Restore the original resolver and remove temp files.
        """
        common._resolve_json_file_path = self.orig_resolver
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_with_foundation_json(self):
        """
        Should return the validated key→value mapping when the foundation JSON is correct.
        """
        # ARRANGE
        data = {"APP_NAME": "MyApp", "WELCOME": "Hello"}
        foundation = json_util.create_foundation_json(data, source_file=self.filename)
        json_util.save_json_file(self.filepath, foundation)

        required_keys = ["APP_NAME", "WELCOME"]
        expected = data

        # ACT
        result = common.load_runtime_json(self.resource, required_keys)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_without_foundation_json(self):
        """
        Should wrap internal file read errors as RuntimeError when the JSON file is missing.
        """
        # ARRANGE
        required_keys = ["APP_NAME"]
        expected = RuntimeError.__name__

        # ACT
        try:
            common.load_runtime_json(self.resource, required_keys)
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_checksum_mismatch(self):
        """
        Should raise RuntimeError when the stored checksum does not match computed checksum.
        """
        # ARRANGE
        data = {"APP_NAME": "MyApp", "WELCOME": "Hello"}
        foundation = json_util.create_foundation_json(data, source_file=self.filename)
        # Tamper with checksum to force a mismatch
        foundation["meta"]["checksum"] = foundation["meta"]["checksum"] + 1  # type: ignore[index]
        json_util.save_json_file(self.filepath, foundation)

        required_keys = ["APP_NAME", "WELCOME"]

        # ACT
        try:
            common.load_runtime_json(self.resource, required_keys)
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=RuntimeError.__name__):
            self.assertEqual(result, RuntimeError.__name__)

    def test_missing_required_keys(self):
        """
        Should raise RuntimeError when any of the required keys is missing from `data`.
        """
        # ARRANGE
        data = {"APP_NAME": "MyApp"}  # WELCOME key is missing
        foundation = json_util.create_foundation_json(data, source_file=self.filename)
        json_util.save_json_file(self.filepath, foundation)

        required_keys = ["APP_NAME", "WELCOME"]

        # ACT
        try:
            common.load_runtime_json(self.resource, required_keys)
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=RuntimeError.__name__):
            self.assertEqual(result, RuntimeError.__name__)

    def test_non_string_values(self):
        """
        Should raise RuntimeError when any value in `data` is not a string.
        """
        # ARRANGE
        data = {"APP_NAME": "MyApp", "WELCOME": 123}  # Non-string value
        foundation = json_util.create_foundation_json(data, source_file=self.filename)
        json_util.save_json_file(self.filepath, foundation)

        required_keys = ["APP_NAME", "WELCOME"]

        # ACT
        try:
            common.load_runtime_json(self.resource, required_keys)
            result = ""  # Unexpected: no exception
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=RuntimeError.__name__):
            self.assertEqual(result, RuntimeError.__name__)


class TestResolveJsonFilePathWithBaseDir(unittest.TestCase):
    """
    Unit tests for `_resolve_json_file_path` in `src.runtime._common`
    when a `base_dir` is explicitly provided.

    This test uses a real temporary directory to keep the logic simple.
    """

    def setUp(self):
        """
        Create a temporary directory to act as the runtime folder.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="runtime_tmp_")

    def tearDown(self):
        """
        Remove the temporary directory after tests.
        """
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_file_exists(self):
        """
        Should return the correct absolute path when the JSON file exists.
        """
        # ARRANGE
        resource = "_info"
        filename = resource + common.file_util.JSON_FILE_EXT
        expected_path = os.path.join(self.tmpdir, filename)

        with open(expected_path, "w", encoding="utf-8") as f:
            f.write('{"meta": {}, "data": {}}')

        # ACT
        result = common._resolve_json_file_path(resource, base_dir=self.tmpdir)

        # ASSERT
        with self.subTest(Out=result, Exp=expected_path):
            self.assertEqual(result, expected_path)

    def test_file_missing(self):
        """
        Should raise FileNotFoundError if the JSON file is not found.
        """
        # ARRANGE
        resource = "_info"
        expected_error = FileNotFoundError.__name__

        # ACT
        try:
            common._resolve_json_file_path(resource, base_dir=self.tmpdir)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


if __name__ == "__main__":
    unittest.main()
