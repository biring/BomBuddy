"""
Raw data model for the version 3 BOM template.

This module defines structured Python dataclasses that mirror the layout of
version 3 excel based Bill of Materials (BOM) files. It captures metadata,
board-level information, and individual rows exactly as they appear in
the source, with all fields represented as plain strings.

These models serve as the initial parsed representation created by BOM parsers
before any standardization, normalization, or mapping to canonical models.

Main capabilities:
 - Encodes board-level BOM metadata (model number, revision, supplier, cost breakdown)
 - Encodes component-level BOM rows (reference, part number, quantity, price)
 - Supports multiple board BOMs within a single file
 - Provides factory methods (`empty`) for zero-initialized object creation

Example Usage:
    from src.models import Bom
    empty_bom = Bom.empty()

    # Direct module usage (acceptable in unit tests or internal scripts only):
    from src.models._v3_model import Board
    board = Board.empty()

Dependencies:
 - Python >= 3.10
 - Standard Library: dataclasses

Notes:
 - All fields are strings to simplify parsing and tolerate missing values.
 - This model reflects raw BOM data; downstream processing should not modify it.
 - Used primarily by `v3_bom_parser` to convert Excel sheets to structured form.

License:
 - Internal Use Only
"""

from dataclasses import dataclass, field


@dataclass
class Row:
    """
    Represents a single row in the BOM table.

    All fields are strings and default to the empty string ("") to simplify parsing
    and ensure consistent handling of missing or blank values.

    Attributes:
        item (str): Line item number.
        component_type (str): Component type description.
        device_package (str): Package type of the component (e.g., 0402, SOT-23).
        description (str): Part description.
        unit (str): Unit of measure (e.g., pcs).
        classification (str): Part classification (A, B, C).
        manufacturer (str): Manufacturer name.
        mfg_part_number (str): Manufacturer's part number.
        ul_vde_number (str): UL/VDE safety certification number.
        validated_at (str): Build where the part was validated.
        qty (str): Quantity per board.
        designator (str): Component reference designator (e.g., R1, C2).
        unit_price (str): Unit price in RMB (with VAT).
        sub_total (str): Extended cost (qty × unit price), in RMB (with VAT).
    """
    item: str = ""
    component_type: str = ""
    device_package: str = ""
    description: str = ""
    unit: str = ""
    classification: str = ""
    manufacturer: str = ""
    mfg_part_number: str = ""
    ul_vde_number: str = ""
    validated_at: str = ""
    qty: str = ""
    designator: str = ""
    unit_price: str = ""
    sub_total: str = ""


@dataclass
class Header:
    """
    Represents the header of a single board BOM.

    All fields are plain strings with default values of "" to simplify normalization
    and tolerate missing values.

    Attributes:
        model_no (str): Product model number.
        board_name (str): Board name (e.g., MAIN-PCB-A).
        manufacturer (str): Board supplier or manufacturer.
        build_stage (str): Stage of the build (e.g., EB0, MP).
        date (str): BOM creation or release date.
        material_cost (str): Raw material cost.
        overhead_cost (str): Overhead, logistics, or handling cost.
        total_cost (str): Total combined cost.
    """
    model_no: str = ""
    board_name: str = ""
    manufacturer: str = ""
    build_stage: str = ""
    date: str = ""
    material_cost: str = ""
    overhead_cost: str = ""
    total_cost: str = ""


@dataclass
class Board:
    """
    Represents a BOM for a single board, including header and all component rows.

    Attributes:
        header (Header): Board-level metadata including model, stage, and costs.
        rows (list[Row]): List of component rows associated with this board.
    """
    header: Header
    rows: list[Row] = field(default_factory=list)

    @classmethod
    def empty(cls) -> "Board":
        """
        Factory method to create an empty board instance.

        Returns:
            Board: A Board object with default header and an empty component list.
        """
        return cls(header=Header())


@dataclass
class Bom:
    """
    Top-level model representing the structure of a Version 3 BOM file.

    Attributes:
        file_name (str): Original filename of the BOM file.
        boards (list[Board]): List of board BOMs extracted from the file.
    """
    file_name: str = ""
    boards: list[Board] = field(default_factory=list)

    @classmethod
    def empty(cls) -> "Bom":
        """
        Factory method to create an empty Bom instance.

        Returns:
            Bom: An empty Bom object.
        """
        return cls(file_name="", boards=[])