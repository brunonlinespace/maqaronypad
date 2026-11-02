#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.4 Audit Item 14 regression contract."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "markopad.py").read_text(encoding="utf-8")

assert 'APP_VERSION = "0.1.4"' in APP

# Item 14: keep the existing QActions, but drive them from the actual
# QTextDocument undo/redo stacks plus Markopad's existing mutability rules.
assert APP.count('self.undo_action = self._action("Undo"') == 1
assert APP.count('self.redo_action = self._action("Redo"') == 1
assert 'self.editor.document().undoAvailable.connect(lambda _available: self._sync_undo_redo_state())' in APP
assert 'self.editor.document().redoAvailable.connect(lambda _available: self._sync_undo_redo_state())' in APP
assert 'def _sync_undo_redo_state(self) -> None:' in APP
assert 'self.undo_action.setEnabled(mutable and document.isUndoAvailable())' in APP
assert 'self.redo_action.setEnabled(mutable and document.isRedoAvailable())' in APP
assert 'mutation_actions = [self.undo_action, self.redo_action,' not in APP
assert 'self._sync_undo_redo_state()\n        self.update_status()' in APP

# Protected Item 6: successful Delete still preserves the live editor.
assert '# Keep the live editor. It is now the only guaranteed surviving copy.' in APP
assert 'self._set_backing_state("missing")' in APP
assert 'File deleted from disk; the open document is retained.' in APP

# Protected core modules must be byte-for-byte identical to Markopad 0.1.3.
expected = {
    'source_editor.py': '0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327',
    'preview.py': 'e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965',
    'document_io.py': 'c14a37ec13162881b68a975ceaf6238a6bcc7e134f658679dc3b67d84b2418cb',
    'legacy_ricopad.py': '2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40',
}
for name, digest in expected.items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert actual == digest, (name, actual, digest)

print('Markopad 0.1.4 Undo/Redo availability contract passed.')
