import os
import tempfile
import shutil
import unittest
import importlib

# noinspection PyProtectedMember
import src.runtime._info as info
# noinspection PyProtectedMember
import src.runtime._common as common

from src.utils import json as json_util


class TestLoad(unittest.TestCase):
    """
    Unit tests for the `load` function in the `src.runtime._info` module.

    These tests ensure that:
      - The '_info' resource is loaded only when not already in cache.
      - Required keys are validated from the JSON file.
      - The cache contains the correct mapping after load.
    """

    def setUp(self):
        """
        Prepare a temporary runtime directory and patch `_common` resolution
        to point to it for predictable testing.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.runtime_dir = os.path.join(self.temp_dir, "src", "runtime")
        os.makedirs(self.runtime_dir)

        # Build a minimal valid foundation JSON file
        from src.utils import json as json_util
        data_map = {k: f"value_for_{k}" for k in info.info_key.REQUIRED_KEYS}
        foundation_obj = json_util.create_foundation_json(data_map, "_info.json")
        json_path = os.path.join(self.runtime_dir, "_info.json")
        json_util.save_json_file(json_path, foundation_obj)

        # Patch _common to resolve JSON path from temp dir
        self.original_resolve = common._resolve_json_file_path

        def fake_resolve_json_file_path(resource_name: str, base_dir=None):
            return os.path.join(self.runtime_dir, resource_name + ".json")

        common._resolve_json_file_path = fake_resolve_json_file_path

    def tearDown(self):
        """
        Clean up temporary files and restore patched functions/modules.
        """
        shutil.rmtree(self.temp_dir)
        common._resolve_json_file_path = self.original_resolve
        importlib.reload(info)  # resets cache

    def test_loads_when_not_in_cache(self):
        """
        Should load '_info' resource into cache when not already loaded.
        """
        # ARRANGE
        self.assertFalse(info.cache.is_loaded(info.SOURCE))

        # ACT
        info.load()
        loaded = info.cache.is_loaded(info.SOURCE)

        # ASSERT
        with self.subTest(Out=loaded, Exp=True):
            self.assertTrue(loaded)
        for key in info.info_key.REQUIRED_KEYS:
            value = info.cache.get_value(info.SOURCE, key)
            expected_value = f"value_for_{key}"
            with self.subTest(Key=key, Out=value, Exp=expected_value):
                self.assertEqual(value, expected_value)

    def test_does_not_reload_if_already_loaded(self):
        """
        Should skip reloading if '_info' resource is already loaded in cache.
        """
        # ARRANGE
        preload_map = {k: "preloaded" for k in info.info_key.REQUIRED_KEYS}
        info.cache.load_resource(info.SOURCE, preload_map)

        # ACT
        info.load()
        result_map = {k: info.cache.get_value(info.SOURCE, k) for k in preload_map}

        # ASSERT
        for key, value in result_map.items():
            with self.subTest(Key=key, Out=value, Exp="preloaded"):
                self.assertEqual(value, "preloaded")


class TestGet(unittest.TestCase):
    """
    Unit tests for the `get` function in `src.runtime._info`.

    This test suite verifies:
      - Lazy loading occurs when the cache is empty.
      - A valid key returns the expected string value.
      - Non-string `key` raises `TypeError`.
      - Missing keys raise `KeyError` with the function's wrapped message.
    """

    def setUp(self):
        """
        Create a temporary runtime directory with a valid `_info.json`
        and patch `_common._resolve_json_file_path` to point there.
        """
        # ARRANGE (fixture)
        self.temp_dir = tempfile.mkdtemp()
        self.runtime_dir = os.path.join(self.temp_dir, "src", "runtime")
        os.makedirs(self.runtime_dir)

        # Build a minimal-valid foundation JSON using real REQUIRED_KEYS
        self.data_map = {k: f"value_for_{k}" for k in info.info_key.REQUIRED_KEYS}
        foundation = json_util.create_foundation_json(self.data_map, "_info.json")
        self.json_path = os.path.join(self.runtime_dir, "_info.json")
        json_util.save_json_file(self.json_path, foundation)

        # Patch resolver so _info.load() reads from our temp file
        self._orig_resolve = common._resolve_json_file_path

        def _fake_resolve(resource_name: str, base_dir=None):
            # Only route the requested resource to our temp runtime dir
            return os.path.join(self.runtime_dir, resource_name + ".json")

        common._resolve_json_file_path = _fake_resolve

        # Ensure a clean cache per test (reload module to reset module-level `cache`)
        importlib.reload(info)

    def tearDown(self):
        """
        Remove temp artifacts and restore patched functions/modules.
        """
        common._resolve_json_file_path = self._orig_resolve
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        # Reset module cache to avoid cross-test contamination
        importlib.reload(info)

    def test_returns_value_for_existing_key_and_lazy_loads(self):
        """
        Should lazily load the resource when cache is empty and return the expected value.
        """
        # ARRANGE
        self.assertFalse(info.cache.is_loaded(info.SOURCE))  # precondition

        # Choose a real key from REQUIRED_KEYS
        test_key = next(iter(info.info_key.REQUIRED_KEYS))
        expected = self.data_map[test_key]

        # ACT
        result = info.get(test_key)
        loaded_after = info.cache.is_loaded(info.SOURCE)

        # ASSERT
        with self.subTest(Out=result, Exp=expected):
            self.assertEqual(result, expected)
        with self.subTest(Out=loaded_after, Exp=True):
            self.assertTrue(loaded_after)

    def test_raises_type_error_for_non_string_key(self):
        """
        Should raise TypeError when `key` is not a string.
        """
        # ARRANGE
        bad_key = 123  # non-string key
        expected_exception_name = TypeError.__name__

        # ACT
        try:
            info.get(bad_key)  # type: ignore[arg-type]
            result_exception_name = ""
        except Exception as e:
            result_exception_name = type(e).__name__

        # ASSERT
        with self.subTest(Out=result_exception_name, Exp=expected_exception_name):
            self.assertEqual(result_exception_name, expected_exception_name)

    def test_raises_key_error_for_missing_key_with_wrapped_message(self):
        """
        Should raise KeyError for a missing key, using the wrapped message from `get()`.
        """
        # ARRANGE
        # Make sure resource is loaded from our temp file
        info.load()
        missing_key = "__NOT_PRESENT__"
        expected_exception_name = KeyError.__name__

        # ACT
        try:
            info.get(missing_key)
            result_exception_name = ""
        except Exception as e:
            result_exception_name = type(e).__name__
            # Optional: verify the wrapped message shape from `get()`
            # (scope-limited to the function's behavior, not internal Cache wording)
            with self.subTest(Out=str(e), Exp_contains=missing_key):
                self.assertIn(missing_key, str(e))

        # ASSERT
        with self.subTest(Out=result_exception_name, Exp=expected_exception_name):
            self.assertEqual(result_exception_name, expected_exception_name)


if __name__ == "__main__":
    unittest.main()
