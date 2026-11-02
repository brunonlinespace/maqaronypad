#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.9 Audit Item 21 asset-family convergence contract."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "markopad.py"
APP = APP_PATH.read_text(encoding="utf-8")

assert 'APP_VERSION = "0.1.9"' in APP

# The entire icon family must be the retained Marko Plus 0.4.4 family, not a partial asset swap.
def tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.glob("*.png")):
        h.update(p.name.encode("utf-8") + b"\0" + p.read_bytes())
    return h.hexdigest()

ICON_ROOT = ROOT / "assets" / "toolbar-icons"
EXPECTED_TREE = {
    "light": "460c0c1d6b625a43fa76efb84178b4baf2c5faef2727c6f12e226101fd863dd9",
    "dark": "32700ede0da30ebe1f2f67e090c29d50751c9bf42978f22235abc8ed637dc700",
}
for scheme, expected in EXPECTED_TREE.items():
    files = sorted((ICON_ROOT / scheme).glob("*.png"))
    assert len(files) == 121, (scheme, len(files))
    assert tree_hash(ICON_ROOT / scheme) == expected, (scheme, tree_hash(ICON_ROOT / scheme), expected)
assert {p.name for p in (ICON_ROOT / "light").glob("*.png")} == {p.name for p in (ICON_ROOT / "dark").glob("*.png")}

# Parse the live mapping so semantic remaps remain explicit and reviewable.
tree = ast.parse(APP)
refresh = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_refresh_action_icons")
mapping_node = None
for stmt in refresh.body:
    if isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "mapping" for t in stmt.targets):
        mapping_node = stmt.value
        break
assert isinstance(mapping_node, ast.Dict)
mapping = ast.literal_eval(mapping_node)

EXPECTED_MAPPING = {
    "new_action":"new", "new_window_action":"new-window", "open_action":"open", "save_action":"save", "save_as_action":"save-as", "save_exit_action":"save-exit",
    "duplicate_file_action":"duplicate-file", "rename_file_action":"rename", "delete_file_action":"delete-file",
    "open_folder_action":"open-folder", "external_editor_action":"external-editor", "properties_action":"properties",
    "print_action":"print", "export_pdf_action":"export-pdf", "exit_action":"exit",
    "undo_action":"undo", "redo_action":"redo", "cut_action":"cut", "copy_action":"copy", "paste_action":"paste",
    "paste_markdown_action":"paste-markdown", "delete_action":"delete-text", "select_all_action":"select-all",
    "duplicate_line_action":"duplicate-line", "delete_line_action":"delete-line", "find_action":"find",
    "replace_action":"replace", "goto_action":"goto-line", "bold_action":"bold", "italic_action":"italic",
    "strike_action":"strikethrough", "quote_action":"quote-block", "bullet_action":"bullet-list",
    "number_action":"numbered-list", "task_action":"task-list", "indent_action":"indent", "outdent_action":"outdent",
    "inline_code_action":"inline-code", "code_fence_action":"code-block", "link_action":"insert-link",
    "edit_link_action":"edit-link", "remove_link_action":"remove-link", "rule_action":"horizontal-rule",
    "image_action":"insert-image", "table_action":"insert-table", "date_time_action":"date-time",
    "date_action":"insert-date", "time_action":"insert-time", "symbol_action":"symbols",
    "source_only_action":"source-only", "split_action":"source-preview", "preview_only_action":"preview-only",
    "view_only_action":"view-only", "word_wrap_action":"word-wrap", "line_numbers_action":"line-numbers",
    "status_bar_action":"status-bar", "fullscreen_action":"full-screen", "zoom_in_action":"zoom-in", "zoom_out_action":"zoom-out", "zoom_reset_action":"zoom-reset",
    "tabbed_mode_action":"toolbar-tabbed", "classic_mode_action":"toolbar-classic",
    "customize_classic_action":"toolbar-classic", "drop_active_action":"drop-active", "drop_new_window_action":"drop-new-window",
    "editor_canvas_theme_action":"editor-canvas", "display_font_action":"font-dialog", "editor_font_action":"default-font",
    "heading_tabbed_action":"heading-group",
    "theme_system_action":"system-theme", "theme_dark_action":"dark-mode", "theme_light_action":"light-theme",
    "tab_width_action":"tab-width", "quick_start_action":"tutorial",
    "shortcuts_action":"shortcuts", "documentation_action":"documentation", "github_action":"github",
    "issue_action":"issue", "about_action":"about",
}
assert mapping == EXPECTED_MAPPING, (mapping, EXPECTED_MAPPING)
for asset in mapping.values():
    for scheme in ("light", "dark"):
        assert (ICON_ROOT / scheme / f"{asset}.png").is_file(), (scheme, asset)
for level in range(7):
    for scheme in ("light", "dark"):
        assert (ICON_ROOT / scheme / f"heading-{level}.png").is_file(), (scheme, level)

# Ensure the semantic remaps that motivated the release cannot silently regress.
for attr, asset in {
    "paste_markdown_action":"paste-markdown",
    "quote_action":"quote-block",
    "inline_code_action":"inline-code",
    "code_fence_action":"code-block",
    "edit_link_action":"edit-link",
    "remove_link_action":"remove-link",
    "heading_tabbed_action":"heading-group",
}.items():
    assert mapping[attr] == asset

# Asset-family convergence must not smuggle toolbar/menu/inventory changes into 0.1.9.
def function_hash(name: str) -> str:
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    segment = ast.get_source_segment(APP, node)
    assert segment is not None
    return hashlib.sha256(segment.encode("utf-8")).hexdigest()

PROTECTED_METHODS = {
    "_create_actions": "8c368be6f4e6c9abace77be58829798604d3f44d7a346080bfb8622e6f580725",
    "_create_menus": "84a57a51fdd31f0a011381757652cf401df7df44be8ac5cd74ccb8772e2316e4",
    "_create_tabbed_toolbar": "7ddad5c5378eb289d43618179f381689046329f3699f9e8d21cb67fe6dd6da39",
    "_classic_toolbar_catalog": "c708102c630d78d734447da040da9578257e1812c5014c567e74dbe170408723",
    "_create_classic_toolbar": "8e373a83fe1127bee2f15a81f6812f70f8b5941b7a899708cb4a2b56589a2170",
    "rebuild_classic_toolbar": "caeaf186f9031f63868e9bec5fa21d1d71ffe6e9a8a701acc4ed1dd2b49504d4",
    "_apply_toolbar_mode": "80995e83d62c2b68fa41e38804f3f59a43db463c81cf9da9cd5b3c9abe0f24c9",
}
for name, expected in PROTECTED_METHODS.items():
    assert function_hash(name) == expected, (name, function_hash(name), expected)

# Editor/file/settings implementations remain exactly the 0.1.8 protected baseline.
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

# Item 20 palette/default contract remains intact.
assert 'self.theme = theme_override or str(self.settings.get("theme", "light"))' in APP
assert 'self.editor_canvas_light = bool(self.settings.get("editor_canvas_light", True))' in APP

print("Markopad 0.1.9 icon-family convergence contract passed.")
