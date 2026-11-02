#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.0 Item 28 Tabbed command-surface contract."""
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


req('APP_VERSION = "0.2.0"' in APP, "0.2.0 identity missing")

# Marko Plus 0.4.6 shared Markdown-facing Ribbon inventory is the authority.
expected_pages = (
    '"Home": [\n'
    '                [self.cut_action, self.copy_action, self.paste_action, self.paste_markdown_action, self.delete_action, self.select_all_action],\n'
    '                [self.undo_action, self.redo_action, self.duplicate_line_action, self.delete_line_action, self.find_action, self.goto_action, self.replace_action],\n'
    '                [self.bold_action, self.italic_action, self.strike_action, self.code_tabbed_action],\n'
    '                [self.bullet_action, self.number_action, self.task_action, self.quote_action, self.indent_action, self.outdent_action],\n'
    '                [self.heading_tabbed_action],\n'
    '            ],',
    '"Insert": [\n'
    '                [self.image_action, self.link_action, self.edit_link_action, self.remove_link_action],\n'
    '                [self.table_action],\n'
    '                [self.date_time_action, self.date_action, self.time_action],\n'
    '                [self.rule_action, self.symbol_action],\n'
    '            ],',
    '"View": [\n'
    '                [self.fullscreen_action, self.status_bar_action],\n'
    '                [self.word_wrap_action, self.line_numbers_action, self.editor_canvas_theme_action, self.view_only_action],\n'
    '                [self.source_only_action, self.split_action, self.preview_only_action],\n'
    '                [self.tabbed_mode_action, self.classic_mode_action, self.customize_classic_action],\n'
    '                [self.zoom_in_action, self.zoom_out_action, self.zoom_reset_action],\n'
    '                [self.tab_width_action, self.editor_font_action, self.display_font_action],\n'
    '            ],',
    '"Settings": [\n'
    '                [self.theme_tabbed_action],\n'
    '                [self.drop_tabbed_action],\n'
    '                [self.dirty_duplicate_tabbed_action, self.dirty_external_tabbed_action],\n'
    '            ],',
)
for fragment in expected_pages:
    req(fragment in APP, f"0.2.0 Tabbed layout missing exact block: {fragment.splitlines()[0]}")

# Missing controls identified by the audit are now present in Tabbed.
for action in (
    "self.select_all_action", "self.duplicate_line_action", "self.delete_line_action",
    "self.fullscreen_action", "self.tab_width_action",
):
    req(action in method_source("_create_tabbed_toolbar"), f"Tabbed still omits {action}")

# Plus-style grouped Code action reuses the canonical underlying Markdown actions.
for fragment in (
    'self.code_tabbed_action = QAction("Code", self)',
    'self.code_tabbed_menu.addAction(self.inline_code_action)',
    'self.code_tabbed_menu.addAction(self.code_fence_action)',
    '"code_tabbed_action":"code-group"',
):
    req(fragment in APP, f"Code flyout convergence missing: {fragment}")
req('self.code_fence_action' not in expected_pages[1], "Code Block must not remain directly on Insert")

# Heading flyout now matches Plus by including Normal Paragraph plus H1-H6.
req('for action in self.heading_actions:\n            self.heading_tabbed_menu.addAction(action)' in APP,
    "Heading flyout does not include the complete Plus heading inventory")

# Tabbed Settings must reuse the real AppMenu QMenu menuActions, never duplicate radio state.
settings_contract = (
    'self.theme_tabbed_action = theme_menu.menuAction()',
    'self.drop_tabbed_action = behaviour.menuAction()',
    'dirty_duplicate = settings.addMenu("Duplicate File with Unsaved Changes")',
    'self.dirty_duplicate_tabbed_action = dirty_duplicate.menuAction()',
    'self.dirty_external_tabbed_action = dirty_external.menuAction()',
    '"theme_tabbed_action":"app-theme"',
    '"drop_tabbed_action":"app-drag-and-drop"',
    '"dirty_duplicate_tabbed_action":"dirty-duplicate-policy"',
    '"dirty_external_tabbed_action":"dirty-external-policy"',
)
for fragment in settings_contract:
    req(fragment in APP, f"Settings flyout convergence missing: {fragment}")

# Match Plus flyout mechanics for every menu-backed Tabbed QAction.
req('if tabbed and action is not None and action.menu() is not None:' in APP,
    "Tabbed menu-backed actions do not use the generic Plus flyout path")
req('button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)' in APP,
    "Tabbed menu-backed action InstantPopup missing")

# Explicit Plus-only shell exclusions: standalone Pad does not gain workspace controls.
tabbed = method_source("_create_tabbed_toolbar")
for forbidden in (
    "sidebar_action", "file_header_action", "collapsed_mode_action", "list_action", "grid_action",
    "left_sidebar_action", "right_sidebar_action", "launch_dashboard_action", "launch_last_file_action",
    "tabs_enabled_action", "tabs_disabled_action", "workspace_tabbed_action", "import_file_action",
    "open_external_file_action",
):
    req(forbidden not in tabbed, f"Plus-only workspace control leaked into Markopad Tabbed: {forbidden}")

# Item 29 remains future work: Classic inventory/building is byte-for-byte method-stable from 0.1.10.
protected_methods = {
    "_classic_toolbar_catalog": "2ed54b8471fe340724457c791f948c705d0eb5ff12ef5e9c77b9061be424d058",
    "_create_classic_toolbar": "968daca6120473ccacfa77242fa277c40206cada15ad34e29c5b5829e89b2289",
    "rebuild_classic_toolbar": "f3847c8facc45a1f44c35927df6b165d1a2541f8c1540d19ab607b0633ea7e93",
    "_create_status_bar": "5a4577f3e84ef0afc265b3777964ffda19eb345df8b79916f35a9292c3e60434",
    "_shortcut_catalog": "b0011bedd0f4d54f74ae29b71f58be88fb6dddf0ebfcb51211ec9ee0660e1004",
    "delete_file": "8c03f4ad2ae9a8e2c0144ae5b9910f6d784cde108a2f7d9d00f47209cc2ecf74",
    "save_as": "d667d51daf2d2b8ce7346c29bf36c23b1df8b17f8c6b22eaf189fd2234fde300",
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

print("Markopad 0.2.0 Tabbed command-surface convergence contract passed.")
