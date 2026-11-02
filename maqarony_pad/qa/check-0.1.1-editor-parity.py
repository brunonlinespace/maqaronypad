#!/usr/bin/env python3
"""Dependency-light 0.1.1 Marko-family editor-parity contract."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "markopad.py").read_text(encoding="utf-8")
EDITOR = (ROOT / "source_editor.py").read_text(encoding="utf-8")

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert 'APP_VERSION = "0.1.1"' in APP
assert 'MAX_SEARCH_MATCHES = 10_000' in APP
assert 'MAX_SEARCH_QUERY_CHARACTERS = 4096' in APP

# Audit item 2: hardened Markopad-style bottom Find/Replace survives as the UX.
for needle in (
    'self.find_edit.setMaxLength(MAX_SEARCH_QUERY_CHARACTERS)',
    'self.find_action = self._action("Find", lambda: self.toggle_find_panel(False)',
    'self.replace_action = self._action("Find and Replace", lambda: self.toggle_find_panel(True), "Ctrl+H")',
    'self.find_next_action = self._action("Find Next", self.find_next, "F3")',
    'self.find_previous_action = self._action("Find Previous", self.find_previous, "Shift+F3")',
    'self.dismiss_find_action = self._action("Close Find/Replace", self.hide_find_panel, "Esc")',
    'self.find_panel.count_label.setText(f"{current:,}/{total_text}")',
    'selection.format.setBackground(QColor("#C9A227"))',
    'self._current_search_index = 0',
    'edit_cursor.beginEditBlock()',
    'resulting_length = current_length + count * (len(replacement) - len(query))',
    'self._search_refresh_suspended = True',
):
    assert needle in APP, needle
assert 'QDialog(self)\n        dialog.setWindowTitle(dialog_title("Symbols"))' in APP
symbols = (
    "©", "®", "™", "°", "•", "·", "—", "–", "…", "→", "←", "↑", "↓", "✓", "✗", "§",
    "£", "€", "$", "¥", "¢", "±", "×", "÷", "≠", "≤", "≥", "≈", "∞", "µ", "¶", "№",
    "★", "☆", "♥", "♦", "♣", "♠", "☐", "☑",
)
assert len(symbols) == 40 and len(set(symbols)) == 40
for symbol in symbols:
    assert f'"{symbol}"' in APP, symbol
for command in ("kcharselect", "gucharmap", "gnome-characters", "charmap"):
    assert command in APP

# Audit item 9: Plus presentation improvements, without changing Markdown/preview core architecture.
for needle in (
    'self.settings["editor_font_weight"] = int(chosen.weight())',
    'self.settings["editor_font_italic"] = chosen.italic()',
    'font.setItalic(bool(self.settings.get("editor_font_italic", False)))',
    'link_color = QColor("#174EA6")',
    'link_color = QColor("#82AAFF")',
    'preview_palette.setColor(QPalette.ColorRole.LinkVisited, link_color)',
    'QCheckBox("Italicize block quotations", effects)',
    'QTextFormat.Property.BlockQuoteLevel',
    'def _apply_presentation_safely(self, callback) -> None:',
    'was_modified = bool(document.isModified())',
    'document.setModified(was_modified)',
):
    assert needle in APP, needle

# Audit item 10: thin Plus editor adapter behavior is now native standalone behavior.
for needle in (
    'overwrite_mode_changed = pyqtSignal(bool)',
    'Qt.Key.Key_Insert',
    'self.setOverwriteMode(enabled)',
    'Qt.Key.Key_Slash',
    'def toggle_comment(self) -> None:',
    'replacement = f"<!-- {selected} -->"',
    'def _resize_gutter_above_horizontal_scrollbar(self) -> None:',
    'gutter_height = max(0, gutter_height - horizontal.height())',
):
    assert needle in EDITOR, needle
assert 'self.comment_action = self._action("Toggle Comment", lambda: self.editor.toggle_comment(), "Ctrl+/")' in APP
assert '("Toggle Overwrite Mode", "Insert")' in APP

# Explicitly deferred/unchanged audit areas: standalone file policy/lifecycle/status stay put.
assert 'Save As creates a clean UTF-8 file while preserving source text exactly.' in APP
assert 'atomic_save(target, self.editor.toPlainText(), encoding="utf-8", bom=b"", newline=self.file_newline)' in APP
assert 'MAX_DOCUMENT_CHARACTERS = 25_000_000' in EDITOR
assert 'MAX_PASTE_CHARACTERS = 5_000_000' in EDITOR
assert 'def handle_external_change(self) -> None:' in APP
assert 'self.status_left.setText(f"Ln {line}/{self.editor.document().blockCount()}  Col {col}  Chars {len(text):,}  Words {words:,}")' in APP
assert 'self.status_right.setText(f"{self.file_encoding.upper()}  {newline}  {view}  {self.zoom_percent}%")' in APP

# Files outside the editor shell remain the 0.1.0-r2 source implementations.
expected_hashes = {
    "document_io.py": "cd0e2a5b95ded6e95383e5230896cac5145acc004303b83576cf8020205f6b88",
    "legacy_ricopad.py": "2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
    "preview.py": "e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
}
for name, expected in expected_hashes.items():
    actual = sha(ROOT / name)
    assert actual == expected, (name, actual, expected)

# Source must still parse without importing PyQt6.
ast.parse(APP)
ast.parse(EDITOR)
print("Markopad 0.1.1 editor-parity contract passed.")
