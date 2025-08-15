"""
Shared runtime resource management utilities.

This module centralizes the core mechanisms for loading, validating, and
caching runtime string resources (e.g., UI messages) from JSON files.
It ensures that resources are well-formed, checksum-verified, and meet
their schema requirements before being stored in a module-specific cache.

Main capabilities:
 - `Cache` class for storing a single named resource mapping (string keys → string values)
 - Loading of JSON-backed runtime resources with integrity and key validation
 - Automatic key export helper for building `__all__` from constants
 - File path resolution to runtime resources within the project tree

Example Usage:
    # Preferred usage via a category module (e.g., _info.py):
    from src.runtime import interfaces as rt
    welcome_msg = rt.info_msg.get(rt.info_key.WELCOME)

    # Direct usage (internal/testing only):
    from src.runtime import _common as common
    cache = common.Cache()
    data_map = common.load_runtime_json("_info", ["WELCOME", "APP_NAME"])
    cache.load_resource("_info", data_map)
    print(cache.get_value("_info", "WELCOME"))

Dependencies:
 - Python >= 3.10
 - Standard Library: typing
 - Internal modules: src.utils.directory, src.utils.file, src.utils.json

Notes:
 - This is an internal utility module for `runtime` category loaders.
 - Designed for lazy-loading: JSON resources are loaded only when first accessed.
 - The `Cache` instance is module-scoped per category (not a global singleton).
 - JSON resources must follow the "foundation" structure with meta/checksum/data sections.

License:
 - Internal Use Only
"""

# Internal utility imports for runtime resource management
import src.utils.directory as dir_util
import src.utils.file as file_util
import src.utils.json as json_util

# CONSTANTS
RUNTIME_FOLDER: tuple[str, ...] = ("src", "runtime",)


class Cache:
    """
    Module-scoped cache for a single runtime resource.

    This cache holds exactly one resource mapping at a time, identified by its logical
    name (`_loaded_resource`). The mapping (`_value_by_key`) contains string keys and
    string values loaded from a validated runtime JSON source.

    Typical usage:
        cache = Cache()
        cache.load_resource("_info", {"WELCOME": "Hello!"})
        if cache.is_loaded("_info"):
            greeting = cache.get_value("_info", "WELCOME")

    Attributes:
        _loaded_resource (str | None): Logical name of the currently loaded resource.
        _value_by_key (dict[str, str]): Mapping of keys to string values for the loaded resource.

    Raises:
        KeyError: If accessing a resource or key when no matching resource is loaded.
        TypeError: If attempting to load data that is not `dict[str, str]`.
    """

    # Holds exactly one resource: its name and key→value mapping
    _loaded_resource: str | None
    _value_by_key: dict[str, str]

    def __init__(self) -> None:
        """
        Initialize an empty runtime resource cache.

        The cache starts with no loaded resource. It can store exactly one
        resource at a time, identified by its logical name and containing
        a mapping of string keys to string values.
        """
        self._loaded_resource: str | None = None  # None if no resource has been loaded.
        self._value_by_key: dict[str, str] = {}  # Empty until `load_resource()` is called.

    def load_resource(self, new_resource_name: str, data_map: dict[str, str]) -> None:
        """
        Load a resource mapping into the cache, replacing any existing resource.

        Validates that `data_map` is a dictionary with strictly string keys and string values.
        This method overwrites any previously loaded resource without warning.

        Args:
            new_resource_name (str): Logical name of the resource category being loaded.
            data_map (dict[str, str]): Mapping of keys to string values for this resource.

        Returns:
            None: The cache is updated in place.

        Raises:
            TypeError: If `data_map` is not a dict with only string keys and values.
        """
        # Ensure provided data is a dict and every key/value is a string
        if not isinstance(data_map, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in data_map.items()):
            raise TypeError("Resource data must be dict[str, str] with string keys and values.")

        # Store the resource name and its mapping in the cache, replacing any previous one
        self._loaded_resource = new_resource_name
        self._value_by_key = data_map

    def get_value(self, expected_resource: str, key: str) -> str:
        """
        Return a value for `key` from the currently loaded `resource_name`.

        Ensures the cache is initialized and that the requested `resource_name`
        matches the one currently loaded. Raises precise errors for empty cache,
        wrong resource, or missing key.

        Args:
            expected_resource (str): Logical name of the resource category expected to be loaded.
            key (str): Key within the loaded resource's mapping to retrieve.

        Returns:
            str: The value associated with `key` in the loaded resource.

        Raises:
            KeyError: If no resource is loaded.
            KeyError: If a different resource is loaded than `resource_name`.
            KeyError: If `key` does not exist in the loaded resource.
        """
        # Ensure the cache has been initialized with a resource
        if self._loaded_resource is None:
            raise KeyError("Resource cache is empty. Call load() before get().")

        # Verify the caller is querying the same resource that is loaded
        if expected_resource != self._loaded_resource:
            raise KeyError(
                f"Requested resource '{expected_resource}' is not loaded. "
                f"Currently loaded: '{self._loaded_resource}'."
            )

        # Attempt lookup
        try:
            return self._value_by_key[key]
        except KeyError as err:
            # Enrich error with available keys for faster debugging
            raise KeyError(
                f"Key '{key}' not found in resource '{expected_resource}'. "
                f"Available keys: {sorted(self._value_by_key.keys())}"
            ) from err

    def is_loaded(self, target_resource: str) -> bool:
        """
        Determine if the specified resource is currently loaded in the cache.

        This method checks whether the cache holds a resource whose logical name matches
        the provided `resource_name`. It returns `True` if the cache contains a loaded
        resource with the same name, otherwise `False`.

        Args:
            target_resource (str): Logical name of the resource category to check.

        Returns:
            bool: True if the cache currently holds a resource matching `resource_name`,
                  False otherwise.
        """
        # Ensure the cache has a resource loaded AND its name matches the one requested
        return self._loaded_resource is not None and self._loaded_resource == target_resource


def _assert_all_values_are_strings(key_value_map: dict[str, str]):
    """
    Validate that all values in the provided dictionary are strings.

    Iterates through each key-value pair in the dictionary and checks that
    the value is of type `str`. If a non-string value is found, a `TypeError`
    is raised specifying the key with the invalid value.

    Args:
        key_value_map (dict[str, str]): Dictionary mapping keys to string values.

    Returns:
        None: This function performs validation and does not return anything.

    Raises:
        TypeError: If any value in the dictionary is not of type `str`.
    """
    # Iterate through each key-value pair in the dictionary
    for key, value in key_value_map.items():
        # Ensure the value is a string; raise an error if not
        if not isinstance(value, str):
            raise TypeError(
                f"Key '{key}' must be a string value, "
                f"but got {type(value).__name__}")


def _assert_required_keys_are_present(key_value_map: dict[str, str], required_keys: list[str]):
    """
    Verify that all required keys are present in the provided dictionary.

    Compares the list of `required_keys` against the keys in `key_value_map` and
    raises a `KeyError` if any required key is missing.

    Args:
        key_value_map (dict[str, str]): Dictionary mapping keys to string values.
        required_keys (list[str]): List of keys that must be present in the dictionary.

    Returns:
        None: This function performs validation and does not return anything.

    Raises:
        KeyError: If `required_keys` is empty.
        KeyError: If one or more required keys are missing from `key_value_map`.
    """
    # Ensure there is at least one required key
    if not required_keys:
        raise KeyError("No required keys specified for validation.")

    # Identify any required keys that are missing from the dictionary
    missing_keys = [key for key in required_keys if key not in key_value_map]

    # If any required keys are missing, raise a KeyError with details
    if missing_keys:
        raise KeyError(f"Missing required keys: {missing_keys}. These keys must be present in the data source.")


def _resolve_json_file_path(resource_name: str, base_dir: str | None = None) -> str:
    """
    Resolve the absolute path to a runtime JSON resource by name.

    Builds the expected "<source>.json" filename, locates the runtime folder,
    lists available JSON files in that folder, and verifies the target file exists.
    Returns the absolute path if found.

    Args:
        resource_name (str): Logical resource name (file stem) of the JSON (e.g., "_info").
        base_dir (str | None): Optional base directory for the runtime folder.
            If None, the application root will be discovered via dir_util.find_root().

    Returns:
        str: Absolute path to the JSON file within the runtime directory.

    Raises:
        FileNotFoundError: If the "<source>.json" file is not present in the runtime directory.
        RuntimeError: If directory discovery or path construction fails.
    """
    # Build the expected filename, e.g., "_info.json"
    target_filename = resource_name + file_util.JSON_FILE_EXT

    # Locate the application root and the runtime directory
    if base_dir is None:
        # Locate the application root and runtime folder
        project_root = dir_util.find_root()
        runtime_dir = dir_util.construct_directory_path(project_root, RUNTIME_FOLDER)
    else:
        # Use the provided base directory (useful for tests)
        runtime_dir = base_dir

    # Enumerate JSON files available in the runtime directory
    available_filenames = file_util.get_files_in_directory(runtime_dir, file_util.JSON_FILE_EXT)

    # Validate presence of the requested resource file
    if target_filename not in available_filenames:
        raise FileNotFoundError(
            f"JSON resource '{resource_name}' not found in '{runtime_dir}'. "
            f"Expected file: '{target_filename}'. "
            f"Found: {sorted(available_filenames)}"
        )

    # Construct and return the absolute file path
    target_path = file_util.build_file_path(runtime_dir, target_filename)

    return target_path


def export_keys(module_globals: dict) -> list[str]:
    """
    Extract all uppercase string constant names from a module's globals.

    This is typically used to auto-generate a module's `__all__` by scanning
    for public key constants (following the convention of all-uppercase names).

    Args:
        module_globals (dict[str, object]): The dictionary returned by `globals()`
            from the calling module.

    Returns:
        list[str]: List of constant names (keys from `module_globals`) that are
        all-uppercase and have string values.
    """
    keys: list[str] = []

    # Iterate through globals as (name, value) pairs
    for name, value in module_globals.items():
        # Only include all-uppercase names (conventional constants)
        if name.isupper():
            # Ensures you only export string keys to avoid exporting REQUIRED_KEYS constant because it is a list.
            if isinstance(value, str):
                keys.append(name)

    return keys


def load_runtime_json(resource_name: str, required_keys: list[str]) -> dict:
    """
    Load a runtime JSON resource, validate integrity and schema, and return its data.

    Resolves the JSON file path for `source`, loads the file, verifies the foundation
    checksum, checks that all `required_keys` are present, and asserts that all values
    are strings. Any failure is wrapped and re-raised as a `RuntimeError` with context.

    Args:
        resource_name (str): Logical resource name (file stem) of the JSON (e.g., "_info").
        required_keys (list[str]): Keys that must exist in the JSON's "data" section.

    Returns:
        dict[str, str]: Validated key–value pairs from the JSON file.

    Raises:
        RuntimeError: If path resolution, file I/O, checksum verification, or schema
            validation fails. The original exception type/message is included.
    """

    try:
        # Resolve the absolute path to "<resource_name>.json" within the runtime folder
        json_path = _resolve_json_file_path(resource_name)

        # Load the foundational JSON object (with meta + data)
        foundation_obj = json_util.load_json_file(json_path)

        # Verify integrity of the "data" block via checksum in meta
        if not json_util.verify_foundation_json_checksum(foundation_obj):
            raise RuntimeError(f"Checksum verification failed for '{resource_name}' JSON data.")

        # Extract the "key:value" mapping (shallow copy)
        key_value_map = json_util.extract_foundation_data(foundation_obj)

        # Ensure the JSON contains all mandatory keys
        _assert_required_keys_are_present(key_value_map, required_keys)

        # Ensure all values are strings (API contract guarantees str values)
        _assert_all_values_are_strings(key_value_map)

    except Exception as err:
        # Wrap with context while preserving the original exception
        raise RuntimeError(
            f"Failed to load runtime JSON for '{resource_name}'.\n"
            f"{type(err).__name__}: {err}"
        ) from err

    return key_value_map
