#!/usr/bin/env python3
"""Dependency-light security/fidelity checks for MaqaronyPad 0.3.3."""
from __future__ import annotations

import codecs
import importlib.util
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


doc = load_module("maqarony_pad_document_io", ROOT / "document_io.py")
legacy = load_module("maqarony_pad_legacy", ROOT / "legacy_ricopad.py")

assert doc.MAX_FILE_BYTES == 25 * 1024 * 1024
assert doc.MAX_DOCUMENT_CHARACTERS == 25_000_000
assert doc.SUPPORTED_EXTENSIONS == {".md", ".markdown", ".mdown", ".mkd"}

with tempfile.TemporaryDirectory() as td:
    base = Path(td)
    cases = [
        ("lf.md", "# A\nline\n", "utf-8", b"", "\n"),
        ("crlf.md", "# A\r\nline\r\n", "utf-8", b"", "\r\n"),
        ("bom.md", "# A\n", "utf-8", codecs.BOM_UTF8, "\n"),
        ("no-final-newline.md", "# A", "utf-8", b"", "\n"),
        ("utf16.md", "# A\r\nΩ\r\n", "utf-16-le", codecs.BOM_UTF16_LE, "\r\n"),
        ("utf32.md", "# A\nΩ\n", "utf-32-le", codecs.BOM_UTF32_LE, "\n"),
    ]
    for name, original, encoding, bom, newline in cases:
        path = base / name
        payload = bom + original.encode(encoding)
        path.write_bytes(payload)
        loaded = doc.load_document(path)
        assert loaded.newline == newline
        doc.atomic_save(path, loaded.text, encoding=loaded.encoding, bom=loaded.bom, newline=loaded.newline)
        assert path.read_bytes() == payload, (name, path.read_bytes(), payload)

    # Unmarked non-UTF-8 is not guessed; the UI chooses an encoding explicitly.
    legacy_path = base / "legacy.md"
    legacy_path.write_bytes("café".encode("cp1252"))
    try:
        doc.load_document(legacy_path)
    except UnicodeDecodeError:
        pass
    else:
        raise AssertionError("unmarked legacy encoding was silently guessed")
    assert doc.load_document(legacy_path, encoding_override="cp1252").text == "café"

    # No-NUL safety.
    bad = base / "bad.md"
    bad.write_bytes(b"abc\x00def")
    try:
        doc.load_document(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("NUL-containing input was accepted")

portable = "# Heading\n\nText\n"
wrapped = "<!-- ricopad: rich-markdown-v1 -->\n" + portable + "\n<!-- ricopad-rich-payload-v1\nsha256:" + ("a" * 64) + "\nencoding:zlib+base64\neA==\n-->\n"
stripped, found = legacy.strip_legacy_envelope(wrapped)
assert found
assert stripped == portable
clean, found = legacy.strip_legacy_envelope(portable)
assert not found and clean == portable

print("MaqaronyPad security/fidelity QA passed.")
