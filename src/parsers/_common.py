"""
Utilities for matching and validating labeled rows in a DataFrame.

This module provides functions to:
 - Identify the row in a DataFrame with the highest number of matching labels
 - Determine which expected labels are missing from the best-matching row
 - Normalize strings before performing matches (case, whitespace, non-printable chars)

These utilities are useful for parsing semi-structured tabular data, such as
imported CSV files where header rows may vary in format or position.

Example Usage:
    # Preferred usage via public package interface:
    # Not applicable — this function is internal and not exposed via public API.

    # Direct module usage (acceptable in unit tests or internal scripts only):
    > from src.parsers._common import find_unmatched_labels_in_best_row
    > unmatched = find_unmatched_labels_in_best_row(df, ["Account", "Amount", "Date"])

Dependencies:
 - Python >= 3.10
 - pandas
 - src.utils.text_sanitizer (for normalization helpers)

Notes:
 - Assumes all inputs are small to moderately sized DataFrames in memory.
 - Matching is tolerant during row selection (substring match), but strict during validation (exact match).
 - Internal use only; leading underscores denote non-public API functions.

License:
 - Internal Use Only
"""

from typing import Final

import pandas as pd
from src.utils import (
    normalize_to_string,
    remove_all_whitespace,
    remove_non_printable_ascii,
)

# Module constants
NO_BEST_MATCH_ROW: Final = -1  # Valid dataframe row number be will zero or higher. So pick something that is invalid


def find_row_with_most_label_matches(df: pd.DataFrame, labels: list[str]) -> int:
    """
    Identifies the row in the DataFrame with the highest number of normalized label matches.

    A label is considered matched if its normalized form—stripped of whitespace,
    non-printable ASCII characters, and case—is found as a **substring** within any string
    cell in the row. Each label is only counted once per row, even if it appears in multiple cells.

    This function is used for fuzzy identification of the most likely header row in
    semi-structured tabular data.

    Args:
        df (pd.DataFrame): The DataFrame to search for label matches.
        labels (list[str]): A list of labels to match against each row in the DataFrame.

    Returns:
        int: Index of the row with the most label matches. Returns NO_BEST_MATCH_ROW (-1)
             if no labels match in any row.
    """
    # Local variable
    best_row_index = NO_BEST_MATCH_ROW
    highest_match_count = 0

    # Normalize each string cell in labels row for consistent label comparison
    normalized_labels = [_normalize_label_text(label) for label in labels]

    # Iterate over all the rows in the data frame
    for row_index, row in df.iterrows():

        # Start with match count of zero
        match_count = 0
        # Normalize each string cell in the row for consistent label comparison.
        sanitized_cells = [_normalize_label_text(cell) for cell in row if isinstance(cell, str)]

        # Check each label one at a time
        for norm_label in normalized_labels:
            if any(norm_label in norm_cell for norm_cell in sanitized_cells):
                match_count += 1

        # When all the cells in the row are checked determine if it is the best match
        if match_count > highest_match_count:
            highest_match_count = match_count
            best_row_index = row_index

    return best_row_index


def find_unmatched_labels_in_best_row(df: pd.DataFrame, required_labels: list[str]) -> list[str]:
    """
    Returns the list of required labels that are not exactly matched in the best-matching row.

    The best-matching row is first identified using partial **substring** matching
    (via `find_row_with_most_label_matches`). This function then performs a strict
    **exact match** (after normalization) between each required label and the values
    in the best-matching row.

    Normalization removes all whitespace, non-printable ASCII characters, and applies
    lowercase comparison.

    This stricter validation step ensures that each required label is precisely represented
    in the selected row.

    Args:
        df (pd.DataFrame): The DataFrame to evaluate for label matches.
        required_labels (list[str]): A list of expected labels to verify against the best-matching row.

    Returns:
        list[str]: A list of labels that were not exactly matched in the best-matching row.
    """

    # Get best match row
    best_match_row = find_row_with_most_label_matches(df, required_labels)

    # When no match is found
    if best_match_row == NO_BEST_MATCH_ROW:
        return required_labels  # return all labels as unmatched list

    # Local variables
    unmatched_labels = []

    # Get best match row as a list
    row_values = df.iloc[best_match_row].astype(str).tolist()

    # Normalize strings for consistent comparison.
    normalized_row = [_normalize_label_text(cell) for cell in row_values]
    normalized_labels = [_normalize_label_text(label) for label in required_labels]

    # Iterate over all the labels
    for label, norm_label in zip(required_labels, normalized_labels):
        # When label is not found in the row
        if not any(norm_label == norm_cell for norm_cell in normalized_row):
            # Add unmatched label to result list
            unmatched_labels.append(label)

    return unmatched_labels


def _normalize_label_text(text: object) -> str:
    """
    Normalizes input text for consistent label matching.

    This helper function standardizes various types of input to enable
    reliable comparison of label strings. It performs the following:
    - Converts the input to a string using `normalize_to_string`
    - Removes all non-printable ASCII characters
    - Eliminates all whitespace characters (including tabs and newlines)
    - Converts the final result to lowercase

    This is used internally for both fuzzy (substring) and exact label matching
    to ensure robustness against formatting differences in raw data.

    Args:
        text (object): The input to normalize. Can be a string, number, None, or other type.

    Returns:
        str: A fully normalized lowercase string, stripped of whitespace and non-printable characters.
    """
    normalized = normalize_to_string(text)
    return remove_all_whitespace(remove_non_printable_ascii(normalized)).lower()
