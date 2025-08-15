"""
Package initializer for `runtime`.

The `runtime` package manages user-facing string resources (e.g., prompts,
messages, labels) stored in JSON "foundation" files with metadata and
checksums. Each resource category (e.g., `_info`, `_error`) is implemented
in its own private module with:
 - A loader/accessor API (`load()` and `get()`)
 - A companion constants module (`*_keys.py`) listing required keys

By default, this package exposes only the `interfaces` module for stable,
public access to all categories.

Main capabilities:
 - Encapsulate category-specific resource logic in private modules
 - Centralize public access to all categories via `interfaces.py`
 - Support lazy loading with schema + checksum validation

Example Usage:
    from src.runtime import interfaces as rt
    app_name = rt.info_msg.get(rt.info_key.APP_NAME)

Dependencies:
 - Python >= 3.10
 - Internal: Category modules (`_info.py`, `_error.py`, etc.) and their constants
 - Internal: src.runtime._common for core cache/load utilities

Notes:
 - Direct imports of private category modules are discouraged; use `interfaces`.
 - All categories must follow the `<name>_msg` and `<name>_key` naming pattern
   when exposed in `interfaces.py`.

License:
 - Internal Use Only
"""

__all__: list[str] = ["interfaces"]
