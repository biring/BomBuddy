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
import re
import copy

import src.utils.json as json_util

from datetime import datetime, timezone


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


class TestParseStrictKeyValueToDict(unittest.TestCase):
    """
    Unit tests for the `parse_strict_key_value_to_dict` function in `src.utils.json`.

    This suite verifies that a quoted key–value configuration text is parsed into a
    dictionary when lines conform to the strict `"Key" = "Value"` format, while:
      - Ignoring empty lines and comment-only lines.
      - Stripping trailing comments introduced by `#`.
      - Skipping invalid lines without failing.
      - Raising an error on duplicate keys.

    Scope: Tests focus strictly on input→output behavior implemented in the function,
    without asserting on logging/printing side effects for invalid lines.
    """

    def test_basic_parsing(self):
        """
        Should parse multiple valid lines into a dictionary.
        """
        # ARRANGE
        src = "config.txt"
        text = (
            '"Name" = "Alice"\n'
            '"City" = "Paris"\n'
            '"Age" = "30"\n'
        )
        expected = {"Name": "Alice", "City": "Paris", "Age": "30"}

        # ACT
        result = json_util.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_trailing_comments_and_whitespace(self):
        """
        Should strip trailing comments and surrounding whitespace before validation.
        """
        # ARRANGE
        src = "cfg.conf"
        text = (
            '   "KeyA"   =   "Value A"    # trailing comment\n'
            '"KeyB"="Value B"#another comment\n'
            '"KeyC" = ""   # empty string value is allowed\n'
        )
        expected = {"KeyA": "Value A", "KeyB": "Value B", "KeyC": ""}

        # ACT
        result = json_util.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_ignores_comments_and_empty_lines(self):
        """
        Should ignore blank lines and lines that are comments (including those reduced to empty after '#').
        """
        # ARRANGE
        src = "settings.kv"
        text = (
            "\n"
            "# Full-line comment\n"
            '   # Indented full-line comment\n'
            '"Mode" = "Prod"\n'
            '   # comment only after spaces\n'
            '"Level" = "High"  # keep this\n'
            "   \n"
            " # another (indented) comment line\n"
        )
        expected = {"Mode": "Prod", "Level": "High"}

        # ACT
        result = json_util.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_invalid_lines_are_skipped(self):
        """
        Should skip non-conforming lines and keep only valid `"Key" = "Value"` entries.
        """
        # ARRANGE
        src = "bad_lines.txt"
        text = (
            'Key = "no_quotes_on_key"\n'  # invalid (key not quoted)
            '"NoEquals"  "MissingEquals"\n'  # invalid (no equals)
            '"Good" = "Yes"\n'  # valid
            '"AlsoGood"="True"\n'  # valid
            '"Bad" = "Unclosed\n'  # invalid (unterminated quote)
        )
        expected = {"Good": "Yes", "AlsoGood": "True"}

        # ACT
        result = json_util.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_duplicate_keys_raises(self):
        """
        Should raise RuntimeError if the same key appears more than once.
        """
        # ARRANGE
        src = "dupe.cfg"
        text = (
            '"A" = "1"\n'
            '"B" = "2"\n'
            '"A" = "3"\n'  # duplicate key: "A"
        )
        expected_error = RuntimeError.__name__

        # ACT
        try:
            json_util.parse_strict_key_value_to_dict(src, text)
            result = ""  # No exception raised (unexpected)
        except Exception as e:
            result = type(e).__name__

        # ASSERT
        with self.subTest(Out=result, Exp=expected_error):
            self.assertEqual(result, expected_error)

    def test_all_whitespace_and_trailing_comment_only_lines(self):
        """
        Should ignore lines that become empty after stripping trailing comments and whitespace.
        """
        # ARRANGE
        src = "comments_only.txt"
        text = (
            "   # just a comment\n"
            "\t  # another comment with leading whitespace\n"
            '"K" = "V"   # valid with trailing comment\n'
            "   #\n"
        )
        expected = {"K": "V"}

        # ACT
        result = json_util.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_value_empty_string_is_allowed(self):
        """
        Should allow empty quoted values (`""`) and parse them as empty strings.
        """
        # ARRANGE
        src = "empty_value.cfg"
        text = '"Empty" = ""\n"NonEmpty" = "x"'
        expected = {"Empty": "", "NonEmpty": "x"}

        # ACT
        result = json_util.parse_strict_key_value_to_dict(src, text)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestNowUtcIso(unittest.TestCase):
    """
    Unit tests for the `now_utc_iso` function in `src.utils.json`.

    This suite verifies that the function:
      - Returns an ISO 8601 timestamp string with a 'Z' UTC suffix.
      - Is precise to the second (no microseconds present).
      - Produces a time value consistent with the current UTC time at call.
    """

    def test_format_and_suffix(self):
        """
        Should return a string in the exact 'YYYY-MM-DDTHH:MM:SSZ' format with 'Z' suffix.
        """
        # ARRANGE
        iso_regex = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        # ACT
        result = json_util.now_utc_iso()

        # ASSERT
        # Type check
        with self.subTest(Out=type(result).__name__, Exp=str.__name__):
            self.assertIsInstance(result, str)

        # Ends with 'Z'
        with self.subTest(Out=result.endswith("Z"), Exp=True):
            self.assertTrue(result.endswith("Z"))

        # Exact length "YYYY-MM-DDTHH:MM:SSZ" == 20 chars
        with self.subTest(Out=len(result), Exp=20):
            self.assertEqual(len(result), 20)

        # 'T' separator at the expected index (10)
        with self.subTest(Out=result[10], Exp="T"):
            self.assertEqual(result[10], "T")

        # Matches strict ISO pattern with Z suffix
        with self.subTest(Out=bool(iso_regex.match(result)), Exp=True):
            self.assertTrue(iso_regex.match(result) is not None)

        # No microseconds or explicit offset in the string
        with self.subTest(Out=("." in result), Exp=False):
            self.assertNotIn(".", result)
        with self.subTest(Out=("+00:00" in result), Exp=False):
            self.assertNotIn("+00:00", result)

    def test_value_within_current_utc_bounds(self):
        """
        Should produce a timestamp that falls between the UTC instants captured
        immediately before and after the call (inclusive), at second precision.
        """
        # ARRANGE
        # Capture lower bound (truncate to seconds)
        lower = datetime.now(timezone.utc).replace(microsecond=0)

        # ACT
        text_ts = json_util.now_utc_iso()

        # Capture upper bound (truncate to seconds)
        upper = datetime.now(timezone.utc).replace(microsecond=0)

        # Convert back to aware UTC datetime for comparison
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        # Ensure parsed time is between lower and upper (inclusive)
        with self.subTest(Out=parsed.isoformat(), Exp=f"[{lower.isoformat()} .. {upper.isoformat()}]"):
            self.assertLessEqual(lower, parsed)
            self.assertLessEqual(parsed, upper)

    def test_second_precision_no_microseconds(self):
        """
        Should represent time with second-level precision only (no microseconds).
        """
        # ARRANGE & ACT
        text_ts = json_util.now_utc_iso()
        parsed = datetime.strptime(text_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)

        # ASSERT
        with self.subTest(Out=parsed.microsecond, Exp=0):
            self.assertEqual(parsed.microsecond, 0)


class TestComputeDictChecksumUint32(unittest.TestCase):
    """
    Unit tests for `compute_dict_checksum_uint32` in `src.utils.json`.

    These tests verify deterministic, order-independent checksumming of a dict by:
      - Sorting keys lexicographically,
      - Concatenating key+value text (values stringified),
      - UTF-8 byte summation modulo 2^32.

    Scope: Input→output correctness only. No mocks, no logging/print assertions.
    """

    def test_example_from_docstring_ascii(self):
        """
        Should match the worked example: {"a": "1", "b": "2"} → sum("a1b2") = 294.
        """
        # ARRANGE
        data = {"b": "2", "a": "1"}  # Deliberately unsorted order
        expected = 294  # 'a1b2' bytes → 97+49+98+50

        # ACT
        result = json_util.compute_dict_checksum_uint32(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_insertion_order_independence(self):
        """
        Should produce the same checksum regardless of dict insertion order.
        """
        # ARRANGE
        data_a = {"x": "10", "a": "Z", "m": "7"}
        data_b = {"m": "7", "x": "10", "a": "Z"}  # Same pairs, different order

        # ACT
        result_a = json_util.compute_dict_checksum_uint32(data_a)
        result_b = json_util.compute_dict_checksum_uint32(data_b)

        # ASSERT
        with self.subTest(Out=result_a, Exp=result_b):
            self.assertEqual(result_a, result_b)

    def test_empty_dict_returns_zero(self):
        """
        Should return 0 for an empty dictionary (no bytes to sum).
        """
        # ARRANGE
        data = {}
        expected = 0

        # ACT
        result = json_util.compute_dict_checksum_uint32(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_unicode_utf8_handling(self):
        """
        Should correctly sum UTF-8 bytes for non-ASCII characters.
        Example: {"a": "1", "Δ": "é"} → bytes("a1Δé") = [97,49,206,148,195,169] → 864.
        """
        # ARRANGE
        data = {"Δ": "é", "a": "1"}  # Sorted keys: "a", "Δ" → concat "a1Δé"
        expected = 864  # 97 + 49 + 206 + 148 + 195 + 169

        # ACT
        result = json_util.compute_dict_checksum_uint32(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_value_stringification_for_non_string_values(self):
        """
        Should convert non-string values to strings before concatenation.
        Example: {"x": 10, "y": True} → concat "x10yTrue" → sum = 754.
        """
        # ARRANGE
        data = {"x": 10, "y": True}  # str(10) → "10", str(True) → "True"
        expected = 754  # bytes("x10yTrue") sum

        # ACT
        result = json_util.compute_dict_checksum_uint32(data)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_uint32_range_property_on_reasonable_input(self):
        """
        Should always return an int within the uint32 range [0, 2^32-1].
        (Property check on a moderately sized input.)
        """
        # ARRANGE
        # Build a moderately large mapping; keys sort lexicographically due to zero-padding.
        data = {f"k{str(i).zfill(4)}": f"v{str(i * i)}" for i in range(0, 500)}

        # ACT
        result = json_util.compute_dict_checksum_uint32(data)

        # ASSERT
        in_range = 0 <= result <= 0xFFFFFFFF
        with self.subTest(Out=in_range, Exp=True):
            self.assertTrue(in_range)


class TestVerifyFoundationJsonChecksum(unittest.TestCase):
    """
    Unit tests for `verify_foundation_json_checksum` in `src.utils.json`.

    This suite validates that the function:
      - Returns True when the stored checksum (int or numeric string) matches the checksum
        recomputed from the `data` section.
      - Returns False when either the data changes or the stored checksum is incorrect.

    Scope: Input→output correctness only (no mocking). Assumes a well-formed object with
    required keys per the function contract.
    """

    def test_matches_checksum_with_int_meta(self):
        """
        Should return True when meta.checksum (int) matches the computed checksum of data.
        """
        # ARRANGE
        data = {"a": "1", "b": "2", "Δ": "é"}  # Realistic sample including Unicode
        checksum = json_util.compute_dict_checksum_uint32(data)
        obj = {"meta": {"checksum": checksum}, "data": data}
        expected = True

        # ACT
        result = json_util.verify_foundation_json_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_matches_checksum_with_string_meta(self):
        """
        Should return True when meta.checksum is a numeric string that equals the computed checksum.
        """
        # ARRANGE
        data = {"x": 10, "y": True, "z": "ok"}  # Non-string values get stringified in checksum helper
        checksum = json_util.compute_dict_checksum_uint32(data)
        obj = {"meta": {"checksum": str(checksum)}, "data": data}
        expected = True

        # ACT
        result = json_util.verify_foundation_json_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_returns_false_when_data_changed(self):
        """
        Should return False if data changes after checksum was computed and stored.
        """
        # ARRANGE
        original_data = {"k1": "v1", "k2": "v2"}
        checksum = json_util.compute_dict_checksum_uint32(original_data)

        # Create object but tamper the data (simulate drift) without updating checksum
        obj = {"meta": {"checksum": checksum}, "data": {"k1": "v1", "k2": "v2X"}}
        expected = False

        # ACT
        result = json_util.verify_foundation_json_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

    def test_returns_false_when_checksum_incorrect(self):
        """
        Should return False if the stored checksum does not match the computed checksum.
        """
        # ARRANGE
        data = {"alpha": "A", "beta": "B"}
        correct_checksum = json_util.compute_dict_checksum_uint32(data)

        # Use an incorrect checksum (off-by-one) in meta
        obj = {"meta": {"checksum": correct_checksum + 1}, "data": data}
        expected = False

        # ACT
        result = json_util.verify_foundation_json_checksum(obj)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


class TestExtractFoundationData(unittest.TestCase):
    """
    Unit tests for `extract_foundation_data` in `src.utils.json`.

    This suite verifies that the function:
      - Returns a new `dict` (not the same object) containing the same key/value pairs.
      - Performs a *shallow* copy: top-level mutations to the returned dict do not
        affect the original, while mutations to shared nested objects are visible.
      - Accepts a value for `foundation['data']` that is convertible to `dict`.

    Scope: Input→output correctness only; assumes well-formed input per the function
    contract and does not test exceptions or logging.
    """

    def test_returns_new_equal_dict(self):
        """
        Should return a new dict equal in content, not the same object identity.
        """
        # ARRANGE
        foundation = {"data": {"a": 1, "b": 2}}
        expected = {"a": 1, "b": 2}

        # ACT
        result = json_util.extract_foundation_data(foundation)

        # ASSERT
        with self.subTest(Out=isinstance(result, dict), Exp=True):
            self.assertIsInstance(result, dict)

        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)

        with self.subTest(Out=(result is foundation["data"]), Exp=False):
            self.assertIsNot(result, foundation["data"])

    def test_shallow_copy_semantics(self):
        """
        Should behave as a shallow copy:
          - Top-level mutations on the returned dict do not affect the source.
          - Nested objects remain shared (mutations reflect in both).
        """
        # ARRANGE
        nested = {"count": 1}
        foundation = {"data": {"x": 10, "meta": nested}}
        original_top_level = copy.deepcopy(foundation["data"])  # Snapshot of original top-level

        # ACT
        result = json_util.extract_foundation_data(foundation)

        # Mutate top-level of result (add a new key)
        result["y"] = 99

        # Mutate a nested shared object from result
        result["meta"]["count"] = 42

        # ASSERT
        # Top-level addition should NOT appear in source (different dict objects)
        with self.subTest(Out=("y" in foundation["data"]), Exp=False):
            self.assertNotIn("y", foundation["data"])

        # Nested mutation should reflect in both (since nested object is shared in shallow copy)
        with self.subTest(Out=foundation["data"]["meta"]["count"], Exp=42):
            self.assertEqual(foundation["data"]["meta"]["count"], 42)

        # Unchanged original keys remain intact aside from intentional nested change
        with self.subTest(Out=foundation["data"]["x"], Exp=original_top_level["x"]):
            self.assertEqual(foundation["data"]["x"], original_top_level["x"])

    def test_accepts_mapping_convertible_value(self):
        """
        Should accept a `foundation['data']` value that can be converted to a dict (e.g., list of pairs).
        """
        # ARRANGE
        foundation = {"data": [("a", "1"), ("b", "2")]}
        expected = {"a": "1", "b": "2"}

        # ACT
        result = json_util.extract_foundation_data(foundation)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
