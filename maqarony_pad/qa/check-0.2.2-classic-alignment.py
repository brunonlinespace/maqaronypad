#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.2 Item 29 Classic-toolbar alignment contract."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "markopad.py"
APP = APP_PATH.read_text(encoding="utf-8")


def req(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def method_source(name: str) -> str:
    tree = ast.parse(APP)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MarkopadWindow")
    node = next(n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
    lines = APP.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno]) + "\n"


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(name: str) -> str:
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()


req('APP_VERSION = "0.2.2"' in APP, "0.2.2 identity missing")

# Default Classic selection: still user-removable/empty-capable, but now starts with
# Image Reference, all three view modes, Toolbar Style and Customise Classic Bar.
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
    "source", "split", "preview", "toolbar_style", "customize_classic",
], f"Classic default changed unexpectedly: {defaults}")

# Classic inventory must follow top-level AppMenu order and flatten normal submenus.
catalog = method_source("_classic_toolbar_catalog")
ordered_markers = [
    '# File (including flattened More Actions)',
    '# Edit',
    '# Markdown',
    '# Insert (flattened Link submenu)',
    '# View (flattened Editor Layout / Toolbar / Zoom / Miscellaneous)',
    '# Settings.',
    '# Help',
]
positions = [catalog.index(marker) for marker in ordered_markers]
req(positions == sorted(positions), "Classic catalogue no longer follows File/Edit/Markdown/Insert/View/Settings/Help order")

# File must include Exit as an optional Classic command and preserve AppMenu More Actions ordering.
for fragment in (
    '("File", "duplicate_file", "Duplicate File", self.duplicate_file_action)',
    '("File", "rename_file", "Rename", self.rename_file_action)',
    '("File", "delete_file", "Delete File", self.delete_file_action)',
    '("File", "external_editor", "Open in External Editor", self.external_editor_action)',
    '("File", "open_folder", "Open Containing Folder", self.open_folder_action)',
    '("File", "properties", "Properties", self.properties_action)',
    '("File", "exit", "Exit", self.exit_action)',
):
    req(fragment in catalog, f"required File option missing: {fragment}")

# Multi-choice groups remain flat; exact binary groups collapse to one synthetic toggle.
for fragment in (
    '("View", "source", "Source Only", self.source_only_action)',
    '("View", "split", "Source + Preview", self.split_action)',
    '("View", "preview", "Preview Only", self.preview_only_action)',
    '("Settings", "theme_light", "Light", self.theme_light_action)',
    '("Settings", "theme_dark", "Dark", self.theme_dark_action)',
    '("Settings", "theme_system", "System", self.theme_system_action)',
    '("View", "toolbar_style", "Toolbar Style", self.toolbar_style_toggle_action)',
    '("Settings", "drop_mode", "App Drag-and-Drop", self.drop_mode_toggle_action)',
):
    req(fragment in catalog, f"Classic flattened/toggle inventory missing: {fragment}")
for forbidden in (
    '("View", "tabbed_mode"', '("View", "classic_mode"',
    '("Settings", "drop_active"', '("Settings", "drop_new_window"',
):
    req(forbidden not in catalog, f"binary radio pair leaked into Classic inventory: {forbidden}")

# Exactly the two approved policy menuActions remain toolbar flyouts.
for fragment in (
    '("Settings", "dirty_duplicate_policy", "Duplicate File with Unsaved Changes", self.dirty_duplicate_tabbed_action)',
    '("Settings", "dirty_external_policy", "Open Externally with Unsaved Changes", self.dirty_external_tabbed_action)',
):
    req(fragment in catalog, f"approved Classic policy flyout missing: {fragment}")
style = method_source("_style_command_button")
req('if action is not None and action.menu() is not None:' in style, "Classic menu-bearing actions are not InstantPopup-capable")
req('if tabbed and action is not None and action.menu() is not None:' not in style, "InstantPopup is still restricted to Tabbed")

# Toolbar Style must be one compact toggle on the Tabbed bar too.
tabbed = method_source("_create_tabbed_toolbar")
req('[self.toolbar_style_toggle_action, self.customize_classic_action]' in tabbed, "Tabbed View lacks compact Toolbar Style toggle")
req('[self.tabbed_mode_action, self.classic_mode_action, self.customize_classic_action]' not in tabbed, "Tabbed View still exposes separate Tabbed/Classic buttons")

# The AppMenu remains the canonical radio presentation; no menu restructuring in 0.2.2.
req(sha_text(method_source("_create_menus")) == "e3b7ef68a817a88297d0fc31d334b62ca9956a195ab4b299b0113e01e337ac29", "AppMenu changed during Classic alignment")
for fragment in (
    'self.toolbar_menu.addAction(self.tabbed_mode_action); self.toolbar_menu.addAction(self.classic_mode_action)',
    'behaviour.addAction(self.drop_active_action); behaviour.addAction(self.drop_new_window_action)',
):
    req(fragment in method_source("_create_menus"), f"canonical AppMenu radio pair missing: {fragment}")

# Compact toggles mirror canonical state and keep provenance in their tooltip.
sync = method_source("_sync_compact_toolbar_toggles")
for fragment in (
    'self.toolbar_style_toggle_action.setChecked(classic)',
    'self.toolbar_style_toggle_action.setToolTip(f"Editor Toolbar — {toolbar_label}")',
    'self.drop_mode_toggle_action.setChecked(new_window)',
    'self.drop_mode_toggle_action.setToolTip(f"App Drag-and-Drop — {drop_label}")',
    '"toolbar-classic" if classic else "toolbar-tabbed"',
    '"drop-new-window" if new_window else "drop-active"',
):
    req(fragment in sync, f"compact toggle state contract missing: {fragment}")

# Existing Classic users who selected either old drag/drop radio option migrate to one toggle.
init = method_source("__init__")
for fragment in ('("drop_active", "drop_new_window")', 'if "drop_mode" not in self.classic_toolbar_items:', 'self.classic_toolbar_items.append("drop_mode")'):
    req(fragment in init, f"old Classic drag/drop selection migration missing: {fragment}")

# Classic remains allowed to be completely empty: no minimum-selection guard was added.
dialog = method_source("show_classic_toolbar_dialog")
req('self.classic_toolbar_items = [item_id for _group, item_id, _label, _action in self._classic_toolbar_catalog() if checks[item_id].isChecked()]' in dialog, "Classic empty-toolbar save path changed")
for forbidden in ('at least one', 'minimum one', 'if not self.classic_toolbar_items'):
    req(forbidden not in dialog.casefold(), f"Classic empty-toolbar behavior was restricted: {forbidden}")

# Toggle Comment remains AppMenu/shortcut-only until the canonical Marko icon family has a
# dedicated toolbar asset; no blank icon-only Classic control is introduced opportunistically.
req('("Edit", "comment",' not in catalog, "Toggle Comment was added as a blank icon-only Classic control")

# Item 30 remains investigation-only: Paste semantics and QAction assignments are untouched.
for fragment in (
    'self.paste_action = self._action("Paste", lambda: self.editor.paste(), QKeySequence.StandardKey.Paste)',
    'self.paste_markdown_action = self._action("Paste as Markdown", self.paste_as_markdown, "Ctrl+Shift+V")',
):
    req(fragment in APP, f"Item 30 Paste behavior changed before investigation: {fragment}")

# Protect non-Item-29 behavior byte-for-byte/method-for-method against 0.2.1.
protected_methods = {
    "_shortcut_catalog": "b0011bedd0f4d54f74ae29b71f58be88fb6dddf0ebfcb51211ec9ee0660e1004",
    "paste_as_markdown": "30a2c19612c53b741dd0d76c09a46c36156148892a0d6d5ef87bd0c687f6696e",
    "delete_file": "8c03f4ad2ae9a8e2c0144ae5b9910f6d784cde108a2f7d9d00f47209cc2ecf74",
    "save_as": "d667d51daf2d2b8ce7346c29bf36c23b1df8b17f8c6b22eaf189fd2234fde300",
    "_update_ui_state": "02019f300bac514f8786a1c61fbaa6e8f3dc7280caa52944dce12b0ad6c4a4ba",
    "set_theme": "a31658f09adf675647828b41f2d81dd23848ae0994ef86ef8184bd0425efba08",
    "_create_status_bar": "5a4577f3e84ef0afc265b3777964ffda19eb345df8b79916f35a9292c3e60434",
    "show_properties": "7d77d46871a3a412defed21beb0dda45e9a3ac4bdb9bdc6234a1ad3e19db7d9a",
}
for name, expected in protected_methods.items():
    req(sha_text(method_source(name)) == expected, f"out-of-scope protected method changed: {name}")

protected_files = {
    "source_editor.py": "0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py": "e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py": "b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "settings_io.py": "9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
    "legacy_ricopad.py": "2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
}
for name, expected in protected_files.items():
    req(sha_file(name) == expected, f"out-of-scope protected file changed: {name}")

print("Markopad 0.2.2 Classic-toolbar alignment contract passed.")
