#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.5 Audit Item 22 regression contract."""
from __future__ import annotations

import hashlib
import os
import stat
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import settings_io  # noqa: E402

APP = (ROOT / "markopad.py").read_text(encoding="utf-8")

assert 'APP_VERSION = "0.1.5"' in APP

# Item 22: the existing Markopad settings API remains in place and delegates
# only physical JSON persistence to the new dependency-light helper.
assert 'from settings_io import load_settings, save_settings' in APP
assert 'def load_json_settings() -> dict:\n    return load_settings(CONFIG_FILE)' in APP
assert 'def save_json_settings(data: dict) -> None:\n    save_settings(CONFIG_FILE, data)' in APP
assert 'CONFIG_FILE = CONFIG_DIR / "markopad.json"' in APP
assert settings_io.MAX_CONFIG_BYTES == 1024 * 1024

with tempfile.TemporaryDirectory(prefix="markopad-settings-qa-") as raw_root:
    root = Path(raw_root)
    config = root / "private" / "markopad.json"
    original = {
        "theme": "system",
        "toolbar": "tabbed",
        "dirty_duplicate_action": "ask",
        "dirty_external_action": "ask",
    }

    # Missing config remains a normal empty/default-settings condition.
    assert settings_io.load_settings(config) == {}

    # Normal round-trip is exact and uses private POSIX permissions where those
    # permission bits are meaningful.
    assert settings_io.save_settings(config, original) is True
    assert settings_io.load_settings(config) == original
    if os.name == "posix":
        assert stat.S_IMODE(os.lstat(config.parent).st_mode) == 0o700
        assert stat.S_IMODE(os.lstat(config).st_mode) == 0o600

    # Damaged, non-dictionary, oversized, and symlink configs never become
    # trusted preferences and never prevent startup.
    config.write_text("{broken", encoding="utf-8")
    assert settings_io.load_settings(config) == {}
    config.write_text("[]\n", encoding="utf-8")
    assert settings_io.load_settings(config) == {}
    config.write_bytes(b" " * (settings_io.MAX_CONFIG_BYTES + 1))
    assert settings_io.load_settings(config) == {}

    if hasattr(os, "symlink"):
        target = root / "target.json"
        target.write_text('{"untouched": true}\n', encoding="utf-8")
        try:
            config.unlink()
            config.symlink_to(target)
        except (OSError, NotImplementedError):
            pass
        else:
            assert settings_io.load_settings(config) == {}
            assert settings_io.save_settings(config, {"replace": True}) is False
            assert target.read_text(encoding="utf-8") == '{"untouched": true}\n'
            config.unlink()

    # A failed atomic replace leaves the previous config intact and cleans its
    # private temporary file rather than exposing a partial preferences file.
    assert settings_io.save_settings(config, original) is True
    before = config.read_bytes()
    with mock.patch.object(settings_io.os, "replace", side_effect=OSError("simulated replace failure")):
        assert settings_io.save_settings(config, {"theme": "dark"}) is False
    assert config.read_bytes() == before
    assert not list(config.parent.glob(f".{config.name}.*.tmp"))

# Protected Item 14 remains present exactly as a behavioural contract.
assert 'self.editor.document().undoAvailable.connect(lambda _available: self._sync_undo_redo_state())' in APP
assert 'self.editor.document().redoAvailable.connect(lambda _available: self._sync_undo_redo_state())' in APP
assert 'self.undo_action.setEnabled(mutable and document.isUndoAvailable())' in APP
assert 'self.redo_action.setEnabled(mutable and document.isRedoAvailable())' in APP

# Protected Item 6: successful Delete still preserves the live editor.
assert '# Keep the live editor. It is now the only guaranteed surviving copy.' in APP
assert 'self._set_backing_state("missing")' in APP
assert 'File deleted from disk; the open document is retained.' in APP

# Protected Item 16: the same sole Undo/Redo QActions remain; Item 22 must not
# add a second editor command/action ownership path.
assert APP.count('self.undo_action = self._action("Undo"') == 1
assert APP.count('self.redo_action = self._action("Redo"') == 1

# Protected editor/file modules are byte-for-byte unchanged from 0.1.4.
expected = {
    'source_editor.py': '0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327',
    'preview.py': 'e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965',
    'document_io.py': 'c14a37ec13162881b68a975ceaf6238a6bcc7e134f658679dc3b67d84b2418cb',
    'legacy_ricopad.py': '2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40',
}
for name, digest in expected.items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)

print('Markopad 0.1.5 hardened-preferences contract passed.')
