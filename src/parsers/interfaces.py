"""
Public interface for the `parsers` package.

This module defines the stable external interface for BOM parsing functionality,
currently exposing only Version 3 parsing functions. It re-exports public APIs
from internal implementations (e.g., `_v3_bom_parser`) while maintaining a clean
boundary for external consumers.

Main capabilities:
 - Exposes `is_v3_bom` for BOM format detection
 - Exposes `parse_v3_bom` to convert Excel sheets into structured BOM models
 - Serves as the single import point for all BOM parser functionality

Example Usage:
    from src.parsers.interface import *
    if is_v3_bom(sheets):
        bom = parse_v3_bom(sheets)

Dependencies:
 - Python >= 3.10

Notes:
 - This is the only module that should be imported from outside the `parsers` package.
 - All internal modules are subject to change and must not be relied upon externally.
 - Designed to support versioned parsing logic behind a stable API.

License:
 - Internal Use Only
"""

from src.parsers._v3_bom_parser import (
    is_v3_bom,
    parse_v3_bom
)

__all__ = [
    'is_v3_bom',
    'parse_v3_bom'
]
