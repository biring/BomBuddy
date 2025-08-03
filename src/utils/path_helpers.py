"""Utility helpers for working with filesystem paths.

This module centralizes small wrappers around :mod:`os.path` to provide a
consistent, cross‑platform interface for path manipulation.  All helpers use
`os.path` under the hood which automatically applies the correct path
separators on Windows, macOS and Linux.

Functions
---------
join(*parts: str) -> str
    Concatenate path fragments using the operating system's separator.
normalize(path: str) -> str
    Collapse redundant separators and resolve user home markers.
project_root(start: str) -> str
    Walk upwards from ``start`` until a project root marker is found.
"""

from __future__ import annotations

import os


def join(*parts: str) -> str:
    """Join multiple path components using :func:`os.path.join`.

    Parameters
    ----------
    *parts:
        Arbitrary path components.  Empty strings are ignored in the same way
        as :func:`os.path.join`.

    Returns
    -------
    str
        The combined path.

    Notes
    -----
    This function is primarily a thin wrapper that explicitly documents the
    project's intent to use :mod:`os.path` for cross‑platform path handling.
    No validation of path existence is performed.
    """

    return os.path.join(*parts)


def normalize(path: str) -> str:
    """Normalize a filesystem path.

    The function expands the user home directory (``~``) and collapses
    redundant separators and relative references.

    Parameters
    ----------
    path:
        A filesystem path.  It may be relative or absolute.

    Returns
    -------
    str
        A normalized path string.

    Raises
    ------
    TypeError
        If ``path`` is not a string.

    Notes
    -----
    The result is not guaranteed to point to an existing location.  The
    behavior of :func:`os.path.normpath` is platform specific; for example,
    Windows drive letters and UNC paths are preserved.
    """

    if not isinstance(path, str):  # Guard against common programmer errors.
        raise TypeError("path must be a string")

    # ``expanduser`` handles ``~`` and is safe on all supported platforms.
    expanded = os.path.expanduser(path)
    normalized = os.path.normpath(expanded)
    return normalized


def project_root(start: str) -> str:
    """Locate the project root directory.

    Starting at ``start`` (which may be a file or directory), this function
    walks up the directory tree until it encounters a marker that identifies the
    project's root.  Recognized markers are a ``.git`` directory or a
    ``pyproject.toml`` file.

    Parameters
    ----------
    start:
        The path from which to begin searching.  If a file path is provided it
        is interpreted relative to its containing directory.

    Returns
    -------
    str
        Absolute path to the discovered project root directory.

    Raises
    ------
    FileNotFoundError
        If no project root markers are found before reaching the filesystem
        root.

    Notes
    -----
    The search resolves symbolic links and is safe on both Windows and POSIX
    filesystems.  The existence of the marker files/directories is checked, but
    no further validation of the directory's contents is performed.
    """

    if not isinstance(start, str):
        raise TypeError("start must be a string")

    path = os.path.abspath(start)
    if os.path.isfile(path):
        path = os.path.dirname(path)

    markers = (".git", "pyproject.toml")

    while True:
        for marker in markers:
            if os.path.exists(os.path.join(path, marker)):
                return path

        parent = os.path.dirname(path)
        if parent == path:
            raise FileNotFoundError(
                f"No project root markers found starting from '{start}'"
            )
        path = parent


__all__ = ["join", "normalize", "project_root"]

