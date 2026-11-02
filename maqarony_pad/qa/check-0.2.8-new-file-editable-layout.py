#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.8 New File editable-layout gate."""
from __future__ import annotations
import hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "markopad.py").read_text(encoding="utf-8")
errors: list[str] = []

def req(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)

def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.glob("*.png")):
        h.update(p.name.encode("utf-8") + b"\0" + p.read_bytes())
    return h.hexdigest()

req('APP_VERSION = "0.2.8"' in APP, "0.2.8 identity missing")

# The ordinary persisted view mode remains three-state; a separate editable-only
# preference remembers Source or Source + Preview without allowing Preview Only
# to erase it.
for frag in (
    'self.view_mode = str(self.settings.get("view_mode", "split"))',
    'stored_editable_view = str(self.settings.get("last_editable_view_mode", ""))',
    'if stored_editable_view not in {"source", "split"}:',
    'stored_editable_view = self.view_mode if self.view_mode in {"source", "split"} else "split"',
    'self.last_editable_view_mode = stored_editable_view',
    '"last_editable_view_mode": self.last_editable_view_mode,',
):
    req(frag in APP, f"editable-layout persistence contract missing: {frag}")

# Only editable layouts update the remembered editable choice.
req('''        self.view_mode = mode
        if mode in {"source", "split"}:
            self.last_editable_view_mode = mode
        self.editor.setVisible(mode in {"source", "split"}); self.preview.setVisible(mode in {"split", "preview"})''' in APP,
    "set_view_mode does not preserve Preview-only exclusion from last editable layout")

# New Document must use the remembered editable layout and must not force a
# hard-coded Source or Split choice.
req('self.set_view_mode(self.last_editable_view_mode, persist=False)' in APP,
    "New Document does not open in the remembered editable layout")
new_start = APP.index('    def new_document(')
new_end = APP.index('    def open_dialog(', new_start)
new_block = APP[new_start:new_end]
req('set_view_mode(self.last_editable_view_mode, persist=False)' in new_block,
    "New Document editable-layout routing is not inside new_document")
req('set_view_mode("source"' not in new_block and 'set_view_mode("split"' not in new_block,
    "New Document hard-codes an editable layout instead of remembering the user choice")

# Ordinary Open remains governed by the regular current layout; this release
# must not globally suppress Preview Only for existing documents.
open_start = APP.index('    def open_path(')
open_end = APP.index('    def _safe_save_current_to(', open_start)
open_block = APP[open_start:open_end]
req('last_editable_view_mode' not in open_block,
    "ordinary Open was incorrectly redirected through the New Document layout preference")

# Preserve the immediately preceding approved UI contract.
for frag in (
    '"Toggle Editor Toolbar", self.toggle_toolbar_style, "Ctrl+Alt+Shift+T"',
    'self.tabbed_mode_action = self._action("Modern (default)", lambda: self.set_toolbar_mode("tabbed"), checkable=True)',
    '"editor_layout_menu_action":"toolbar-tabbed", "editor_toolbar_menu_action":"toolbar-classic"',
):
    req(frag in APP, f"0.2.7 UI contract regressed: {frag}")

# No icon or engine changes belong to this release.
ICON_ROOT = ROOT / "assets" / "toolbar-icons"
expected_icons = {
    "light": "2241488dcb703c08f82d6389358c77d306dbf1299efa0d5220e3bc189c56311e",
    "dark": "217bfe74d20ea492e21a1964de5bd8b399081246be6a3fa47bc5bdbfd1a3b825",
}
for scheme, digest in expected_icons.items():
    files = sorted((ICON_ROOT / scheme).glob("*.png"))
    req(len(files) == 122, f"{scheme} icon family count changed")
    req(tree_hash(ICON_ROOT / scheme) == digest, f"{scheme} icon family changed")

for rel, digest in {
    "source_editor.py":"0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py":"e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py":"b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "settings_io.py":"9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
    "legacy_ricopad.py":"2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
}.items():
    req(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest,
        f"protected implementation changed: {rel}")

if errors:
    print("Markopad 0.2.8 check failed:")
    for error in errors:
        print("-", error)
    sys.exit(1)
print("PASS: Markopad 0.2.8 New File editable-layout contract")
