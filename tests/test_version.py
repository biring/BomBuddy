import unittest
import re
from src.version import __version__
from src.version import __build__

class TestVersionFormat(unittest.TestCase):

    def test_version_format(self):
        # Define a regex pattern for the version format
        pattern = r'^\d+\.\d+\.\d+$'

        # Check if the version matches the pattern
        self.assertRegex(__version__, pattern, f"Version string '{__version__}' is not formatted correctly.")

    def test_build_format(self):
        # Define a regex pattern for the build format
        pattern = r'^\d+$'

        # Check if the build matches the pattern
        self.assertRegex(__build__, pattern, f"Build number '{__build__}' is not formatted correctly.")

if __name__ == '__main__':
    unittest.main()