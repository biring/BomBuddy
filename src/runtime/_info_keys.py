"""
Public key constants for the 'info' runtime resource category.

This module defines all symbolic key names expected to exist in the
corresponding `_info.json` runtime resource. Each key is a string constant
that maps to a value in the resource’s JSON "data" section. All keys are
treated as required — they must exist at load time or validation will fail.

Main capabilities:
 - Define human-readable constants instead of hardcoded string keys
 - Auto-generate `__all__` by scanning uppercase string constants
 - Maintain `REQUIRED_KEYS` list for JSON schema validation

Example Usage:
    # Preferred usage via the public interface
    from src.runtime import interfaces as rt
    app_name = rt.info_msg.get(rt.info_key.APP_NAME)

    # Direct usage (internal/testing only)
    import src.runtime._info_keys as info_key
    print(info_key.SAMPLE_STRING)

Dependencies:
 - Python >= 3.10
 - Internal: src.runtime._common.export_keys

Notes:
 - `__all__` is generated automatically; no manual edits required.
 - Keep constants in uppercase to be detected by `export_keys()`.
 - Intended for internal use within the `runtime` package, but exposed via
   `interfaces.py` for safe external access.

License:
 - Internal Use Only
"""

from ._common import export_keys

# Public key constants
SAMPLE_STRING = "Sample String"

# Auto-generate __all__ from all uppercase string constants in this module.
__all__ = export_keys(globals())

# Required keys for validation — all keys defined in this module are required.
REQUIRED_KEYS: list[str] = __all__.copy()
