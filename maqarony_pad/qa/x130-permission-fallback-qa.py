#!/usr/bin/env python3
"""x13.0: Desk-authoritative permission restoration, with x12.6 preservation."""
from __future__ import annotations

import errno
import hashlib
import importlib.util
import os
from pathlib import Path
import stat
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "document_io.py").read_bytes()
DESK_ADDITION = (
    b'            if hasattr(os, "fchmod"):\n'
    b'                os.fchmod(descriptor, source_mode)\n'
)
BASELINE_SHA256 = "f8cf3dfdd9eee7a1ded21d6d7ddabbe6b18f71d90265f37dc94d687c624d0aa7"
assert SOURCE.count(DESK_ADDITION) == 1, "Desk permission restoration missing or duplicated"
assert hashlib.sha256(SOURCE.replace(DESK_ADDITION, b"")).hexdigest() == BASELINE_SHA256, (
    "document_io.py differs from x12.6 beyond the two approved lines"
)
anchor = b'            descriptor = os.open(destination, flags, source_mode)\n            created = True\n'
assert SOURCE.count(anchor + DESK_ADDITION) == 1, "permission restoration moved from Desk's exclusive-open location"

spec = importlib.util.spec_from_file_location("maqarony_pad_x130_document_io", ROOT / "document_io.py")
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name] = module
spec.loader.exec_module(module)

if os.name == "posix" and hasattr(os, "fchmod"):
    with tempfile.TemporaryDirectory(prefix="maq-x130-") as directory:
        base = Path(directory)
        content = b"# Permission preservation\n\x00binary staging remains unchanged\n"
        source = base / "staged.tmp"
        destination = base / "new.md"
        source.write_bytes(content)
        source.chmod(0o664)
        original_mode = stat.S_IMODE(source.stat().st_mode)
        original_fchmod = os.fchmod
        previous_umask = os.umask(0o077)
        try:
            with mock.patch.object(module.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "no hard links")), \
                 mock.patch.object(module.os, "fchmod", wraps=original_fchmod) as fchmod:
                module.install_new_file_from_temp(source, destination)
                assert fchmod.call_count == 1, "fchmod must run once in fallback"
                assert fchmod.call_args.args[1] == original_mode
        finally:
            os.umask(previous_umask)
        assert destination.read_bytes() == content
        assert stat.S_IMODE(destination.stat().st_mode) == original_mode == 0o664
        assert not source.exists(), "success should retire the staged file"

        # In a raced collision, O_EXCL still refuses to replace the destination.
        source.write_bytes(b"new staged contents")
        source.chmod(0o664)
        previous_umask = os.umask(0o077)
        try:
            with mock.patch.object(module.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "no hard links")):
                try:
                    module.install_new_file_from_temp(source, destination)
                except module.FileStateChangedError:
                    pass
                else:
                    raise AssertionError("O_EXCL fallback overwrote a raced-in destination")
        finally:
            os.umask(previous_umask)
        assert destination.read_bytes() == content
        assert source.read_bytes() == b"new staged contents"

        # A permission-setting failure must clean up only the newly created destination.
        destination.unlink()
        with mock.patch.object(module.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "no hard links")), \
             mock.patch.object(module.os, "fchmod", side_effect=OSError(errno.EPERM, "denied")):
            try:
                module.install_new_file_from_temp(source, destination)
            except OSError as error:
                assert error.errno == errno.EPERM
            else:
                raise AssertionError("fchmod failure was silently ignored")
        assert not destination.exists()
        assert source.read_bytes() == b"new staged contents"

        # The original hard-link path must remain functional and retain source metadata.
        module.install_new_file_from_temp(source, destination)
        assert destination.read_bytes() == b"new staged contents"
        assert stat.S_IMODE(destination.stat().st_mode) == 0o664
        assert not source.exists()
else:
    print("Note: POSIX permission runtime cases skipped on this host")

print("PASS x13.0: exact Desk fchmod insertion; fallback permissions, collisions, cleanup and original hard-link path")
