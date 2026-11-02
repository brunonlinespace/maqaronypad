#!/usr/bin/env python3
# ==============================================================================
# MaqaronyPad - focused Markdown editor
# Copyright (C) 2026 Bruno Machado
# GPLv3-or-later
# ==============================================================================
"""Small, dependency-light helpers for private MaqaronyPad JSON preferences."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path

MAX_CONFIG_BYTES = 1024 * 1024
_READ_CHUNK_SIZE = 64 * 1024


def _ensure_private_directory(directory: Path) -> None:
    """Create and validate MaqaronyPad's user-private configuration directory."""
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    details = os.lstat(directory)
    if not stat.S_ISDIR(details.st_mode):
        raise OSError(f"Not a private directory: {directory}")
    if hasattr(os, "getuid") and details.st_uid != os.getuid():
        raise OSError(f"Directory is not owned by the current user: {directory}")
    try:
        os.chmod(directory, 0o700)
    except OSError:
        # Permission normalization may be unavailable on non-POSIX filesystems.
        pass


def _fsync_directory(directory: Path) -> None:
    """Best-effort durability barrier for a completed atomic replacement."""
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_DIRECTORY", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(directory, flags)
        os.fsync(descriptor)
    except OSError:
        # Directory fsync is not supported by every platform/filesystem.
        pass
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def _read_private_regular_file(path: Path) -> bytes:
    """Read one stable, bounded, non-symlink regular file."""
    path_before = os.lstat(path)
    if not stat.S_ISREG(path_before.st_mode):
        raise OSError("Preferences path is not a regular file.")
    if path_before.st_size > MAX_CONFIG_BYTES:
        raise OSError("Preferences file exceeds the 1 MiB limit.")

    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_NOCTTY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)

    descriptor: int | None = None
    try:
        descriptor = os.open(path, flags)
        opened_before = os.fstat(descriptor)
        if not stat.S_ISREG(opened_before.st_mode):
            raise OSError("Preferences path is not a regular file.")
        if opened_before.st_size > MAX_CONFIG_BYTES:
            raise OSError("Preferences file exceeds the 1 MiB limit.")

        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, _READ_CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_CONFIG_BYTES:
                raise OSError("Preferences file exceeds the 1 MiB limit.")
            chunks.append(chunk)

        opened_after = os.fstat(descriptor)
        path_after = os.lstat(path)
        stable_path = (
            path_before.st_dev == path_after.st_dev
            and path_before.st_ino == path_after.st_ino
            and stat.S_IFMT(path_before.st_mode) == stat.S_IFMT(path_after.st_mode)
        )
        stable_file = (
            opened_before.st_dev == opened_after.st_dev
            and opened_before.st_ino == opened_after.st_ino
            and opened_before.st_size == opened_after.st_size
            and opened_before.st_mtime_ns == opened_after.st_mtime_ns
            and opened_before.st_ctime_ns == opened_after.st_ctime_ns
        )
        path_matches_open_file = (
            path_after.st_dev == opened_after.st_dev
            and path_after.st_ino == opened_after.st_ino
            and stat.S_ISREG(path_after.st_mode)
        )
        if not (stable_path and stable_file and path_matches_open_file):
            raise OSError("Preferences file changed while MaqaronyPad was reading it.")
        return b"".join(chunks)
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def load_settings(path: Path) -> dict:
    """Return a settings dictionary, or an empty dictionary for unsafe/damaged input."""
    try:
        raw = _read_private_regular_file(path)
        loaded = json.loads(raw.decode("utf-8"))
        return loaded if isinstance(loaded, dict) else {}
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        # Preferences must never prevent MaqaronyPad from starting.
        return {}


def save_settings(path: Path, data: dict) -> bool:
    """Atomically write MaqaronyPad preferences without following a config symlink."""
    temporary: Path | None = None
    descriptor: int | None = None
    try:
        _ensure_private_directory(path.parent)
        try:
            existing = os.lstat(path)
        except FileNotFoundError:
            existing = None
        if existing is not None and not stat.S_ISREG(existing.st_mode):
            return False

        descriptor, raw_path = tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            text=True,
        )
        temporary = Path(raw_path)
        if hasattr(os, "fchmod"):
            os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = None
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary, path)
        temporary = None
        _fsync_directory(path.parent)
        return True
    except OSError:
        return False
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass
