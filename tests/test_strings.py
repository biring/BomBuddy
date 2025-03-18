import unittest
import pandas as pd
from src.strings import strip_match_from_string

class TestStripMatchFromString(unittest.TestCase):
    def test_strip_match_from_string_basic_removal(self):
        print('test_strip_match_from_string_basic_removal')
        # Test data
        self.data = {
            'pattern':  ['abc',         'defg',     'fgh'],
            'search':   ['abcdefgh',    'abcdefgh', 'abcdefgh']
        }
        self.df = pd.DataFrame(self.data)
        # Call the function
        result_df = strip_match_from_string(self.df.copy(), 'pattern', 'search')
        # Expected result
        expected_result = {
            'pattern':  ['abc',         'defg',     'fgh'],
            'search':   ['defgh',       'abch',     'abcde']
        }
        expected_df = pd.DataFrame(expected_result)
        # Check result
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_strip_match_from_string_no_match(self):
        print('test_strip_match_from_string_no_match')
        # Test data
        self.data = {
            'pattern':  ['bcd',         '0123',         '!@#$'],
            'search':   ['abc123@#$',   'abc123@#$',    'abc123@#$']
        }
        self.df = pd.DataFrame(self.data)
        # Call the function
        result_df = strip_match_from_string(self.df.copy(), 'pattern', 'search')
        # Expected result
        expected_result = {
            'pattern':  ['bcd',         '0123',         '!@#$'],
            'search':   ['abc123@#$',   'abc123@#$',    'abc123@#$']
        }
        expected_df = pd.DataFrame(expected_result)
        # Check result
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_strip_match_from_string_special_characters(self):
        print('test_strip_match_from_string_special_characters')
        # Test data
        self.data = {
            'pattern':  ['#123',        '#789-',        '-456'],
            'search':   ['abc#123xyz',  'ghi#789-xyz',  'def-456ghi']
        }
        self.df = pd.DataFrame(self.data)
        # Call the function
        result_df = strip_match_from_string(self.df.copy(), 'pattern', 'search')
        # Expected result
        expected_result = {
            'pattern':  ['#123',        '#789-',        '-456'],
            'search':   ['abcxyz',      'ghixyz',       'defghi']
        }
        expected_df = pd.DataFrame(expected_result)
        # Check result
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_strip_match_from_string_edge_case_empty_column(self):
        print('test_strip_match_from_string_edge_case_empty_column')
        # Test data
        self.data = {
            'pattern': [],
            'search': []
        }
        self.df = pd.DataFrame(self.data)
        # Call the function
        result_df = strip_match_from_string(self.df.copy(), 'pattern', 'search')
        # Expected result
        expected_result = {
            'pattern': [],
            'search': []
        }
        expected_df = pd.DataFrame(expected_result)
        # Check result
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_strip_match_from_string_pattern_column_with_spaces(self):
        print('test_strip_match_from_string_pattern_column_with_spaces')
        # Test data
        self.data = {
            'pattern':  [' 123 ',       '  #123 ',      ' -456 '],
            'search':   ['abc123xyz',   'abc#123xyz',   'def-456ghi']
        }
        self.df = pd.DataFrame(self.data)
        # Call the function
        result_df = strip_match_from_string(self.df.copy(), 'pattern', 'search')
        # Expected result
        expected_result = {
            'pattern':  [' 123 ',       '  #123 ',      ' -456 '],
            'search':   ['abcxyz',      'abcxyz',       'defghi']
        }
        expected_df = pd.DataFrame(expected_result)
        # Check result
        pd.testing.assert_frame_equal(result_df, expected_df)


if __name__ == "__main__":
    unittest.main()
