#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.1 Item 28 Settings-tab corrective contract."""
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


req('APP_VERSION = "0.2.1"' in APP, "0.2.1 identity missing")

# Item 28 corrective: Settings must be flat for direct-choice groups and reserve
# flyouts only for the final two dirty-document policies.
settings_block = '''"Settings": [
                [self.theme_light_action, self.theme_dark_action, self.theme_system_action],
                [self.drop_active_action, self.drop_new_window_action],
                [self.dirty_duplicate_tabbed_action, self.dirty_external_tabbed_action],
            ],'''
req(settings_block in APP, "Settings tab is not flat/direct-choice in the approved order")
tabbed = method_source("_create_tabbed_toolbar")
for forbidden in ("self.theme_tabbed_action", "self.drop_tabbed_action"):
    req(forbidden not in tabbed, f"Settings tab still uses grouped flyout wrapper: {forbidden}")
for required in ("self.dirty_duplicate_tabbed_action", "self.dirty_external_tabbed_action"):
    req(required in tabbed, f"approved final policy flyout missing: {required}")

# Exact option provenance tooltips approved for Pad.
for tooltip in (
    'self.theme_light_action.setToolTip("App Theme — Light")',
    'self.theme_dark_action.setToolTip("App Theme — Dark")',
    'self.theme_system_action.setToolTip("App Theme — System")',
    'self.drop_active_action.setToolTip("App Drag-and-Drop — Opens on Active Window")',
    'self.drop_new_window_action.setToolTip("App Drag-and-Drop — Opens on New Window")',
):
    req(tooltip in APP, f"Settings option provenance tooltip missing: {tooltip}")

# The AppMenu remains hierarchical; only the Tabbed Settings presentation is flat.
menu_contract = method_source("_create_menus")
for fragment in (
    'theme_menu = settings.addMenu("App Theme")',
    'theme_menu.addAction(self.theme_light_action); theme_menu.addAction(self.theme_dark_action); theme_menu.addAction(self.theme_system_action)',
    'behaviour = settings.addMenu("App Drag-and-Drop")',
    'behaviour.addAction(self.drop_active_action); behaviour.addAction(self.drop_new_window_action)',
    'dirty_duplicate = settings.addMenu("Duplicate File with Unsaved Changes")',
    'dirty_external = settings.addMenu("Open Externally with Unsaved Changes")',
):
    req(fragment in menu_contract, f"AppMenu Settings contract changed unexpectedly: {fragment}")

# 0.2.0 Home/Insert/View convergence remains exactly present.
for fragment in (
    '"Home": [\n                [self.cut_action, self.copy_action, self.paste_action, self.paste_markdown_action, self.delete_action, self.select_all_action],\n                [self.undo_action, self.redo_action, self.duplicate_line_action, self.delete_line_action, self.find_action, self.goto_action, self.replace_action],\n                [self.bold_action, self.italic_action, self.strike_action, self.code_tabbed_action],\n                [self.bullet_action, self.number_action, self.task_action, self.quote_action, self.indent_action, self.outdent_action],\n                [self.heading_tabbed_action],\n            ],',
    '"Insert": [\n                [self.image_action, self.link_action, self.edit_link_action, self.remove_link_action],\n                [self.table_action],\n                [self.date_time_action, self.date_action, self.time_action],\n                [self.rule_action, self.symbol_action],\n            ],',
    '"View": [\n                [self.fullscreen_action, self.status_bar_action],\n                [self.word_wrap_action, self.line_numbers_action, self.editor_canvas_theme_action, self.view_only_action],\n                [self.source_only_action, self.split_action, self.preview_only_action],\n                [self.tabbed_mode_action, self.classic_mode_action, self.customize_classic_action],\n                [self.zoom_in_action, self.zoom_out_action, self.zoom_reset_action],\n                [self.tab_width_action, self.editor_font_action, self.display_font_action],\n            ],',
):
    req(fragment in APP, "0.2.0 shared Tabbed inventory/order regressed")

# Item 29 is still future work: Classic remains frozen at the 0.2.0 baseline.
protected_methods = {
    "_classic_toolbar_catalog": "2ed54b8471fe340724457c791f948c705d0eb5ff12ef5e9c77b9061be424d058",
    "_create_classic_toolbar": "968daca6120473ccacfa77242fa277c40206cada15ad34e29c5b5829e89b2289",
    "rebuild_classic_toolbar": "f3847c8facc45a1f44c35927df6b165d1a2541f8c1540d19ab607b0633ea7e93",
    "_create_status_bar": "5a4577f3e84ef0afc265b3777964ffda19eb345df8b79916f35a9292c3e60434",
    "_shortcut_catalog": "b0011bedd0f4d54f74ae29b71f58be88fb6dddf0ebfcb51211ec9ee0660e1004",
    "delete_file": "8c03f4ad2ae9a8e2c0144ae5b9910f6d784cde108a2f7d9d00f47209cc2ecf74",
    "save_as": "d667d51daf2d2b8ce7346c29bf36c23b1df8b17f8c6b22eaf189fd2234fde300",
    "paste_as_markdown": "30a2c19612c53b741dd0d76c09a46c36156148892a0d6d5ef87bd0c687f6696e",
    "_update_ui_state": "02019f300bac514f8786a1c61fbaa6e8f3dc7280caa52944dce12b0ad6c4a4ba",
}
for name, expected in protected_methods.items():
    req(sha_text(method_source(name)) == expected, f"out-of-scope protected method changed: {name}")

# Item 30 is investigation-only in this release: Paste behavior/action assignments are untouched.
for fragment in (
    'self.paste_action = self._action("Paste", lambda: self.editor.paste(), QKeySequence.StandardKey.Paste)',
    'self.paste_markdown_action = self._action("Paste as Markdown", self.paste_as_markdown, "Ctrl+Shift+V")',
):
    req(fragment in APP, f"Item 30 Paste behavior changed before investigation: {fragment}")

protected_files = {
    "source_editor.py": "0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py": "e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py": "b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "settings_io.py": "9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
    "legacy_ricopad.py": "2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
}
for name, expected in protected_files.items():
    req(sha_file(name) == expected, f"out-of-scope protected file changed: {name}")

print("Markopad 0.2.1 Settings-tab corrective convergence contract passed.")
