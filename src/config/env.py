"""
Environment detection for application runtime mode.

This module centralizes logic for determining how the application is being
executed. It distinguishes between development, testing, and packaged
executable contexts, and exposes a module-level constant (`APP_MODE`)
for global reference.

Main capabilities:
 - Detect if the app is running as a frozen executable (PyInstaller, cx_Freeze)
 - Detect if the app is running under unittest or pytest
 - Detect if the app is running directly from source (development mode)
 - Provide a stable `AppMode` enum and `APP_MODE` constant for configuration

Example Usage:
    # Preferred usage via package interface
    from src.runtime.env import APP_MODE, AppMode
    if APP_MODE is AppMode.EXECUTABLE:
        print("Running as packaged binary")

    # Direct module usage (acceptable in tests or internal scripts only)
    import src.runtime.env as env
    print(env.APP_MODE)

Dependencies:
 - Python >= 3.9
 - Standard Library: os, sys, enum, typing

Notes:
    - Evaluation of `APP_MODE` occurs at module import time and is immutable
        thereafter.
    - Priority order of detection:
         1. Executable (frozen binary)
         2. Unit test (unittest/pytest)
         3. Development (default fallback)
    - This module is intended for use throughout the runtime/configuration layer
        to adjust behavior based on execution context.

License:
 - Internal Use Only
"""

import os
import sys

from enum import Enum, auto
from typing import Final

# Public API
__all__ = ["AppMode", "APP_MODE"]  # Restricts exports to enum and constant only


class AppMode(Enum):
    """
    Enumeration of application runtime modes.

    This enum distinguishes between different contexts in which the application
    may be running:
      - DEVELOPMENT: Normal execution from source code during development.
      - UNITTEST: Execution within a unittest/pytest testing environment.
      - EXECUTABLE: Execution as a frozen binary (e.g., PyInstaller, cx_Freeze).
    """
    DEVELOPMENT = auto()
    UNITTEST = auto()
    EXECUTABLE = auto()


def _is_running_as_executable() -> bool:
    """
    Determine if the application is running as a frozen executable.

    Frozen mode occurs when the application is packaged with tools like
    PyInstaller or cx_Freeze. In this mode, `sys.frozen` is set by the packager.

    Returns:
        bool: True if running as a frozen executable, False if running from source.
    """
    # PyInstaller and cx_Freeze inject this attribute at runtime
    return getattr(sys, "frozen", False)


def _is_running_a_unittest() -> bool:
    """
    Determine if the application is running under the unittest framework.

    This checks whether the 'unittest' module is present in sys.modules,
    which only occurs when tests are being executed via unittest (e.g.
    `python -m unittest`, `pytest` running unittest tests, or direct runner).

    Returns:
        bool: True if running inside unittest, False otherwise.
    System properties used:
      - 'unittest' and its submodules present in sys.modules during active runs
      - 'PYTEST_CURRENT_TEST' environment variable when pytest orchestrates the run
    """
    # pytest orchestrating unittest-based tests
    if "PYTEST_CURRENT_TEST" in os.environ:
        return True

    # unittest runner typically loads these submodules when executing tests
    if "unittest" in sys.modules:
        if any(m.startswith("unittest.") for m in sys.modules.keys()):
            return True

    return False


def _is_running_from_source() -> bool:
    """
    Check if the app is running directly from source code.

    Returns:
        bool: True if running from a source checkout, False otherwise.
    """
    return hasattr(sys, "frozen") is False


def _determine_app_mode() -> AppMode:
    """
    Determine the current application runtime mode.

    The function detects the runtime context in priority order:
    1) EXECUTABLE — when the app is packaged as a frozen binary (e.g., PyInstaller).
    2) UNITTEST   — when running under unittest/pytest.
    3) DEVELOPMENT— when running directly from source (not frozen).

    Returns:
        AppMode: The detected runtime mode.

    Raises:
        RuntimeError: If no mode can be determined (this should only occur if the
            environment behaves unexpectedly—e.g., frozen state is ambiguous).
    """
    # 1) Highest priority: packaged as a frozen binary (PyInstaller/cx_Freeze)
    if _is_running_as_executable():
        return AppMode.EXECUTABLE

    # 2) Tests take precedence over normal source runs
    if _is_running_a_unittest():
        return AppMode.UNITTEST

    # 3) Default to development when running from source (not frozen)
    if _is_running_from_source():
        return AppMode.DEVELOPMENT

    # Defensive: if we get here, the environment is inconsistent
    raise RuntimeError("Unable to determine application mode.")


# Module-level constant
APP_MODE: Final[AppMode] = _determine_app_mode()
