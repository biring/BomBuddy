"""
Utilities for identifying and validating labeled rows in semi-structured DataFrames.

This module provides functionality to:
 - Detect the most likely header row based on fuzzy label matching
 - Validate that all required labels exist in a row using exact matching
 - Extract metadata and BOM component tables from Excel-like sheets
 - Normalize strings for resilient header and label comparisons
 - Flatten DataFrames and retrieve values using fuzzy label indexing

These utilities support parsing tabular data (e.g., BOM sheets or form-like tables)
where headers may appear in different rows or with inconsistent formatting.

Example Usage:
 > import src.parsers._common as common
 > unmatched = common.find_unmatched_labels_in_best_row(df, ["Item", "Part Number", "Quantity"])

Dependencies:
 - Python >= 3.10
 - pandas
 - src.utils.text_sanitizer:
     - normalize_to_string
     - remove_all_whitespace
     - remove_non_printable_ascii

Notes:
 - Designed for internal use; functions are not part of a public API.
 - Matching is tolerant (substring) during row detection, but exact during validation.
 - Assumes inputs are moderately sized in-memory DataFrames, as from Excel or CSV.

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
NO_MATCH_IN_LIST: Final = -1  # Valid list number be will zero or higher. So pick something that is invalid
EMPTY_CELL_REPLACEMENT: Final = ""  # Empty cells in a dataframe default to an empty string


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


def _search_label_index(data: list[str], label: str) -> int:
    """
    Searches for the index of a label in a list using normalized exact matching.

    This function normalizes both the label and list elements using
    `_normalize_label_text`, and returns the index of the first exact match.

    Used to locate label positions in flattened metadata lists.

    Args:
        data (list[str]): List of candidate strings.
        label (str): Label to search for.

    Returns:
        int: Index of the matching element, or NO_MATCH_IN_LIST (-1) if not found.
    """
    for idx, value in enumerate(data):
        if _normalize_label_text(label) == _normalize_label_text(value):
            return idx

    return NO_MATCH_IN_LIST


def create_dict_from_row(row: pd.Series) -> dict[str, str]:
    """
    Converts a one-row pandas DataFrame (Series) into a dictionary
    with normalized column names as keys and cell values.

        This function is intended for processing metadata or BOM rows where column headers
        may be inconsistently formatted. Each column label is normalized and used as a key,
        with the corresponding cell value converted to a string if needed.This is useful
        when extracting key-value pairs from BOM or metadata rows where headers may be
        inconsistently formatted.

    Args:
        row (pd.Series): A single row from a pandas DataFrame.

    Returns:
        dict[str, str]: Dictionary with normalized keys and string values.
    """
    dictionary = {}

    for column_label, cell_value in row.items():
        key = _normalize_label_text(column_label)
        dictionary[key] = cell_value

    return dictionary


def extract_header(df: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    """
    Extracts the section above the BOM table from the given DataFrame.

    Finds the most probable BOM table header row, then returns all rows above it.
    Used to capture metadata like revision, date, or build stage.

    Args:
        df (pd.DataFrame): Full DataFrame for the sheet.
        labels (list[str]): Expected BOM column headers.

    Returns:
        pd.DataFrame: All rows above the detected header row.

    Raises:
        ValueError: If no suitable header row is found or header block is empty.
    """
    bom_table_header_row = find_row_with_most_label_matches(df, labels)

    if bom_table_header_row <= 0:
        raise ValueError("Header extraction failed: unable to locate BOM table header row.")

    bom_header = df.iloc[:bom_table_header_row]

    if bom_header.empty:
        raise ValueError("Header extraction failed: resulting header is empty.")

    return bom_header


def extract_label_value(data: list[str], label: str, skip_empty=True) -> str:
    """
    Extracts the value corresponding to a label from a flat list of alternating label-value pairs.

    Performs normalized substring matching to locate the label, then returns the next non-empty
    element as the value (unless skip_empty is False).

    Args:
        data (list[str]): Flat list of strings with label and value in sequence.
        label (str): Label whose associated value is to be retrieved.
        skip_empty (bool): If True, skips over empty or whitespace-only values when looking for the value.

    Returns:
        str: The value found after the matched label, or an empty string if the label is not found.

    Raises:
        ValueError: If the label is matched but no valid value follows it.
    """
    label_index = _search_label_index(data, label)

    if label_index == NO_MATCH_IN_LIST:
        # TODO: Log a warning when value for label is not found
        return ""

    for i in range(label_index + 1, len(data)):
        value = data[i]
        if not skip_empty or value:  # skip empty entries
            return value
    # Raise an error when label is found but not value as all labels should have a value
    raise ValueError(f"No value found for label = {label}, at index = {label_index}.")


def extract_row_cell(row: pd.Series, column_header: str) -> str:
    """
    Extracts and normalizes the value of a cell from a row using fuzzy column header matching.

    Normalizes both the requested column header and the row’s keys to allow resilient lookup.

    Args:
        row (pd.Series): Row from the BOM table.
        column_header (str): The desired column header to search for.

    Returns:
        str: Normalized string value if found; empty string otherwise.
    """
    norm_column_header = _normalize_label_text(column_header)
    normalized_row = create_dict_from_row(row)
    value = normalized_row.get(norm_column_header, "")
    return normalize_to_string(value)


def extract_table(df: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    """
    Extracts the BOM component table from the given DataFrame.

    Finds the most probable BOM table header row and returns all rows from that row onward.

    Args:
        df (pd.DataFrame): Full sheet as a DataFrame.
        labels (list[str]): Expected BOM header labels.

    Returns:
        pd.DataFrame: BOM table including the header and all following rows.

    Raises:
        ValueError: If no header is found or resulting table is empty.
    """
    bom_table_header_row = find_row_with_most_label_matches(df, labels)

    if bom_table_header_row < 0 or bom_table_header_row >= len(df):
        raise ValueError("Table extraction failed: unable to locate BOM table start row.")

    bom_table = df.iloc[bom_table_header_row:]

    if bom_table.shape[0] <= 1:
        raise ValueError("Table extraction failed: no data rows found in the table.")

    return bom_table


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


def flatten_dataframe(df: pd.DataFrame) -> list[str]:
    """
    Flattens the entire DataFrame into a single list of strings.

    Includes column headers followed by all cell values. Replaces NaNs with empty strings.

    Args:
        df (pd.DataFrame): DataFrame to flatten.

    Returns:
        list[str]: Flat list containing all header and cell values.
    """
    df_clean = df.fillna(EMPTY_CELL_REPLACEMENT)
    headers = df_clean.columns.tolist()
    rows = df_clean.to_numpy().flatten().tolist()
    return headers + rows


def has_all_labels_in_a_row(name: str, df: pd.DataFrame, required_labels: list[str]) -> bool:
    """
    Checks whether the DataFrame contains all required labels in any single row.

    This function identifies the best-matching row in the sheet (based on
    overlap with `required_labels`) and returns True only if all labels are
    found in that row.

    Args:
        name (str): The name of the sheet (used for logging or diagnostics).
        df (pd.DataFrame): The sheet data to evaluate.
        required_labels (list[str]): Expected column header labels to look for.

    Returns:
        bool: True if all required labels are found in one row, False otherwise.
    """
    unmatched_labels = find_unmatched_labels_in_best_row(df, required_labels)

    if not unmatched_labels:
        # TODO: logger.info(f"✅ Sheet '{name}' contains all required labels.")
        return True
    else:
        # TODO: logger.debug(f"⚠️ Sheet '{name}' is missing labels: {unmatched_labels}")
        return False
