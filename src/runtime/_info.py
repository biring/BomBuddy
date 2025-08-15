"""
Category accessor for the 'info' runtime resource.

This module provides a thin, lazy-initialized API to read user-facing
“info” messages (e.g., prompts, labels) from the `_info.json` foundation.
It validates the JSON (checksum + required keys) and exposes a simple
`get(key)` call for consumers. A small, module-local `Cache` ensures we
load only once per process.

Main capabilities:
 - Lazy initialization of the 'info' resource via `load()`
 - Public read accessor `get(key: str) -> str`
 - Enforced validation against `info_key.REQUIRED_KEYS`
 - Clear error messages for missing keys / wrong resource / bad JSON

Example Usage:
    # Preferred usage via public package interface:
    from src.runtime import interfaces as rt
    title = rt.info_msg.get(rt.info_key.APP_NAME)

    # Direct module usage (internal/tests only):
    from src.runtime import _info as info
    info.load()
    welcome = info.get("WELCOME")

Dependencies:
 - Python >= 3.10
 - Internal: src.runtime._common (Cache, load_runtime_json)
 - Internal: src.runtime._info_keys (REQUIRED_KEYS defined from constants)
 - Transitive utils used by _common: src.utils.directory, src.utils.file, src.utils.json

Notes:
 - The `SOURCE` name must match the JSON stem (“_info” → “_info.json”).
 - All values in the JSON `data` section must be strings.
 - This module is intentionally small; business logic lives in `_common`.
 - Intended to be imported indirectly via `src.runtime.interfaces` to preserve
   a stable, public surface while keeping per-category modules private.

License:
 - Internal Use Only
"""

from typing import Final

from . import _info_keys as info_key
from . import _common as common

# MODULE CONSTANTS
SOURCE: Final[str] = "_info"  # Must match file name exactly without extension

# MODULE VARIABLES
cache: common.Cache = common.Cache()  # Singleton cache for this module only


def load() -> None:
    """
    Load the 'info' category runtime resource into the cache if not already loaded.

    Checks if the '_info' resource is present in the cache; if not, loads it from
    the corresponding JSON file, validates that all required keys are present,
    and stores it in the cache for future access.

    This is a lazy initializer: repeated calls will not reload the resource unless
    the cache is cleared or replaced.

    Returns:
        None: Modifies the module's cache in place.

    Raises:
        RuntimeError: If the JSON file cannot be loaded, fails checksum validation,
                      or is missing required keys.
        TypeError: If the loaded data is not `dict[str, str]`.
    """
    # Skip loading if the resource is already in the cache
    if cache.is_loaded(SOURCE):
        return

    # Load and validate the JSON resource for this category
    key_value_map = common.load_runtime_json(SOURCE, info_key.REQUIRED_KEYS)

    # Store the validated mapping in the runtime cache
    cache.load_resource(SOURCE, key_value_map)


def get(key: str) -> str:
    """
    Return the string value for a key from the 'info' runtime resource.

    Lazily ensures the '_info' resource is loaded into the module cache, then
    retrieves the value for the requested key. Use this as the public accessor
    (e.g., `info.get("WELCOME")`) instead of touching the cache directly.

    Args:
        key (str): Resource key to retrieve from the 'info' mapping.

    Returns:
        str: The string value associated with the provided key.

    Raises:
        KeyError: If the key does not exist in the loaded 'info' resource.
        RuntimeError: If loading/validation of the 'info' resource fails.
        TypeError: If `key` is not a `str`.
    """
    # Validate argument type early for clearer errors
    if not isinstance(key, str):
        raise TypeError(f"'key' must be str, got {type(key).__name__}.")

    # Lazily load the resource if not already present
    if not cache.is_loaded(SOURCE):
        load()

    # Attempt lookup and rethrow with context on failure
    try:
        return cache.get_value(SOURCE, key)
    except KeyError as err:
        raise KeyError(
            f"Key '{key}' not found in resource '{SOURCE}'."
        ) from err
