#!/usr/bin/env python3
"""Bounded, fidelity-oriented Markdown file I/O for MaqaronyPad."""
from __future__ import annotations

import codecs
import hashlib
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_DOCUMENT_CHARACTERS = 25_000_000
SUPPORTED_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}
_READ_CHUNK_SIZE = 1024 * 1024
_MAX_STABILITY_ATTEMPTS = 2


class UnsupportedFileError(OSError):
    """Raised when a selected path is not a regular file."""


class FileTooLargeError(OSError):
    """Raised when a file exceeds MaqaronyPad's configured size limit."""


class FileStateChangedError(OSError):
    """Raised when a path changes while MaqaronyPad is reading or saving it."""


@dataclass(frozen=True, slots=True)
class FileState:
    """Stable identity for both the opened path entry and its regular target."""

    path_device: int
    path_inode: int
    path_type: int
    path_mode: int
    target_device: int
    target_inode: int
    target_type: int
    target_mode: int
    size: int
    mtime_ns: int
    ctime_ns: int

    @property
    def is_symlink(self) -> bool:
        return self.path_type == stat.S_IFLNK

    # Compatibility aliases retained for the existing MaqaronyPad document model.
    @property
    def device(self) -> int:
        return self.target_device

    @property
    def inode(self) -> int:
        return self.target_inode

    @property
    def file_type(self) -> int:
        return self.target_type

    @property
    def mode(self) -> int:
        return self.target_mode


@dataclass(frozen=True, slots=True)
class FileSnapshot:
    """A stable file state plus an exact-content digest."""

    state: FileState
    digest: str


@dataclass(slots=True)
class DocumentData:
    text: str
    encoding: str
    bom: bytes
    newline: str
    signature: tuple[int, int, int, int] | None
    snapshot: FileSnapshot | None = None


def absolute_user_path(value: str | os.PathLike[str]) -> Path:
    """Return an absolute user path without resolving its final symbolic link."""
    expanded = Path(value).expanduser()
    return Path(os.path.abspath(os.fspath(expanded)))


def path_lexists(path: Path) -> bool:
    """Like Path.exists(), but also report dangling symbolic links."""
    return os.path.lexists(os.fspath(path))


def _file_state(path_stat: os.stat_result, target_stat: os.stat_result) -> FileState:
    return FileState(
        path_device=int(path_stat.st_dev),
        path_inode=int(path_stat.st_ino),
        path_type=stat.S_IFMT(path_stat.st_mode),
        path_mode=int(path_stat.st_mode),
        target_device=int(target_stat.st_dev),
        target_inode=int(target_stat.st_ino),
        target_type=stat.S_IFMT(target_stat.st_mode),
        target_mode=int(target_stat.st_mode),
        size=int(target_stat.st_size),
        mtime_ns=int(target_stat.st_mtime_ns),
        ctime_ns=int(target_stat.st_ctime_ns),
    )


def _validate_path_entry(path_state: os.stat_result) -> None:
    if stat.S_ISREG(path_state.st_mode) or stat.S_ISLNK(path_state.st_mode):
        return
    raise UnsupportedFileError("The selected path is not a regular file.")


def _open_read_only(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
    flags |= getattr(os, "O_NOCTTY", 0)
    return os.open(path, flags)


def current_file_state(path: Path) -> FileState:
    """Return stable identity for a path entry and the regular file it names."""
    last_error: OSError | None = None
    for _attempt in range(_MAX_STABILITY_ATTEMPTS):
        descriptor: int | None = None
        try:
            path_before = os.lstat(path)
            _validate_path_entry(path_before)
            descriptor = _open_read_only(path)
            target_state = os.fstat(descriptor)
            path_after = os.lstat(path)
            if not stat.S_ISREG(target_state.st_mode):
                raise UnsupportedFileError("The selected path is not a regular file.")
            state = _file_state(path_after, target_state)
            stable_path = (
                path_before.st_dev == path_after.st_dev
                and path_before.st_ino == path_after.st_ino
                and stat.S_IFMT(path_before.st_mode) == state.path_type
            )
            if stable_path:
                return state
            last_error = FileStateChangedError(
                "The file path changed while MaqaronyPad was checking it."
            )
        except UnsupportedFileError:
            raise
        except OSError as error:
            last_error = error
        finally:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
    assert last_error is not None
    raise last_error


def path_identity_matches(path: Path, expected: FileState) -> bool:
    """Return whether the same path entry is still present."""
    try:
        details = os.lstat(path)
    except OSError:
        return False
    return (
        int(details.st_dev) == expected.path_device
        and int(details.st_ino) == expected.path_inode
        and stat.S_IFMT(details.st_mode) == expected.path_type
    )


def read_regular_file(path: Path, max_size: int = MAX_FILE_BYTES) -> tuple[bytes, FileSnapshot]:
    """Read a stable regular target while also retaining the opened path identity."""
    last_error: OSError | None = None
    for _attempt in range(_MAX_STABILITY_ATTEMPTS):
        descriptor: int | None = None
        try:
            path_before = os.lstat(path)
            _validate_path_entry(path_before)
            descriptor = _open_read_only(path)
            target_before = os.fstat(descriptor)
            if not stat.S_ISREG(target_before.st_mode):
                raise UnsupportedFileError("The selected path is not a regular file.")
            if target_before.st_size > max_size:
                raise FileTooLargeError(
                    f"File is larger than MaqaronyPad's {max_size // (1024 * 1024)} MiB read limit."
                )

            chunks: list[bytes] = []
            digest = hashlib.sha256()
            total = 0
            while True:
                chunk = os.read(descriptor, _READ_CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > max_size:
                    raise FileTooLargeError(
                        f"File is larger than MaqaronyPad's {max_size // (1024 * 1024)} MiB read limit."
                    )
                digest.update(chunk)
                chunks.append(chunk)

            target_after = os.fstat(descriptor)
            path_after = os.lstat(path)
            state = _file_state(path_after, target_after)
            stable_path = (
                path_before.st_dev == path_after.st_dev
                and path_before.st_ino == path_after.st_ino
                and stat.S_IFMT(path_before.st_mode) == state.path_type
            )
            stable_target = (
                target_before.st_dev == target_after.st_dev
                and target_before.st_ino == target_after.st_ino
                and target_before.st_size == target_after.st_size
                and target_before.st_mtime_ns == target_after.st_mtime_ns
                and target_before.st_ctime_ns == target_after.st_ctime_ns
            )
            if stable_path and stable_target:
                return b"".join(chunks), FileSnapshot(state, digest.hexdigest())
            last_error = FileStateChangedError(
                "The file changed while MaqaronyPad was reading it. Try again."
            )
        except (UnsupportedFileError, FileTooLargeError):
            raise
        except OSError as error:
            last_error = error
        finally:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
    assert last_error is not None
    raise last_error


def validated_symlink_target(path: Path, expected: FileState) -> Path:
    """Resolve an unchanged symlink to its unchanged regular-file target for saving."""
    if not expected.is_symlink:
        raise FileStateChangedError("The save target is no longer a symbolic link.")
    if current_file_state(path) != expected:
        raise FileStateChangedError(
            "The symbolic-link save target changed before MaqaronyPad could write it."
        )
    try:
        target = path.resolve(strict=True)
    except OSError as error:
        raise FileStateChangedError(
            "The symbolic-link save target cannot be resolved."
        ) from error
    target_state = os.stat(target)
    if not stat.S_ISREG(target_state.st_mode):
        raise UnsupportedFileError("The symbolic link does not point to a regular file.")
    if (
        int(target_state.st_dev) != expected.target_device
        or int(target_state.st_ino) != expected.target_inode
    ):
        raise FileStateChangedError(
            "The symbolic-link target changed before MaqaronyPad could save it."
        )
    return target


def file_signature(path: Path) -> tuple[int, int, int, int] | None:
    try:
        state = current_file_state(path)
    except OSError:
        return None
    return (state.device, state.inode, state.size, state.mtime_ns)


def _detect_newline(text: str) -> str:
    crlf = text.count("\r\n")
    stripped = text.replace("\r\n", "")
    cr = stripped.count("\r")
    lf = stripped.count("\n")
    if crlf >= cr and crlf >= lf and crlf:
        return "\r\n"
    if cr > lf and cr:
        return "\r"
    return "\n"


def _decode(raw: bytes, encoding_override: str | None = None) -> tuple[str, str, bytes]:
    bom_map = (
        (codecs.BOM_UTF32_LE, "utf-32-le"), (codecs.BOM_UTF32_BE, "utf-32-be"),
        (codecs.BOM_UTF8, "utf-8"), (codecs.BOM_UTF16_LE, "utf-16-le"), (codecs.BOM_UTF16_BE, "utf-16-be"),
    )
    for bom, encoding in bom_map:
        if raw.startswith(bom):
            return raw[len(bom):].decode(encoding, errors="strict"), encoding, bom
    if encoding_override:
        return raw.decode(encoding_override, errors="strict"), encoding_override, b""
    return raw.decode("utf-8", errors="strict"), "utf-8", b""


def _looks_binary_text(text: str) -> bool:
    if "\x00" in text:
        return True
    if not text:
        return False
    controls = sum(1 for char in text if ord(char) < 32 and char not in "\t\n\r\f\b")
    return controls / len(text) > 0.02


def load_document(path: str | os.PathLike[str], *, encoding_override: str | None = None) -> DocumentData:
    target = absolute_user_path(path)
    raw, snapshot = read_regular_file(target, MAX_FILE_BYTES)
    text, encoding, bom = _decode(raw, encoding_override)
    if _looks_binary_text(text):
        raise ValueError("The file appears to contain binary control data and is not a plain Markdown document.")
    newline = _detect_newline(text)
    # QPlainTextEdit is LF-oriented; retain original newline style separately.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(text) > MAX_DOCUMENT_CHARACTERS:
        raise ValueError("The decoded Markdown document exceeds MaqaronyPad's 25,000,000-character safety limit.")
    signature = (snapshot.state.device, snapshot.state.inode, snapshot.state.size, snapshot.state.mtime_ns)
    return DocumentData(text, encoding, bom, newline, signature, snapshot)


def _encode_text(text: str, encoding: str, bom: bytes, newline: str) -> bytes:
    normalized = str(text).replace("\r\n", "\n").replace("\r", "\n")
    if newline != "\n":
        normalized = normalized.replace("\n", newline)
    try:
        payload = normalized.encode(encoding, errors="strict")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"This document contains characters that cannot be represented in {encoding}. "
            "Save was cancelled; the existing file was not changed."
        ) from exc
    encoded = bom + payload
    if len(encoded) > MAX_FILE_BYTES:
        raise ValueError(
            f"The file exceeds MaqaronyPad's {MAX_FILE_BYTES // (1024 * 1024)} MiB editor safety limit."
        )
    return encoded


def encode_document(text: str, *, encoding: str, bom: bytes, newline: str) -> bytes:
    """Encode editor text according to the current MaqaronyPad fidelity policy."""
    return _encode_text(text, encoding, bom, newline)


def fsync_directory(directory: Path) -> None:
    if os.name == "nt":
        return
    descriptor: int | None = None
    try:
        descriptor = os.open(directory, os.O_RDONLY | getattr(os, "O_CLOEXEC", 0))
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass


def install_new_file_from_temp(temporary: Path, destination: Path) -> None:
    """Install a synchronized temporary file without overwriting a raced path."""
    try:
        os.link(temporary, destination, follow_symlinks=False)
    except FileExistsError as error:
        raise FileStateChangedError(
            "A file appeared at the save location. Saving was cancelled."
        ) from error
    except (AttributeError, NotImplementedError, TypeError, OSError):
        descriptor: int | None = None
        created = False
        try:
            source_mode = temporary.stat().st_mode & 0o7777
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
            descriptor = os.open(destination, flags, source_mode)
            created = True
            if hasattr(os, "fchmod"):
                os.fchmod(descriptor, source_mode)
            with temporary.open("rb") as source, os.fdopen(descriptor, "wb") as target:
                descriptor = None
                while True:
                    chunk = source.read(_READ_CHUNK_SIZE)
                    if not chunk:
                        break
                    target.write(chunk)
                target.flush()
                os.fsync(target.fileno())
        except FileExistsError as error:
            raise FileStateChangedError(
                "A file appeared at the save location. Saving was cancelled."
            ) from error
        except OSError:
            if created:
                try:
                    destination.unlink()
                except OSError:
                    pass
            raise
        finally:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
    try:
        temporary.unlink()
    except OSError:
        pass


def snapshot_from_payload(path: Path, payload: bytes) -> FileSnapshot:
    return FileSnapshot(current_file_state(path), hashlib.sha256(payload).hexdigest())


def safe_atomic_save(
    path: str | os.PathLike[str],
    text: str,
    *,
    encoding: str = "utf-8",
    bom: bytes = b"",
    newline: str = "\n",
    expected: FileSnapshot | None,
) -> FileSnapshot:
    """Atomically save without replacing or silently retargeting an opened symlink."""
    target = absolute_user_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = _encode_text(text, encoding, bom, newline)

    if expected is None:
        if path_lexists(target):
            raise FileStateChangedError(
                "A file appeared at the save location. Saving was cancelled."
            )
        write_path = target
        mode = 0o666
    else:
        if current_file_state(target) != expected.state:
            raise FileStateChangedError(
                "The file changed again before MaqaronyPad could save it."
            )
        write_path = (
            validated_symlink_target(target, expected.state)
            if expected.state.is_symlink
            else target
        )
        mode = expected.state.target_mode & 0o7777

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{write_path.name}.maqarony_pad-", suffix=".tmp", dir=str(write_path.parent)
    )
    temp_path = Path(temp_name)
    try:
        if hasattr(os, "fchmod"):
            try:
                os.fchmod(fd, mode)
            except OSError:
                pass
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if expected is None:
            install_new_file_from_temp(temp_path, write_path)
        else:
            if current_file_state(target) != expected.state:
                raise FileStateChangedError(
                    "The file changed again before MaqaronyPad could replace it."
                )
            if expected.state.is_symlink and validated_symlink_target(
                target, expected.state
            ) != write_path:
                raise FileStateChangedError(
                    "The symbolic-link target changed before replacement."
                )
            os.replace(temp_path, write_path)
        fsync_directory(write_path.parent)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
    return snapshot_from_payload(target, payload)



def write_new_bytes(path: Path, payload: bytes, *, mode: int = 0o666) -> FileSnapshot:
    """Create one new synchronized file without clobbering an existing path."""
    target = absolute_user_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if path_lexists(target):
        raise FileStateChangedError("A file appeared at the destination. Operation cancelled.")
    fd, raw_name = tempfile.mkstemp(
        prefix=f".{target.name}.maqarony_pad-", suffix=".tmp", dir=str(target.parent)
    )
    temporary = Path(raw_name)
    try:
        if hasattr(os, "fchmod"):
            try:
                os.fchmod(fd, mode & 0o7777)
            except OSError:
                pass
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        install_new_file_from_temp(temporary, target)
        fsync_directory(target.parent)
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
    return snapshot_from_payload(target, payload)

def rename_path_no_replace(source: Path, destination: Path) -> None:
    """Rename a file without overwriting a destination that raced in."""
    try:
        os.link(source, destination, follow_symlinks=False)
    except FileExistsError as error:
        raise FileStateChangedError(
            "A file appeared at the rename destination. Rename was cancelled."
        ) from error
    except (AttributeError, NotImplementedError, TypeError, OSError):
        if path_lexists(destination):
            raise FileStateChangedError(
                "A file appeared at the rename destination. Rename was cancelled."
            )
        os.rename(source, destination)
        return
    try:
        source.unlink()
    except OSError:
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def atomic_save(
    path: str | os.PathLike[str], text: str, *, encoding: str = "utf-8",
    bom: bytes = b"", newline: str = "\n"
) -> tuple[int, int, int, int] | None:
    """Historical MaqaronyPad save helper retained for compatibility/tests."""
    target = Path(path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = _encode_text(text, encoding, bom, newline)
    old_mode: int | None = None
    try:
        old_mode = target.stat().st_mode & 0o7777
    except OSError:
        pass
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(target.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if old_mode is not None:
            os.chmod(temp_path, old_mode)
        os.replace(temp_path, target)
        fsync_directory(target.parent)
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
    return file_signature(target)
