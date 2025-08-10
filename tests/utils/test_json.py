"""
Unit tests for JSON utility functions in `src.utils.json`.

This module validates serialization, deserialization, file loading, and file saving
behaviors for the JSON helper functions:
 - dict_to_json_string: Serialize dicts to JSON strings with optional indentation
 - json_string_to_dict: Deserialize JSON strings into Python dictionaries
 - load_json_file: Read and parse JSON from disk into a dictionary
 - save_json_file: Serialize and save a dictionary to disk as JSON

Each test suite covers:
 - Correct handling of valid input data (including Unicode characters)
 - Proper application of optional pretty-print indentation
 - Behavior with nested structures and whitespace
 - Error handling for malformed JSON, non-serializable values, and missing files

Example Usage:
    # Preferred usage — run all tests in this module:
    python -m unittest tests.utils.test_json

    # Run a specific test case directly:
    python -m unittest tests.utils.test_json.TestSaveJsonFile.test_with_indent

Dependencies:
 - Python >= 3.9
 - Standard Library: unittest, json, os, tempfile, shutil
 - Internal: src.utils.json

Notes:
 - Tests follow the Arrange–Act–Assert pattern with `subTest` assertions
   for clearer output on mismatches.
 - Temporary files and directories are created in setUp/tearDown to ensure
   isolation between tests and avoid polluting the filesystem.
 - Unicode handling is explicitly verified to ensure `ensure_ascii=False` works as intended.

License:
 - Internal Use Only
"""

import json
import os
import shutil
import tempfile
import unittest

import src.utils.json as json_util


class TestDictToJsonString(unittest.TestCase):
    """
    Unit tests for the `dict_to_json_string` function.

    This test ensures that:
      1) A dictionary with string keys is correctly serialized to JSON.
      2) Pretty-printing indentation is applied when `indent_spaces` is provided.
      3) Unicode characters are preserved (ensure_ascii=False).
      4) Serialization errors are wrapped in a `RuntimeError` with a descriptive message.
    """

    def test_serialization(self):
        """
        Should serialize a simple dictionary with string keys into a JSON string.
        """
        # ARRANGE
        input_dict = {"name": "Alice", "age": 30}
        expected = json.dumps(input_dict, ensure_ascii=False)

        # ACT
        result = json_util.dict_to_json_string(input_dict)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_with_indentation(self):
        """
        Should serialize with indentation when indent_spaces is provided.
        """
        # ARRANGE
        input_dict = {"city": "Paris", "population": 2148327}
        indent_spaces = 4
        expected = json.dumps(input_dict, indent=indent_spaces, ensure_ascii=False)

        # ACT
        result = json_util.dict_to_json_string(input_dict, indent_spaces=indent_spaces)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_unicode(self):
        """
        Should preserve Unicode characters without escaping.
        """
        # ARRANGE
        input_dict = {"greeting": "こんにちは"}  # Japanese for "Hello"
        expected = json.dumps(input_dict, ensure_ascii=False)

        # ACT
        result = json_util.dict_to_json_string(input_dict)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_non_serializable(self):
        """
        Should raise RuntimeError when dictionary contains non-serializable values.
        """
        # ARRANGE
        input_dict = {"callback": lambda x: x}  # Functions are not JSON serializable
        expected_error = RuntimeError.__name__

        # ACT
        try:
            json_util.dict_to_json_string(input_dict)
            result = ""
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestJsonStringToDict(unittest.TestCase):
    """
    Unit tests for the `json_string_to_dict` function.

    This suite verifies that valid JSON strings are deserialized into Python
    dictionaries and that malformed JSON raises a `RuntimeError`. Tests focus
    strictly on input→output behavior implemented in the function body (i.e.,
    calling `json.loads` and wrapping exceptions) without asserting implied
    validations not present in the function.
    """

    def test_deserialization(self):
        """
        Should parse a compact JSON object string into an equivalent Python dict.
        """
        # ARRANGE
        json_str = '{"name":"Alice","age":30,"active":true}'
        expected = {"name": "Alice", "age": 30, "active": True}

        # ACT
        result = json_util.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_with_whitespace_and_newlines(self):
        """
        Should ignore whitespace/newlines and parse to the same dict.
        """
        # ARRANGE
        json_str = """
        {
            "city": "Paris",
            "population": 2148327,
            "co-ords": { "lat": 48.8566, "lon": 2.3522 }
        }
        """
        # Use Python literal for clarity and to avoid duplicating parsing logic
        expected = {
            "city": "Paris",
            "population": 2148327,
            "co-ords": {"lat": 48.8566, "lon": 2.3522},
        }

        # ACT
        result = json_util.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_unicode(self):
        """
        Should correctly parse and preserve Unicode characters.
        """
        # ARRANGE
        json_str = '{"greeting":"こんにちは","emoji":"😀","currency":"€"}'
        expected = {"greeting": "こんにちは", "emoji": "😀", "currency": "€"}

        # ACT
        result = json_util.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_nested_structures(self):
        """
        Should parse nested dicts and arrays exactly as represented.
        """
        # ARRANGE
        json_str = json.dumps(
            {
                "user": {"id": 1, "roles": ["admin", "editor"]},
                "flags": {"beta": True, "notifications": {"email": False, "sms": True}},
            },
            ensure_ascii=False,
        )
        expected = {
            "user": {"id": 1, "roles": ["admin", "editor"]},
            "flags": {"beta": True, "notifications": {"email": False, "sms": True}},
        }

        # ACT
        result = json_util.json_string_to_dict(json_str)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_json(self):
        """
        Should raise RuntimeError when JSON string is malformed.
        """
        # ARRANGE
        # Trailing comma makes this JSON invalid
        invalid_json = '{"a": 1, "b": 2,}'

        expected_error = RuntimeError.__name__

        # ACT
        try:
            json_util.json_string_to_dict(invalid_json)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            # Verify the wrapped exception type name only (no reliance on message format)
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestLoadJsonFile(unittest.TestCase):
    """
    Unit tests for the `load_json_file` function.

    This suite verifies that a JSON file is read and deserialized into a Python
    dictionary, and that errors are wrapped in a RuntimeError when the file is
    missing, unreadable, or contains invalid JSON.
    """

    def setUp(self):
        """
        Create a temporary directory for test artifacts.
        """
        self.tmpdir = tempfile.mkdtemp(prefix="json_load_test_")
        self.file_path = os.path.join(self.tmpdir, "test.json")

    def tearDown(self):
        """
        Remove any temporary files/directories created during tests.
        """
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_load_valid_json_file(self):
        """
        Should read and parse a valid JSON file into the expected dictionary.
        """
        # ARRANGE
        expected = {"name": "Alice", "age": 30, "active": True}
        with open(self.file_path, mode="w", encoding="utf-8") as f:
            json.dump(expected, f, ensure_ascii=False)  # type: ignore[arg-type]

        # ACT
        result = json_util.load_json_file(self.file_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_load_json_with_unicode(self):
        """
        Should correctly parse JSON containing Unicode characters.
        """
        # ARRANGE
        expected = {"greeting": "こんにちは", "emoji": "😀", "currency": "€"}
        with open(self.file_path, mode="w", encoding="utf-8") as f:
            json.dump(expected, f, ensure_ascii=False)  # type: ignore[arg-type]

        # ACT
        result = json_util.load_json_file(self.file_path)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_json_file(self):
        """
        Should raise RuntimeError if the file contains invalid JSON.
        """
        # ARRANGE
        with open(self.file_path, mode="w", encoding="utf-8") as f:
            f.write('{"a": 1, "b": 2,}')  # Invalid trailing comma
        expected_error = RuntimeError.__name__

        # ACT
        try:
            json_util.load_json_file(self.file_path)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_missing_file(self):
        """
        Should raise RuntimeError if the file does not exist.
        """
        # ARRANGE
        missing_path = os.path.join(self.tmpdir, "missing.json")
        expected_error = RuntimeError.__name__

        # ACT
        try:
            json_util.load_json_file(missing_path)
            result = ""  # No exception raised
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


class TestSaveJsonFile(unittest.TestCase):
    """
    Unit tests for the `save_json_file` function.

    This suite verifies that a dictionary is serialized and saved to disk as JSON,
    that optional indentation is honored, that Unicode is preserved (ensure_ascii=False),
    and that errors are wrapped in `RuntimeError` for non-serializable data or invalid paths.

    Tests follow Arrange–Act–Assert and focus on input→output/side-effect behavior defined
    in the function body (writing JSON text to a file using `json.dump` with `ensure_ascii=False`).
    """

    def setUp(self):
        """Create a temporary directory for test artifacts."""
        self.tmpdir = tempfile.mkdtemp(prefix="save_json_test_")
        self.file_path = os.path.join(self.tmpdir, "out.json")

    def tearDown(self):
        """Remove any temporary files/directories created during tests."""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_valid_json_compact(self):
        """
        Should write a compact JSON file when indent_spaces=None.
        """
        # ARRANGE
        data = {"name": "Alice", "age": 30, "active": True}
        expected_text = json.dumps(data, indent=None, ensure_ascii=False)

        # ACT
        json_util.save_json_file(self.file_path, data, indent_spaces=None)

        # ASSERT
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            written_text = f.read()
        with self.subTest(Out=written_text, Exp=expected_text):
            self.assertEqual(written_text, expected_text)

        # Also confirm round-trip parses to the same dict
        parsed = json.loads(written_text)
        with self.subTest(Out=parsed, Exp=data):
            self.assertEqual(parsed, data)

    def test_with_indent(self):
        """
        Should write pretty-printed JSON when indent_spaces is provided.
        """
        # ARRANGE
        data = {"city": "Paris", "population": 2148327}
        indent_spaces = 4
        expected_text = json.dumps(data, indent=indent_spaces, ensure_ascii=False)

        # ACT
        json_util.save_json_file(self.file_path, data, indent_spaces=indent_spaces)

        # ASSERT
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            written_text = f.read()
        with self.subTest(Out=written_text, Exp=expected_text):
            self.assertEqual(written_text, expected_text)

        parsed = json.loads(written_text)
        with self.subTest(Out=parsed, Exp=data):
            self.assertEqual(parsed, data)

    def test_unicode(self):
        """
        Should preserve Unicode characters without escaping (ensure_ascii=False).
        """
        # ARRANGE
        data = {"greeting": "こんにちは", "emoji": "😀", "currency": "€"}
        # The exact bytes should match json.dumps with ensure_ascii=False
        expected_text = json.dumps(data, ensure_ascii=False, indent=2)

        # ACT
        json_util.save_json_file(self.file_path, data, indent_spaces=2)

        # ASSERT
        with open(self.file_path, mode="r", encoding="utf-8") as f:
            written_text = f.read()
        with self.subTest(Out=written_text, Exp=expected_text):
            self.assertEqual(written_text, expected_text)

        # Additionally ensure characters are present literally (not escaped)
        contains_unicode = all(s in written_text for s in ["こんにちは", "😀", "€"])
        with self.subTest(Out=contains_unicode, Exp=True):
            self.assertTrue(contains_unicode)

    def test_non_serializable(self):
        """
        Should raise RuntimeError when data contains non-serializable values.
        """
        # ARRANGE
        data = {"callback": lambda x: x}  # Functions are not JSON-serializable
        expected_error = RuntimeError.__name__

        # ACT
        try:
            json_util.save_json_file(self.file_path, data)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_missing_parent_directory(self):
        """
        Should raise RuntimeError when the target directory does not exist.
        """
        # ARRANGE
        missing_dir_path = os.path.join(self.tmpdir, "does_not_exist", "out.json")
        expected_error = RuntimeError.__name__

        # ACT
        try:
            json_util.save_json_file(missing_dir_path, {"a": 1})
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)


if __name__ == "__main__":
    unittest.main()
