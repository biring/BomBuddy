import unittest
import re
from src.version import __version__


class TestVersionFormat(unittest.TestCase):

    def test_version_format(self):
        # Define a regex pattern for the version format
        version_pattern = r'^\d+\.\d+\.\d+$'

        # Check if the version matches the pattern
        self.assertRegex(__version__, version_pattern, f"Version string '{__version__}' is not formatted correctly.")


if __name__ == '__main__':
    unittest.main()