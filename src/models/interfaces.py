"""
Public interface for `models` package.

This module exposes the stable API surface of the `models` package.
It re-exports dataclass models and constants used to represent and parse
BOMs. Internal modules must not be imported directly.

Main capabilities:
 - Exposes Board, Bom, Header, and Row dataclasses
 - Exposes field mappings and template identifiers
 - Hides internal implementation from external consumers

Example Usage:
    from src.models.interface import *
    board = Board.empty()

Dependencies:
 - Python >= 3.10

Notes:
 - Only symbols listed in `__all__` are exposed via `src.models`.
 - Designed to maintain a clean, testable, and stable external API.

License:
 - Internal Use Only
"""

from src.models._v3_fields import (
    BoardHeaderFields,
    BoardTableFields,
    TABLE_LABEL_TO_ATTR_MAP,
    BOARD_HEADER_TO_ATTR_MAP,
    REQUIRED_V3_BOARD_TABLE_IDENTIFIERS,
    REQUIRED_V3_BOM_IDENTIFIERS
)
from src.models._v3_raw import (
    Board,
    Bom,
    Header,
    Row
)

__all__ = [
    'BoardHeaderFields',
    'BoardTableFields',
    'TABLE_LABEL_TO_ATTR_MAP',
    'BOARD_HEADER_TO_ATTR_MAP',
    'REQUIRED_V3_BOARD_TABLE_IDENTIFIERS',
    'REQUIRED_V3_BOM_IDENTIFIERS',
    'Board',
    'Bom',
    'Header',
    'Row'
]
