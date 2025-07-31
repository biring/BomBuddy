"""
Package initializer for the `models` component.

This package defines structured dataclass models and constants to represent
version 3 excel based Bill of Materials (BOM). It provides a stable public API
via the `interface` module and encapsulates all internal logic in private modules.

Main capabilities:
 - Exposes `interface` as the only public entry point
 - Encapsulates raw model definitions and parsing constants
 - Ensures clean separation between internal and external usage

Example Usage:
    from src.models.interface import *
    bom = Bom.empty()

Dependencies:
 - Python >= 3.10

Notes:
 - Only `interface` is exposed via `__all__`.
 - Internal modules (`_v3_raw`, `_v3_fields`) must not be imported directly.
 - Maintains modular boundaries to support future versioned model definitions.

License:
 - Internal Use Only
"""

__all__ = ["interfaces"]
