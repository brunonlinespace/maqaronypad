#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.8 Audit Item 20 theme/default parity contract."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "markopad.py"
APP = APP_PATH.read_text(encoding="utf-8")
TREE = ast.parse(APP, filename=str(APP_PATH))

assert 'APP_VERSION = "0.1.8"' in APP


def function_source(name: str) -> str:
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            source = ast.get_source_segment(APP, node)
            assert source is not None
            return source
    raise AssertionError(f"missing function/method: {name}")


def source_hash(name: str) -> str:
    return hashlib.sha256(function_source(name).encode("utf-8")).hexdigest()


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


# Item 20: fresh/default state follows the current Marko Plus contract.
assert 'self.theme = theme_override or str(self.settings.get("theme", "light"))' in APP
assert 'self.editor_canvas_light = bool(self.settings.get("editor_canvas_light", True))' in APP
assert 'theme = args.theme or str(settings.get("theme", "light")); apply_theme(app, theme)' in APP

# Existing explicit user choices remain authoritative and independently persisted.
assert '"theme": self.theme' in APP
assert '"editor_canvas_light": self.editor_canvas_light' in APP
assert 'self.settings.pop("theme"' not in APP
assert 'self.settings.pop("editor_canvas_light"' not in APP
assert source_hash("set_theme") == "8584a1f40a77b7c2c03b0e2a9b63a2e2d685d50a378ed366d57fff9bd65c3225"
assert source_hash("toggle_editor_canvas_light") == "77978e20c0c9c338ddc5c25bbf9bc4e58344634eb6b43140403844f31c15068a"
assert source_hash("_apply_editor_canvas_theme") == "a390d16035e91bbec650b7a2e07dcb3e2ed01d577f9b269816073652021a2c3d"

# Exact Marko Plus 0.4.4 Light application palette.
apply_theme = function_source("apply_theme")
light_palette = {
    "Window": "#D4D4D4",
    "WindowText": "#2A2A2A",
    "Base": "#F4F4F4",
    "AlternateBase": "#E4E4E4",
    "ToolTipBase": "#F4F4F4",
    "ToolTipText": "#2A2A2A",
    "Text": "#2A2A2A",
    "Button": "#E4E4E4",
    "ButtonText": "#2A2A2A",
    "Light": "#F4F4F4",
    "Midlight": "#D0D0D0",
    "Mid": "#B2B2B2",
    "Dark": "#767676",
    "Shadow": "#545454",
    "Highlight": "#0B8781",
    "HighlightedText": "#FFFFFF",
    "PlaceholderText": "#767676",
    "Link": "#0068A6",
    "LinkVisited": "#0068A6",
}
assert '# Marko-family Light application palette.' in apply_theme
assert 'palette = app.style().standardPalette()' in apply_theme
for role, colour in light_palette.items():
    snippet = f'palette.setColor(QPalette.ColorRole.{role}, QColor("{colour}"))'
    assert snippet in apply_theme, snippet
for stale in ("#F5F6F7", "#202124"):
    assert stale not in apply_theme, stale

# Dark application palette stays unchanged from 0.1.7/current Plus.
dark_palette = {
    "Window": "#202326",
    "WindowText": "#F1F3F4",
    "Base": "#151719",
    "AlternateBase": "#202326",
    "ToolTipBase": "#F1F3F4",
    "ToolTipText": "#101214",
    "Text": "#F1F3F4",
    "Button": "#292D31",
    "ButtonText": "#F1F3F4",
    "Highlight": "#158B86",
    "HighlightedText": "#FFFFFF",
    "PlaceholderText": "#8E969E",
}
for role, colour in dark_palette.items():
    snippet = f'palette.setColor(QPalette.ColorRole.{role}, QColor("{colour}"))'
    assert snippet in apply_theme, snippet

# 0.1.7 shortcut/fuzzy behavior and both toolbar presentations remain frozen.
protected_methods = {
    "_create_actions": "8c368be6f4e6c9abace77be58829798604d3f44d7a346080bfb8622e6f580725",
    "_shortcut_catalog": "d775168b294a688c419bbdea559ca5745e46ea078384727e3d0de9e757b12b54",
    "_create_menus": "84a57a51fdd31f0a011381757652cf401df7df44be8ac5cd74ccb8772e2316e4",
    "_create_tabbed_toolbar": "7ddad5c5378eb289d43618179f381689046329f3699f9e8d21cb67fe6dd6da39",
    "_create_classic_toolbar": "8e373a83fe1127bee2f15a81f6812f70f8b5941b7a899708cb4a2b56589a2170",
    "_refresh_action_icons": "05fefe02cdf63f969edb188ecfaffb3224cfb1f6bf82594bc5106a73dbf99362",
    "_restore_preferences": "ced8c83afac145b75f680875cc4601b5d89332d5721c9641fc4c9e3c48a73221",
    "_apply_editor_appearance": "314fdff639b6258ed97448091561ae129eec3817de238b88d9eda50252101b37",
    "persist_preferences": "a376865b4fa4344cced94f6a0ba6379ca5e7f797608de3a80fb72ab3c7e9695e",
    "toggle_locked_mode": "860fead83fb4045ebe6dd6dc1e47aef9e652265fdea1f366620d935f4f9e0864",
    "save_document": "b9f7c8ea705e882378536f8d7eaa39b3cf87e9d1a53387faf4827b2051d95ec4",
    "save_as": "cb1256a59b14e4bb08e15ec793455d0ef1188849013e686195bf3271f3759536",
    "rename_file": "b207112638cc043ee8e90119ef117c050d1937e7259f334f82b8605aa29d6bde",
    "delete_file": "3461c4e858ac0132244044054b07655211c4aa2574d937d9bf3ac0aede958746",
}
for name, expected in protected_methods.items():
    actual = source_hash(name)
    assert actual == expected, (name, actual, expected)

# Protected editor/file/settings modules and icon assets remain byte-identical to 0.1.7.
protected_files = {
    "source_editor.py": "0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py": "e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py": "b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "legacy_ricopad.py": "2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
    "settings_io.py": "9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
}
for name, expected in protected_files.items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert actual == expected, (name, actual, expected)
assert tree_hash(ROOT / "assets" / "toolbar-icons") == "58e8a5226e911b5fed81adcd896e8fb108b7a0aa972f04fdd63cb3c4e4ccdf51"

# Safer Markopad Delete and state-aware Undo/Redo remain intact.
assert '# Keep the live editor. It is now the only guaranteed surviving copy.' in APP
assert 'File deleted from disk; the open document is retained.' in APP
assert 'self.undo_action.setEnabled(mutable and document.isUndoAvailable())' in APP
assert 'self.redo_action.setEnabled(mutable and document.isRedoAvailable())' in APP

print("Markopad 0.1.8 theme/default parity contract passed.")
