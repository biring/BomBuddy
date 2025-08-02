"""
Parser for Version 3 Bill of Materials (BOM) Excel sheets.

This module identifies and parses Excel workbooks that follow the Version 3 BOM template.
It extracts board-level metadata and BOM table from sheets that match expected
structure and headers.

Main capabilities:
 - Detects whether an Excel workbook uses the v3 BOM format (`is_v3_bom`)
 - Extracts and parses board-level BOM data (`parse_v3_bom`)
 - Converts sheet content into structured `Board`, `Header`, and `Item` models
 - Handles malformed or non-matching sheets gracefully

Example Usage:
    # Usage via public package interface:
    Not allowed. This is an internal module. interface.py lists public package interfaces

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.parsers._v3_bom_parser import is_v3_bom, parse_v3_bom
    if is_v3_bom(sheets):
        bom = parse_v3_bom(sheets)

Dependencies:
 - Python >= 3.10
 - pandas
 - src.models.interfaces: Bom, Board, Header, Item
 - src.parsers._common: utility functions for flattening, extraction, and normalization

Notes:
 - Assumes a workbook may contain multiple sheets, only some of which are board BOMs.
 - Uses label-to-field mapping for robust extraction across inconsistent formatting.
 - Raises ValueError if no valid board sheets are parsed, to prevent silent failure.
 - Designed for incremental extension (e.g., summary sheet parsing).

License:
 - Internal Use Only
"""

import pandas as pd
import src.parsers._common as common

from src.models.interfaces import *


def _is_v3_board_sheet(name: str, sheet: pd.DataFrame) -> bool:
    """
    Checks whether a sheet contains required identifiers for a Version 3 board BOM.

    Evaluates whether the sheet includes all required board-level identifiers to qualify
    as a Version 3 BOM. This is used to selectively parse valid board sheets.

    Args:
        name (str): Name of the sheet (for logging/diagnostic purposes).
        sheet (pd.DataFrame): The DataFrame representing the Excel sheet.

    Returns:
        bool: True if all required identifiers are found, False otherwise.
    """
    # Check for all required identifiers in a single row to qualify as a Version 3 board BOM
    if common.has_all_identifiers_in_single_row(name, sheet, REQUIRED_V3_BOARD_TABLE_IDENTIFIERS):
        # TODO: logger.info(f"✅ Sheet '{name}' is version 3 board BOM.")
        # when match found, exit
        return True
    else:
        # TODO: logger.debug(f"⚠️ Sheet '{name}' is not version 3 board BOM.")
        # If not ignore the sheet
        pass

    return False


def _parse_board_sheet(sheet: pd.DataFrame) -> Board:
    """
    Parses a board BOM sheet into a structured Board object.

    Separates the sheet into header and component sections and converts both into
    structured dataclass instances.

    Args:
        sheet (pd.DataFrame): The board BOM sheet to be parsed.

    Returns:
        Board: A structured Board object containing parsed header and component items.
    """
    # Initialize an empty Board object
    board: Board = Board.empty()

    # Extract board-level metadata block from the top of the sheet
    header_block = common.extract_header_block(sheet, REQUIRED_V3_BOARD_TABLE_IDENTIFIERS)
    # Parse and assign header metadata
    board.header = _parse_board_header(header_block)

    # Extract the BOM component table from the lower part of the sheet
    table_block = common.extract_table_block(sheet, REQUIRED_V3_BOARD_TABLE_IDENTIFIERS)
    # Parse and assign the BOM items
    board.items = _parse_board_table(table_block)

    return board


def _parse_board_header(sheet_header: pd.DataFrame) -> Header:
    """
    Parses the board-level metadata block into a Header object.

    Flattens the input sheet block and maps known labels to the `Header` dataclass fields.

    Args:
        sheet_header (pd.DataFrame): Metadata section of the sheet.

    Returns:
        Header: A populated Header object with string values.
    """
    field_map = {}

    # Flatten the metadata block into a list of strings
    header_as_list = common.flatten_dataframe(sheet_header)

    # Map known Excel labels to Header dataclass fields using label-to-field mapping
    for excel_label, model_field in BOARD_HEADER_TO_ATTR_MAP.items():
        field_map[model_field] = common.extract_value_after_identifier(header_as_list, excel_label)

    return Header(**field_map)


def _parse_board_table(sheet_table: pd.DataFrame) -> list[Item]:
    """
    Parses the component table into a list of Item instances.

    Iterates through each row and converts it to a structured Item object.

    Args:
        sheet_table (pd.DataFrame): The component table section of the BOM.

    Returns:
        list[Item]: Parsed list of BOM component items.
    """
    items: list[Item] = []

    for _, row in sheet_table.iterrows():
        # Convert each row of the table into an Item object
        item = _parse_board_table_row(row)
        # Append parsed Item to the result list
        items.append(item)

    return items


def _parse_board_table_row(row: pd.Series) -> Item:
    """
    Parses a single component row into an Item instance.

    Uses fuzzy label matching to extract values and maps them to the Item dataclass fields.

    Args:
        row (pd.Series): One row of the BOM table.

    Returns:
        Item: The parsed BOM component with mapped field values.
    """
    item_fields = {}

    for excel_label, model_field in TABLE_LABEL_TO_ATTR_MAP.items():
        # Extract each field using fuzzy matching against the row headers
        item_fields[model_field] = common.extract_cell_value_by_fuzzy_header(row, excel_label)

    return Item(**item_fields)


def is_v3_bom(sheets: list[tuple[str, pd.DataFrame]]) -> bool:
    """
    Checks if any sheet in the workbook uses the Version 3 BOM format.

    Scans all provided sheets for required identifiers to detect a v3 BOM template.

    Args:
        sheets (list[tuple[str, pd.DataFrame]]): List of (sheet name, DataFrame) tuples.

    Returns:
        bool: True if any sheet matches the v3 BOM structure, False otherwise.
    """
    # Iterate through all sheets and check for required identifiers
    for name, sheet in sheets:
        # If it contains the labels that identify it as version 3 template
        if common.has_all_identifiers_in_single_row(name, sheet, REQUIRED_V3_BOM_IDENTIFIERS):
            # TODO: logger.info(f"✅ Sheet '{name}' is using version 3 BOM template.")
            # TODO: logger.info(f"✅ BOM is using version 3 template.")
            # Return True on first match
            return True
        else:
            # TODO: logger.debug(f"⚠️ Sheet '{name}' is not using version 3 BOM Template.")
            # Skip non-matching sheets
            pass

    # TODO: logger.debug(f"⚠️ BOM is not using version 3 template.")
    return False


def parse_v3_bom(sheets: list[tuple[str, pd.DataFrame]]) -> Bom:
    """
    Parses Version 3 BOM sheets into a structured Bom object.

    Iterates through all sheets, identifies valid board BOMs, and converts them into
    structured Board instances. Raises an exception if none are valid.

    Args:
        sheets (list[tuple[str, pd.DataFrame]]): List of (sheet name, DataFrame) tuples.

    Returns:
        Bom: Parsed BOM with one or more structured boards.

    Raises:
        ValueError: If no valid board sheets are found.
    """
    # Initialize an empty BOM object
    bom = Bom.empty()

    # Loop through each sheet
    for name, sheet in sheets:
        # Check if sheet is a valid board BOM
        if _is_v3_board_sheet(name, sheet):
            # Parse and append valid boards to the BOM
            bom.boards.append(_parse_board_sheet(sheet))
            # TODO: logger.info(f"✅ Sheet '{name}' was parsed..")
        else:
            # TODO: logger.debug(f"⚠️ Sheet '{name}' was not parsed.")
            # If not ignore the sheet
            pass

    # Raise an error if the BOM remains empty after parsing
    if bom == Bom.empty():
        raise ValueError("Parsed version 3 bom is empty.")

    return bom
