#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.6 approved UI/menu refinement gate."""
from __future__ import annotations
import ast, hashlib, sys
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

req('APP_VERSION = "0.2.6"' in APP, "0.2.6 identity missing")

# Theme commands remain present but own no keyboard shortcuts.
for frag in (
    'self.theme_light_action = self._action("Light", lambda: self.set_theme("light"), checkable=True)',
    'self.theme_dark_action = self._action("Dark", lambda: self.set_theme("dark"), checkable=True)',
    'self.theme_system_action = self._action("System", lambda: self.set_theme("system"), checkable=True)',
):
    req(frag in APP, f"missing shortcut-free theme action: {frag}")
for shortcut in ("Ctrl+Alt+Shift+1", "Ctrl+Alt+Shift+2", "Ctrl+Alt+Shift+3"):
    req(shortcut not in APP, f"removed App Theme shortcut remains: {shortcut}")

# AppMenu menu actions and exact icon assignments.
for frag in (
    'self.editor_layout_menu_action = layout.menuAction()',
    'self.editor_toolbar_menu_action = self.toolbar_menu.menuAction()',
    '"editor_layout_menu_action":"toolbar-classic", "editor_toolbar_menu_action":"toolbar-tabbed"',
    'self.toolbar_menu.addAction(self.tabbed_mode_action); self.toolbar_menu.addAction(self.classic_mode_action)',
    'self.toolbar_menu.addSeparator(); self.toolbar_menu.addAction(self.customize_classic_action)',
):
    req(frag in APP, f"missing approved menu wiring: {frag}")

# Editor Toolbar submenu entries are text-only; the old synthetic binary toggle is gone.
for forbidden in (
    '"tabbed_mode_action":"toolbar-tabbed"',
    '"classic_mode_action":"toolbar-classic"',
    '"customize_classic_action":"toolbar-classic"',
    'toolbar_style_toggle_action',
    'def toggle_toolbar_style',
    'Ctrl+Alt+Shift+T',
):
    req(forbidden not in APP, f"obsolete Editor Toolbar toggle/icon wiring remains: {forbidden}")
req('for action in (self.tabbed_mode_action, self.classic_mode_action, self.customize_classic_action):\n            action.setIcon(QIcon())' in APP,
    "Editor Toolbar submenu entries are not explicitly iconless")

# One Editor Toolbar flyout is present on both toolbar presentations; customisation is no longer standalone.
req('[self.editor_toolbar_menu_action]' in APP, "Tabbed View lacks Editor Toolbar flyout")
req('[self.toolbar_style_toggle_action, self.customize_classic_action]' not in APP,
    "old Tabbed toggle/customise pair remains")
req('("View", "editor_toolbar", "Editor Toolbar", self.editor_toolbar_menu_action)' in APP,
    "Classic catalogue lacks Editor Toolbar flyout")
req('("View", "customize_classic", "Customise Classic Bar...", self.customize_classic_action)' not in APP,
    "Classic catalogue still exposes standalone Customise Classic Bar button")

module = ast.parse(APP)
default_assign = next(
    n for n in module.body
    if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "CLASSIC_TOOLBAR_DEFAULT" for t in n.targets)
)
defaults = ast.literal_eval(default_assign.value)
req(defaults == [
    "new", "open", "save",
    "undo", "redo", "find",
    "bold", "italic", "inline_code",
    "image", "link",
    "source", "split", "preview", "editor_toolbar",
], f"Classic default is not the approved one-flyout replacement: {defaults}")
req('legacy_toolbar_items = {"toolbar_style", "customize_classic"}' in APP,
    "old Classic toolbar selections are not migrated to Editor Toolbar flyout")

# Existing toolbar icon family must be untouched.
ICON_ROOT = ROOT / "assets" / "toolbar-icons"
expected_icons = {
    "light": "2241488dcb703c08f82d6389358c77d306dbf1299efa0d5220e3bc189c56311e",
    "dark": "217bfe74d20ea492e21a1964de5bd8b399081246be6a3fa47bc5bdbfd1a3b825",
}
for scheme, digest in expected_icons.items():
    files = sorted((ICON_ROOT / scheme).glob("*.png"))
    req(len(files) == 122, f"{scheme} icon family count changed")
    req(tree_hash(ICON_ROOT / scheme) == digest, f"{scheme} icon family changed")

# Protected engines and I/O remain byte-for-byte from 0.2.5.
for rel, digest in {
    "source_editor.py":"0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py":"e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py":"b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "settings_io.py":"9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
    "legacy_ricopad.py":"2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
}.items():
    req(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest,
        f"protected implementation changed: {rel}")

# Completed Item 32 remains present.
for frag in (
    'self.copy_action = self._action("Copy", self._copy_active_text_surface',
    'self.select_all_action = self._action("Select All", self._select_all_active_text_surface',
    'def _preview_is_active_text_surface(self) -> bool:',
    'self.preview.copy()', 'self.preview.selectAll()',
    'obj is self.splitter.handle(1)',
    'self.splitter.setSizes([3, 2])',
):
    req(frag in APP, f"Item 32 contract regressed: {frag}")

if errors:
    print("Markopad 0.2.6 check failed:")
    for error in errors:
        print("-", error)
    sys.exit(1)
print("PASS: Markopad 0.2.6 approved UI/menu refinement contract")
