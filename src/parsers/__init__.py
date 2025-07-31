"""
Package initializer for the `parsers` package.

This module exposes the stable, version-agnostic interface to all BOM parsing
capabilities via the `interfaces` module. Internal parser implementations
(e.g., `_v3_bom_parser`) are intentionally hidden to enforce API boundaries
and allow safe refactoring and evolution of internal logic.

Main capabilities:
 - Provides access to public BOM parsing functions (e.g., `is_v3_bom`, `parse_v3_bom`)
 - Hides internal implementation details and module structure
 - Supports safe import patterns for application-level or unit test use

Example Usage:
    from src.parsers import *
    if is_v3_bom(sheets):
        bom = parse_v3_bom(sheets)

Dependencies:
 - Python >= 3.10
 - Standard Library only

Notes:
 - Only the `interface` module is exposed via `__all__`, to enforce a stable external API.
 - Internal modules (prefixed with `_`) must not be imported directly.
 - Designed to support BOM parsing version control and future extensibility.

License:
 - Internal Use Only
"""

__all__ = ["interfaces"]
