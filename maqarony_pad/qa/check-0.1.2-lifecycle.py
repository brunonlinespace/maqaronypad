#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.2 lifecycle-hardening contract."""
from __future__ import annotations

import ast
import importlib.util
import tempfile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "markopad.py").read_text(encoding="utf-8")
IO = (ROOT / "document_io.py").read_text(encoding="utf-8")

assert 'APP_VERSION = "0.1.2"' in APP

# Phase 2B / Audit Item 6: targeted watcher + explicit backing states.
for needle in (
    'self.file_watcher = QFileSystemWatcher(self)',
    'self.file_watcher.fileChanged.connect(self._queue_backing_check)',
    'self.file_watcher.directoryChanged.connect(self._queue_backing_check)',
    'self.backing_check_timer.setInterval(160)',
    'if state not in {"normal", "changed", "missing"}',
    'self.external_label.setText(',
    '"Save Version As preserves the live document; Reload is unavailable."',
    'self.reload_external_button.setEnabled(False)',
    'self._bind_document_watcher()',
):
    assert needle in APP, needle

# Save conflict cannot silently overwrite a changed/missing disk copy.
for needle in (
    'def _external_change_action(self) -> str:',
    'dialog.setWindowTitle(dialog_title("File Changed on Disk"))',
    'dialog.addButton("Reload", QMessageBox.ButtonRole.ActionRole)',
    'dialog.addButton("Save Version As…", QMessageBox.ButtonRole.ActionRole)',
    'dialog.addButton("Overwrite", QMessageBox.ButtonRole.DestructiveRole)',
    'self._overwrite_snapshot = current',
    'safe_atomic_save(',
):
    assert needle in APP, needle

# Clean-but-missing close protection.
for needle in (
    'def _confirm_close_missing_backing(self) -> bool:',
    'dialog.setWindowTitle(dialog_title("Backing File Missing"))',
    'dialog.addButton("Close Without Saving", QMessageBox.ButtonRole.DestructiveRole)',
    'if self.backing_state == "missing":',
):
    assert needle in APP, needle

# Dirty duplicate / external-editor workflows are explicit and cancellable.
for needle in (
    '"Duplicate Current Document"',
    '"Duplicate Last Saved Version"',
    '"Unsaved Changes — Duplicate File"',
    '"Save Changes and Open"',
    '"Open Last Saved Version"',
    '"Unsaved Changes — External Editor"',
):
    assert needle in APP, needle

# Rename/Delete re-check exact state around the destructive action and rebind watcher.
for needle in (
    'rename_path_no_replace(old_path, target)',
    'if current_file_state(self.current_path) != expected.state:',
    'if current_file_state(self.current_path) != expected:',
    '"The Markdown file changed after the confirmation dialog. Nothing was deleted."',
    '"File deleted from disk; the open document is retained."',
):
    assert needle in APP, needle

# Audit Items 3, 8 and 13 stay outside Phase 2B.
assert 'MAX_FILE_BYTES = 64 * 1024 * 1024' in IO
assert '# Historical Markopad policy: ordinary Save As creates UTF-8/no-BOM.' in APP
assert 'return self._save_as_target(target, preserve_encoding=False)' in APP
assert 'self.save_as_action = self._action("Save As…", self.save_as, QKeySequence.StandardKey.SaveAs)' in APP
assert 'self.status_left.setText(f"Ln {line}/{self.editor.document().blockCount()}  Col {col}  Chars {len(text):,}  Words {words:,}")' in APP
assert 'self.status_right.setText(f"{self.file_encoding.upper()}  {newline}  {view}  {self.zoom_percent}%")' in APP

# No Plus workspace/tabs/dashboard scaffolding entered standalone Markopad.
for forbidden in (
    'ModuleRepository', 'WorkspaceManager', 'Tabs Enabled', 'Tabs Disabled',
    'DashboardWidget', 'managed workspace', 'library_root',
):
    assert forbidden not in APP, forbidden

# Exercise the dependency-free safe I/O primitives against real races.
spec = importlib.util.spec_from_file_location("markopad_document_io", ROOT / "document_io.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as raw_tmp:
    tmp = Path(raw_tmp)
    path = tmp / "doc.md"
    snap = module.safe_atomic_save(path, "one\n", expected=None)
    assert path.read_text(encoding="utf-8") == "one\n"
    # A stale snapshot must not clobber a file changed in between.
    path.write_text("outside\n", encoding="utf-8")
    try:
        module.safe_atomic_save(path, "editor\n", expected=snap)
    except module.FileStateChangedError:
        pass
    else:
        raise AssertionError("stale expected snapshot overwrote an external change")
    assert path.read_text(encoding="utf-8") == "outside\n"

    _, current = module.read_regular_file(path)
    replaced = module.safe_atomic_save(path, "editor\n", expected=current)
    assert path.read_text(encoding="utf-8") == "editor\n"
    assert replaced.digest != current.digest

    duplicate = tmp / "copy.md"
    module.write_new_bytes(duplicate, b"copy\n")
    try:
        module.write_new_bytes(duplicate, b"clobber\n")
    except module.FileStateChangedError:
        pass
    else:
        raise AssertionError("duplicate helper clobbered an existing destination")

    renamed = tmp / "renamed.md"
    module.rename_path_no_replace(duplicate, renamed)
    assert renamed.read_bytes() == b"copy\n" and not duplicate.exists()
    collision = tmp / "collision.md"
    collision.write_text("existing\n", encoding="utf-8")
    source = tmp / "source.md"
    source.write_text("source\n", encoding="utf-8")
    try:
        module.rename_path_no_replace(source, collision)
    except module.FileStateChangedError:
        pass
    else:
        raise AssertionError("rename helper replaced an existing destination")
    assert source.exists() and collision.read_text(encoding="utf-8") == "existing\n"

ast.parse(APP)
ast.parse(IO)
print("Markopad 0.1.2 lifecycle-hardening contract passed.")
