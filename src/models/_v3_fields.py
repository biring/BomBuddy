"""
Internal constants and field mappings for version 3 BOM model support.

This module defines string constants and mapping dictionaries used to translate
raw Excel headers into structured model attributes (Header, Row). It enables
automated parsing workflows within the Version 3 BOM parser.

Main capabilities:
 - Definitions for board-level and component-level Excel fields
 - Mappings from Excel labels to internal model attribute names
 - Identifiers used to detect Version 3 BOM templates

Example Usage:
    # Internal module usage (within `models` or parsing logic):
    from src.models import _v3_field_constants as v3
    field = v3.BoardHeaderFields.BOM_DATE

    # Unit test usage (allowed and expected for testing internals):
    from src.models._v3_field_constants import TABLE_FIELD_MAP

Dependencies:
 - Python >= 3.10
 - Standard Library only

Notes:
 - This module is internal to `src.models`. It is not part of the public API.
 - External code should import public interfaces via `src.models.interface`.
 - Use in unit tests is acceptable to validate parsing logic and constants.

License:
 - Internal Use Only
"""


class BoardHeaderFields:
    """
    Field constants for board-level metadata in Version 3 BOM sheets.

    Each class attribute corresponds to a known header label in the Excel sheet,
    used to extract metadata like model number, revision, supplier, and costs.

    These fields map to internal dataclass attributes via `HEADER_FIELD_MAP`.

    Class Methods:
        names(): Returns a list of all defined header field strings.
    """
    MODEL_NUMBER = "Model No:"  # Product model identifier
    BUILD_STAGE = "Rev:"  # Build stage or revision (e.g., EB0, MP)
    BOARD_NAME = "Description:"  # Board or BOM description
    BOARD_SUPPLIER = "Manufacturer:"  # Board supplier or manufacturer name
    BOM_DATE = "Date:"  # BOM creation or approval date
    MATERIAL_COST = "Material"  # Material cost subtotal
    OVERHEAD_COST = "OHP"  # Overhead or handling cost
    TOTAL_COST = "Total"  # Total cost (material + overhead)

    @classmethod
    def names(cls) -> list[str]:
        """
        Returns all board header field strings defined in the class.

        Returns:
            list[str]: List of board metadata field labels used in Excel.
        """
        return [
            value for name, value in vars(cls).items()
            if not name.startswith("__") and isinstance(value, str)
        ]


"""
Mapping of board-level Excel header fields to Header dataclass attributes.

This dictionary translates raw Excel labels from the Version 3 BOM template 
(as defined in `BoardHeaderFields`) into corresponding attribute names 
of the internal `Header` dataclass. It enables consistent field matching 
during BOM parsing and model population.

Key:
    str: Excel label for a board-level metadata field (e.g., "Model No:")
Value:
    str: Attribute name in the `Header` dataclass (e.g., "model_no")
"""
BOARD_HEADER_TO_ATTR_MAP = {
    BoardHeaderFields.MODEL_NUMBER: "model_no",
    BoardHeaderFields.BUILD_STAGE: "build_stage",
    BoardHeaderFields.BOARD_NAME: "board_name",
    BoardHeaderFields.BOARD_SUPPLIER: "manufacturer",
    BoardHeaderFields.BOM_DATE: "date",
    BoardHeaderFields.MATERIAL_COST: "material_cost",
    BoardHeaderFields.OVERHEAD_COST: "overhead_cost",
    BoardHeaderFields.TOTAL_COST: "total_cost"
}


class BoardTableFields:
    """
    Field constants for component table columns in Version 3 BOM sheets.

    Each class attribute represents a standardized column header in the board's
    component table, such as part number, quantity, or pricing information.

    These fields map to internal dataclass attributes via `TABLE_FIELD_MAP`.

    Class Methods:
        names(): Returns a list of all defined table field strings.
    """

    ITEM = "Item"  # Line number in the BOM
    COMPONENT = "Component"  # Component name or ID
    PACKAGE = "Device Package"  # Physical package type (e.g., QFN-8)
    DESCRIPTION = "Description"  # Part description
    UNITS = "Unit"  # Unit of measure (e.g., pcs)
    CLASSIFICATION = "Classification"  # Component class (e.g., A, B, C)
    MANUFACTURER = "Manufacturer"  # Part manufacturer
    MFG_PART_NO = "Manufacturer P/N"  # Manufacturer part number
    UL_VDE_NUMBER = "UL/VDE Number"  # Certification reference (if applicable)
    VALIDATED_AT = "Validated at"  # Validation build stage
    QTY = "Qty"  # Quantity used
    DESIGNATOR = "Designator"  # Reference designators (e.g., R1, C4)
    UNIT_PRICE = "U/P (RMB W/ VAT)"  # Unit price (incl. VAT) in RMB
    SUB_TOTAL = "Sub-Total (RMB W/ VAT)"  # Line subtotal cost

    @classmethod
    def names(cls) -> list[str]:
        """
        Returns all component table field strings defined in the class.

        Returns:
            list[str]: List of component table column labels used in Excel.
        """
        return [
            value for name, value in vars(cls).items()
            if not name.startswith("__") and isinstance(value, str)
        ]


"""
Mapping of component table column labels to Row dataclass attributes.

This dictionary translates raw Excel column headers from the Version 3 BOM template 
(as defined in `BoardTableFields`) into corresponding attribute names 
of the internal `Row` dataclass. It enables automated parsing of component-level 
data into structured models during BOM ingestion.

Key:
    str: Excel label for a component table column (e.g., "Qty")
Value:
    str: Attribute name in the `Row` dataclass (e.g., "qty")
"""
TABLE_LABEL_TO_ATTR_MAP = {
    BoardTableFields.ITEM: "item",
    BoardTableFields.COMPONENT: "component_type",
    BoardTableFields.PACKAGE: "device_package",
    BoardTableFields.DESCRIPTION: "description",
    BoardTableFields.UNITS: "unit",
    BoardTableFields.CLASSIFICATION: "classification",
    BoardTableFields.MANUFACTURER: "manufacturer",
    BoardTableFields.MFG_PART_NO: "mfg_part_number",
    BoardTableFields.UL_VDE_NUMBER: "ul_vde_number",
    BoardTableFields.VALIDATED_AT: "validated_at",
    BoardTableFields.QTY: "qty",
    BoardTableFields.DESIGNATOR: "designator",
    BoardTableFields.UNIT_PRICE: "unit_price",
    BoardTableFields.SUB_TOTAL: "sub_total"
}

"""
Required column labels used to detect Version 3 BOM templates.

This list defines the minimum set of Excel column headers that must be present 
in a sheet for it to be recognized as conforming to the Version 3 BOM format. 
These fields are typically found in the component table section of the sheet.

Returns:
    list[str]: List of field labels used to validate a Version 3 BOM sheet.
"""
REQUIRED_V3_BOM_IDENTIFIERS: list[str] = [
    BoardTableFields.CLASSIFICATION,
    BoardTableFields.DESIGNATOR,
    BoardTableFields.MANUFACTURER,
    BoardTableFields.MFG_PART_NO
]

"""
Required column labels used to identify Version 3 BOM board tables.

This list contains key Excel column headers that must be present in a sheet's 
component table for it to be recognized as following the Version 3 BOM board template. 
These fields help ensure structural compatibility before parsing.

Returns:
    list[str]: Column labels expected in a valid Version 3 board-level BOM table.
"""
REQUIRED_V3_BOARD_TABLE_IDENTIFIERS: list[str] = [
    BoardTableFields.CLASSIFICATION,
    BoardTableFields.DESIGNATOR,
    BoardTableFields.MANUFACTURER,
    BoardTableFields.MFG_PART_NO
]
