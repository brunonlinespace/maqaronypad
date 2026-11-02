#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.10 Items 17 + 27B AppMenu/shortcut contract."""
from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "markopad.py"
APP = APP_PATH.read_text(encoding="utf-8")
TREE = ast.parse(APP)

assert 'APP_VERSION = "0.1.10"' in APP


def method(name: str) -> ast.FunctionDef:
    return next(
        node for node in ast.walk(TREE)
        if isinstance(node, ast.FunctionDef) and node.name == name
    )


def method_source(name: str) -> str:
    segment = ast.get_source_segment(APP, method(name))
    assert segment is not None
    return segment


def method_hash(name: str) -> str:
    return hashlib.sha256(method_source(name).encode("utf-8")).hexdigest()

# Item 17: the AppMenu is native/global-menu capable and toolbar mode never hides it.
menus = method_source("_create_menus")
apply_mode = method_source("_apply_toolbar_mode")
assert 'bar.setNativeMenuBar(True)' in menus
assert 'self.menuBar().setVisible(True)' in apply_mode
assert 'self.menuBar().setVisible(not tabbed)' not in APP
for attr, label in (
    ("file_menu", "&File"),
    ("edit_menu", "&Edit"),
    ("markdown_menu", "&Markdown"),
    ("insert_menu", "&Insert"),
    ("view_menu", "&View"),
    ("settings_menu", "&Settings"),
    ("help_menu", "&Help"),
):
    assert f'self.{attr} = bar.addMenu("{label}")' in menus, (attr, label)

# The visible AppMenu inventory itself must be unchanged from 0.1.9.
expected_direct_actions = [
    'new_action', 'new_window_action', 'open_action', 'save_action', 'save_as_action',
    'duplicate_file_action', 'rename_file_action', 'delete_file_action',
    'external_editor_action', 'open_folder_action', 'properties_action', 'print_action',
    'export_pdf_action', 'exit_action', 'save_exit_action',
    'undo_action', 'redo_action', 'cut_action', 'copy_action', 'paste_action',
    'paste_markdown_action', 'delete_action', 'comment_action', 'duplicate_line_action',
    'delete_line_action', 'select_all_action', 'find_action', 'goto_action', 'replace_action',
    'bold_action', 'italic_action', 'strike_action', 'quote_action', 'bullet_action',
    'number_action', 'task_action', 'indent_action', 'outdent_action', 'inline_code_action',
    'code_fence_action', 'image_action', 'link_action', 'edit_link_action',
    'remove_link_action', 'table_action', 'date_time_action', 'date_action', 'time_action',
    'rule_action', 'symbol_action', 'fullscreen_action', 'status_bar_action',
    'word_wrap_action', 'line_numbers_action', 'editor_canvas_theme_action',
    'view_only_action', 'source_only_action', 'split_action', 'preview_only_action',
    'tabbed_mode_action', 'classic_mode_action', 'customize_classic_action',
    'zoom_in_action', 'zoom_out_action', 'zoom_reset_action', 'tab_width_action',
    'editor_font_action', 'display_font_action', 'theme_light_action', 'theme_dark_action',
    'theme_system_action', 'drop_active_action', 'drop_new_window_action',
    'documentation_action', 'quick_start_action', 'shortcuts_action', 'github_action',
    'issue_action', 'about_action',
]
actual_direct_actions = re.findall(r'\.addAction\(self\.([A-Za-z0-9_]+)\)', menus)
assert actual_direct_actions == expected_direct_actions, (actual_direct_actions, expected_direct_actions)
for required_loop in (
    'for action in self.heading_actions:',
    'dirty_duplicate.addAction(self.dirty_duplicate_actions[key])',
    'dirty_external.addAction(self.dirty_external_actions[key])',
):
    assert required_loop in menus, required_loop

# Item 27B: menu-backed shortcut membership comes recursively from the live AppMenu.
catalog = method_source("_shortcut_catalog")
for required in (
    'def collect(menu: QMenu)',
    'for action in menu.actions()',
    'submenu = action.menu()',
    'entries.extend(collect(submenu))',
    'action.shortcut().toString(',
    'QKeySequence.SequenceFormat.NativeText',
    '"File": collect(self.file_menu)',
    '"Edit": collect(self.edit_menu)',
    '"Markdown": collect(self.markdown_menu)',
    '"Insert": collect(self.insert_menu)',
    '"View": collect(self.view_menu)',
    '"Settings": collect(self.settings_menu)',
    '"Help": collect(self.help_menu)',
):
    assert required in catalog, required

# Menu-backed QActions must not be mirrored manually in the catalogue anymore.
for forbidden in (
    'self.new_action', 'self.save_action', 'self.rename_file_action',
    'self.undo_action', 'self.comment_action', 'self.bold_action',
    'self.image_action', 'self.fullscreen_action', 'self.theme_light_action',
    'self.documentation_action', 'self.shortcuts_action',
):
    assert forbidden not in catalog, forbidden

# The explicit exception set is intentionally tiny and contains only shortcuts
# that have no AppMenu QAction representation.
for required in (
    '("Find Next", self.find_next_action)',
    '("Find Previous", self.find_previous_action)',
    '("Close Find/Replace", self.dismiss_find_action)',
    '("Toggle Overwrite Mode", "Insert")',
    '("Next Tabbed Tab", self.next_tabbed_tab_action)',
    '("Previous Tabbed Tab", self.previous_tabbed_tab_action)',
):
    assert required in catalog, required

exception_action_attrs = {
    node.attr for node in ast.walk(method("_shortcut_catalog"))
    if isinstance(node, ast.Attribute)
    and isinstance(node.value, ast.Name)
    and node.value.id == "self"
    and node.attr.endswith("_action")
}
assert exception_action_attrs == {
    "find_next_action", "find_previous_action", "dismiss_find_action",
    "next_tabbed_tab_action", "previous_tabbed_tab_action",
}, exception_action_attrs

# The 0.1.7 fuzzy matcher remains the dialog filtering mechanism.
shortcuts = method_source("show_shortcuts")
assert '_shortcut_query_matches(query, shortcut_tokens)' in shortcuts
assert 'category.addItems(["All", *catalog.keys()])' in shortcuts
assert 'catalog = self._shortcut_catalog()' in shortcuts

# No shortcut assignment, toolbar inventory, icon mapping, theme implementation,
# editor/file/settings code or Delete lifecycle may change in this release.
PROTECTED_METHODS = {
    "_create_actions": "8c368be6f4e6c9abace77be58829798604d3f44d7a346080bfb8622e6f580725",
    "_create_tabbed_toolbar": "7ddad5c5378eb289d43618179f381689046329f3699f9e8d21cb67fe6dd6da39",
    "_classic_toolbar_catalog": "c708102c630d78d734447da040da9578257e1812c5014c567e74dbe170408723",
    "_create_classic_toolbar": "8e373a83fe1127bee2f15a81f6812f70f8b5941b7a899708cb4a2b56589a2170",
    "rebuild_classic_toolbar": "caeaf186f9031f63868e9bec5fa21d1d71ffe6e9a8a701acc4ed1dd2b49504d4",
    "_refresh_action_icons": "28e18450ab874cd81caf4b01d4ee433c7901d1a16cbe815e8bc9f18ef772c310",
    "set_theme": "8584a1f40a77b7c2c03b0e2a9b63a2e2d685d50a378ed366d57fff9bd65c3225",
    "_apply_editor_appearance": "314fdff639b6258ed97448091561ae129eec3817de238b88d9eda50252101b37",
    "delete_file": "3461c4e858ac0132244044054b07655211c4aa2574d937d9bf3ac0aede958746",
}
for name, expected in PROTECTED_METHODS.items():
    actual = method_hash(name)
    assert actual == expected, (name, actual, expected)

PROTECTED_FILES = {
    "source_editor.py": "0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py": "e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py": "b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "settings_io.py": "9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
    "legacy_ricopad.py": "2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
}
for rel, expected in PROTECTED_FILES.items():
    actual = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    assert actual == expected, (rel, actual, expected)

# 0.1.8 theme/default contract and 0.1.9 Plus icon family remain intact.
assert 'self.theme = theme_override or str(self.settings.get("theme", "light"))' in APP
assert 'self.editor_canvas_light = bool(self.settings.get("editor_canvas_light", True))' in APP

def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.glob("*.png")):
        h.update(p.name.encode("utf-8") + b"\0" + p.read_bytes())
    return h.hexdigest()

ICON_ROOT = ROOT / "assets" / "toolbar-icons"
assert len(list((ICON_ROOT / "light").glob("*.png"))) == 121
assert len(list((ICON_ROOT / "dark").glob("*.png"))) == 121
assert tree_hash(ICON_ROOT / "light") == "460c0c1d6b625a43fa76efb84178b4baf2c5faef2727c6f12e226101fd863dd9"
assert tree_hash(ICON_ROOT / "dark") == "32700ede0da30ebe1f2f67e090c29d50751c9bf42978f22235abc8ed637dc700"

print("Markopad 0.1.10 AppMenu/live-shortcut-inventory contract passed.")
