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
 > from src.parsers.v3_bom_parser import is_v3_bom, parse_v3_bom
 > if is_v3_bom(sheets):
 >     bom = parse_v3_bom(sheets)

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


def _is_v3_board(name: str, sheet: pd.DataFrame) -> bool:
    """
    Checks whether a sheet contains required identifiers for a Version 3 board BOM.

    Evaluates whether the sheet includes all expected identifiers for a board BOM.
    Used to selectively parse valid sheets.

    Args:
        name (str): The name of the sheet (used for logging or diagnostics).
        sheet (pd.DataFrame): A DataFrame representing the sheet's content.

    Returns:
        bool: True if the sheet contains all required board-level identifiers, False otherwise.
    """
    # If it contains the labels that identify it as version 3 template
    if common.has_all_labels_in_a_row(name, sheet, REQUIRED_V3_BOARD_TABLE_IDENTIFIERS):
        # TODO: logger.info(f"✅ Sheet '{name}' is version 3 board BOM.")
        # when match found, exit
        return True
    else:
        # TODO: logger.debug(f"⚠️ Sheet '{name}' is not version 3 board BOM.")
        # If not ignore the sheet
        pass

    return False


def _parse_board(sheet: pd.DataFrame) -> Board:
    """
    Parses a board BOM sheet into a structured Board object.

    Separates the sheet into header and table sections, and processes each
    into structured dataclass instances.

    Args:
        sheet (pd.DataFrame): The DataFrame representing a board BOM sheet.

    Returns:
        Board: A structured Board object with parsed header and items.
    """
    # Start with an empty board
    board: Board = Board.empty()

    # Extract the board header
    sheet_header = common.extract_header(sheet, REQUIRED_V3_BOARD_TABLE_IDENTIFIERS)
    board.header = _parse_board_header(sheet_header)

    # Extract the board table
    sheet_table = common.extract_table(sheet, REQUIRED_V3_BOARD_TABLE_IDENTIFIERS)
    board.items = _parse_board_table(sheet_table)

    return board


def _parse_board_header(sheet_header: pd.DataFrame) -> Header:
    """
    Parses the board-level metadata section of a BOM into a Header instance.

    Flattens the top portion of the sheet and maps known labels to field names
    defined in the Header dataclass.

    Args:
        sheet_header (pd.DataFrame): The top portion of the sheet containing metadata.

    Returns:
        Header: A populated Header object with string fields ("" if values are missing).
    """
    header_data = {}
    # Flatten the metadata section into a list
    header_as_list = common.flatten_dataframe(sheet_header)

    for excel_label, model_field in BOARD_HEADER_TO_ATTR_MAP.items():
        header_data[model_field] = common.extract_label_value(header_as_list, excel_label)

    return Header(**header_data)


def _parse_board_table(sheet_table: pd.DataFrame) -> list[Item]:
    """
    Parses the BOM component table into a list of Item instances.

    Processes each row in the table section of the sheet and converts it
    into a structured Item object using label mappings.

    Args:
        sheet_table (pd.DataFrame): The table section of the BOM sheet.

    Returns:
        list[Item]: A list of parsed Item instances representing BOM components.
    """
    table: list[Item] = []

    for _, row in sheet_table.iterrows():
        item = _parse_board_table_row(row)
        table.append(item)

    return table


def _parse_board_table_row(row: pd.Series) -> Item:
    """
    Parses a single row from the BOM component table into an Item instance.

    Handles messy or inconsistent input by normalizing headers before mapping
    values to fields in the Item dataclass.

    Args:
        row (pd.Series): A single row from the BOM component table.

    Returns:
        Item: A structured Item object with extracted and normalized field values.
    """
    item_data = {}

    for excel_label, model_field in TABLE_LABEL_TO_ATTR_MAP.items():
        item_data[model_field] = common.extract_row_cell(row, excel_label)

    return Item(**item_data)


def is_v3_bom(sheets: list[tuple[str, pd.DataFrame]]) -> bool:
    """
    Checks whether any sheet in the workbook uses the Version 3 BOM template.

    Scans each sheet for required identifying labels to determine if the workbook conforms
    to the expected v3 BOM format. Returns True as soon as a match is found.

    Args:
        sheets (list[tuple[str, pd.DataFrame]]): A list of (sheet name, DataFrame) tuples representing Excel sheets.

    Returns:
        bool: True if any sheet contains all required v3 template labels, False otherwise.
    """
    # Check each sheet in the dataframe
    for name, sheet in sheets:
        # If it contains the labels that identify it as version 3 template
        if common.has_all_labels_in_a_row(name, sheet, REQUIRED_V3_BOM_IDENTIFIERS):
            # TODO: logger.info(f"✅ Sheet '{name}' is using version 3 BOM template.")
            # TODO: logger.info(f"✅ BOM is using version 3 template.")
            return True  # when match found, exit
        else:
            # TODO: logger.debug(f"⚠️ Sheet '{name}' is not using version 3 BOM Template.")
            # If not ignore the sheet
            pass

    # TODO: logger.debug(f"⚠️ BOM is not using version 3 template.")
    return False


def parse_v3_bom(sheets: list[tuple[str, pd.DataFrame]]) -> Bom:
    """
    Parses a list of Excel sheets into a Bom object for the Version 3 BOM template.

    Identifies board-level BOM sheets, extracts their metadata and table data, and
    converts them into structured Board instances. Raises an exception if no valid
    boards are found.

    Args:
        sheets (list[tuple[str, pd.DataFrame]]): A list of (sheet name, DataFrame) tuples representing Excel sheets.

    Returns:
        Bom: A structured Bom object populated with parsed board data.

    Raises:
        ValueError: If no valid board sheets are found and the resulting Bom is empty.
    """
    # Start with an empty bom
    bom = Bom.empty()

    # Parse each sheet in the bom one at a time
    for name, sheet in sheets:
        # If the sheet is the board sheet
        if _is_v3_board(name, sheet):
            # Parse and add it to the bom
            bom.boards.append(_parse_board(sheet))
            # TODO: logger.info(f"✅ Sheet '{name}' was parsed..")
        else:
            # TODO: logger.debug(f"⚠️ Sheet '{name}' was not parsed.")
            # If not ignore the sheet
            pass

    if bom == Bom.empty():
        raise ValueError("Parsed version 3 bom is empty.")

    return bom
