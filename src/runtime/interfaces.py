"""
Public bindings for runtime resource categories.

This module acts as the stable, public-facing interface to all runtime
resource categories. Each category is exposed with:
 - A module alias providing its public API (`get()` and `load()` functions)
 - A companion module containing its key constants and REQUIRED_KEYS list

This indirection allows category modules (e.g., `_info.py`) to remain
internal while exposing them under predictable, stable names. This
supports easier refactoring and external usage without breaking imports.

Main capabilities:
 - Provide a single import point for all runtime categories
 - Keep category implementations private while exposing their APIs
 - Group each category’s accessors and keys in one place

Example Usage:
    from src.runtime import interfaces as rt
    # Access a string resource by key constant
    greeting = rt.info_msg.get(rt.info_key.WELCOME)

Dependencies:
 - Python >= 3.10
 - Internal: Each category module and its corresponding *_keys module

Notes:
 - Categories should follow the naming convention:
       <category>_msg → category loader/accessor module
       <category>_key → category constants module
 - All public imports for runtime categories should be added here.
 - Designed for use by higher-level code, not for category implementation.

License:
 - Internal Use Only
"""

from . import _info as info_msg
from . import _info_keys as info_key

__all__ = [
    'info_msg',
    'info_key'
]
