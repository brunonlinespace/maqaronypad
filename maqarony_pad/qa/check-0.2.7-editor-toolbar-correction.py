#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.7 Editor Toolbar correction gate."""
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

req('APP_VERSION = "0.2.7"' in APP, "0.2.7 identity missing")

# App Theme remains available and shortcut-free.
for frag in (
    'self.theme_light_action = self._action("Light", lambda: self.set_theme("light"), checkable=True)',
    'self.theme_dark_action = self._action("Dark", lambda: self.set_theme("dark"), checkable=True)',
    'self.theme_system_action = self._action("System", lambda: self.set_theme("system"), checkable=True)',
):
    req(frag in APP, f"missing shortcut-free theme action: {frag}")
for shortcut in ("Ctrl+Alt+Shift+1", "Ctrl+Alt+Shift+2", "Ctrl+Alt+Shift+3"):
    req(shortcut not in APP, f"removed App Theme shortcut remains: {shortcut}")

# User-facing toolbar naming changes only; internal state remains tabbed/classic.
req('self.tabbed_mode_action = self._action("Modern (default)", lambda: self.set_toolbar_mode("tabbed"), checkable=True)' in APP,
    "Modern label/internal tabbed mapping missing")
req('self.classic_mode_action = self._action("Classic", lambda: self.set_toolbar_mode("classic"), checkable=True)' in APP,
    "Classic mode action changed")
req('self.tabbed_mode_action = self._action("Tabbed (default)"' not in APP,
    "old Tabbed user-facing submenu label remains")
req('self.toolbar_mode = stored_toolbar if stored_toolbar in {"tabbed", "classic"} else "tabbed"' in APP,
    "internal toolbar mode/state was renamed or changed")

# Ctrl+Alt+Shift+T is an independent shortcut-only toggle, not a toolbar button.
for frag in (
    'self.toolbar_mode_shortcut_action = self._action(',
    '"Toggle Editor Toolbar", self.toggle_toolbar_style, "Ctrl+Alt+Shift+T"',
    'self.addAction(self.toolbar_mode_shortcut_action)',
    'def toggle_toolbar_style(self) -> None:',
    'self.set_toolbar_mode("classic" if self.toolbar_mode == "tabbed" else "tabbed")',
    '("Toggle Editor Toolbar", self.toolbar_mode_shortcut_action)',
):
    req(frag in APP, f"toolbar shortcut contract missing: {frag}")
req('toolbar_style_toggle_action' not in APP,
    "obsolete binary toolbar button/action was reintroduced")

# Editor Toolbar / Editor Layout menu headings use the approved existing icons.
for frag in (
    'self.editor_layout_menu_action = layout.menuAction()',
    'self.editor_toolbar_menu_action = self.toolbar_menu.menuAction()',
    '"editor_layout_menu_action":"toolbar-tabbed", "editor_toolbar_menu_action":"toolbar-classic"',
    'self.toolbar_menu.addAction(self.tabbed_mode_action); self.toolbar_menu.addAction(self.classic_mode_action)',
    'self.toolbar_menu.addSeparator(); self.toolbar_menu.addAction(self.customize_classic_action)',
):
    req(frag in APP, f"approved menu wiring missing: {frag}")
req('for action in (self.tabbed_mode_action, self.classic_mode_action, self.customize_classic_action):\n            action.setIcon(QIcon())' in APP,
    "Editor Toolbar submenu entries are not text-only")

# The flyout remains on both toolbar presentations; Classic customisation remains inside it only.
req('[self.editor_toolbar_menu_action]' in APP, "Modern View lacks Editor Toolbar flyout")
req('("View", "editor_toolbar", "Editor Toolbar", self.editor_toolbar_menu_action)' in APP,
    "Classic catalogue lacks Editor Toolbar flyout")
req('("View", "customize_classic", "Customise Classic Bar...", self.customize_classic_action)' not in APP,
    "standalone Classic customisation toolbar item returned")

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
], f"Classic default changed unexpectedly: {defaults}")

# Existing toolbar icon family is rewired only, never edited.
ICON_ROOT = ROOT / "assets" / "toolbar-icons"
expected_icons = {
    "light": "2241488dcb703c08f82d6389358c77d306dbf1299efa0d5220e3bc189c56311e",
    "dark": "217bfe74d20ea492e21a1964de5bd8b399081246be6a3fa47bc5bdbfd1a3b825",
}
for scheme, digest in expected_icons.items():
    files = sorted((ICON_ROOT / scheme).glob("*.png"))
    req(len(files) == 122, f"{scheme} icon family count changed")
    req(tree_hash(ICON_ROOT / scheme) == digest, f"{scheme} icon family changed")

# Protected editor/Preview/I/O implementations remain byte-for-byte unchanged.
for rel, digest in {
    "source_editor.py":"0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py":"e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py":"b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "settings_io.py":"9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
    "legacy_ricopad.py":"2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
}.items():
    req(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest,
        f"protected implementation changed: {rel}")

# Completed Item 32 remains present and Find/Replace remains outside this release.
for frag in (
    'self.copy_action = self._action("Copy", self._copy_active_text_surface',
    'self.select_all_action = self._action("Select All", self._select_all_active_text_surface',
    'def _preview_is_active_text_surface(self) -> bool:',
    'self.preview.copy()', 'self.preview.selectAll()',
    'obj is self.splitter.handle(1)', 'self.splitter.setSizes([3, 2])',
):
    req(frag in APP, f"Item 32 contract regressed: {frag}")

if errors:
    print("Markopad 0.2.7 check failed:")
    for error in errors:
        print("-", error)
    sys.exit(1)
print("PASS: Markopad 0.2.7 Editor Toolbar correction contract")
