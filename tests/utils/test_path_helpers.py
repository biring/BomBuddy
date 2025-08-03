"""Unit tests for filesystem path helper utilities.

This module exercises the small helpers in ``src.utils.path_helpers`` to ensure
consistent behaviour across operating systems and edge cases.

The tests cover:

* ``join`` – cross‑platform concatenation of path fragments.
* ``normalize`` – collapsing redundant separators and expanding ``~``.
* ``project_root`` – discovery of the repository root and error handling when
  no markers are present.

Example Usage
-------------
    # From project root
    python -m unittest tests/utils/test_path_helpers.py

Dependencies
------------
* Python >= 3.9
* Standard Library: unittest, tempfile, os

Notes
-----
* These tests rely solely on the public API exported by ``src.utils``.
"""

import os
import tempfile
import unittest

from src.utils import join, normalize, project_root


class TestPathHelpers(unittest.TestCase):

    def test_join(self):
        """Ensures wrapper mirrors :func:`os.path.join` semantics."""
        parts = ["foo", "bar", "baz"]
        expected = os.path.join(*parts)
        self.assertEqual(join(*parts), expected)

    def test_normalize(self):
        """Verify tilde expansion and separator normalization."""
        raw = os.path.join("~", "some", "..", "folder")
        expected = os.path.normpath(os.path.expanduser(raw))
        self.assertEqual(normalize(raw), expected)

    def test_project_root_from_file(self):
        """Detect repository root starting from a file path."""
        # Compute expected root using os.path directly for test isolation.
        path = os.path.abspath(__file__)
        expected = path
        while True:
            expected = os.path.dirname(expected)
            if os.path.exists(os.path.join(expected, ".git")):
                break

        self.assertEqual(project_root(__file__), expected)

    def test_project_root_not_found(self):
        """Raise ``FileNotFoundError`` when no marker exists."""
        with tempfile.TemporaryDirectory() as tmp:
            nested = os.path.join(tmp, "a", "b")
            os.makedirs(nested)
            with self.assertRaises(FileNotFoundError):
                project_root(nested)


if __name__ == "__main__":
    unittest.main()

