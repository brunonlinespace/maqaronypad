#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.7 Audit Items 19 + 27 regression contract."""
from __future__ import annotations

import ast
import hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "markopad.py"
APP = APP_PATH.read_text(encoding="utf-8")
TREE = ast.parse(APP, filename=str(APP_PATH))

assert 'APP_VERSION = "0.1.7"' in APP


def source_hash(name: str) -> str:
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            source = ast.get_source_segment(APP, node)
            assert source is not None
            return hashlib.sha256(source.encode("utf-8")).hexdigest()
    raise AssertionError(f"missing method: {name}")


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def action_shortcuts() -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    for node in ast.walk(TREE):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        value = node.value
        if not (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
            and isinstance(value, ast.Call)
            and isinstance(value.func, ast.Attribute)
            and value.func.attr == "_action"
        ):
            continue
        shortcut: str | None = None
        if len(value.args) >= 3:
            shortcut_node = value.args[2]
            if isinstance(shortcut_node, ast.Constant):
                shortcut = shortcut_node.value
            else:
                shortcut = ast.unparse(shortcut_node)
        result[target.attr] = shortcut
    return result


shortcuts = action_shortcuts()

# Item 19: common Marko-family commands follow current Marko Plus shortcut policy.
expected = {
    "new_action": "QKeySequence.StandardKey.New",
    "new_window_action": "Ctrl+Alt+Shift+N",
    "save_action": "QKeySequence.StandardKey.Save",
    "save_as_action": None,
    "save_exit_action": "Ctrl+Shift+Q",
    "duplicate_file_action": "Ctrl+Shift+D",
    "rename_file_action": "F2",
    "open_folder_action": "Ctrl+Shift+O",
    "external_editor_action": "Ctrl+Shift+E",
    "properties_action": "F4",
    "print_action": "QKeySequence.StandardKey.Print",
    "export_pdf_action": "Ctrl+Shift+P",
    "exit_action": "QKeySequence.StandardKey.Quit",
    "undo_action": "QKeySequence.StandardKey.Undo",
    "redo_action": "Ctrl+Y",
    "cut_action": "QKeySequence.StandardKey.Cut",
    "copy_action": "QKeySequence.StandardKey.Copy",
    "paste_action": "QKeySequence.StandardKey.Paste",
    "paste_markdown_action": "Ctrl+Shift+V",
    "delete_action": "Delete",
    "duplicate_line_action": "Ctrl+D",
    "delete_line_action": "Ctrl+Shift+K",
    "select_all_action": "QKeySequence.StandardKey.SelectAll",
    "comment_action": "Ctrl+/",
    "find_action": "QKeySequence.StandardKey.Find",
    "replace_action": "Ctrl+H",
    "find_next_action": "F3",
    "find_previous_action": "Shift+F3",
    "goto_action": "Ctrl+G",
    "dismiss_find_action": "Esc",
    "bold_action": "Ctrl+B",
    "italic_action": "Ctrl+I",
    "strike_action": "Ctrl+Shift+X",
    "bullet_action": "Ctrl+L",
    "number_action": "Ctrl+Shift+L",
    "task_action": None,
    "indent_action": "Ctrl+]",
    "outdent_action": "Ctrl+[",
    "inline_code_action": "Ctrl+`",
    "link_action": "Ctrl+K",
    "rule_action": "Ctrl+Shift+H",
    "image_action": "Ctrl+Shift+I",
    "table_action": "Ctrl+Shift+T",
    "date_time_action": "F5",
    "date_action": "Ctrl+;",
    "time_action": "Ctrl+:",
    "symbol_action": "Shift+F5",
    "source_only_action": "Ctrl+1",
    "split_action": "Ctrl+2",
    "preview_only_action": "Ctrl+3",
    "view_only_action": "F12",
    "word_wrap_action": "Ctrl+Alt+Shift+W",
    "line_numbers_action": "Ctrl+Alt+Shift+L",
    "status_bar_action": "Ctrl+Alt+Shift+S",
    "fullscreen_action": "F11",
    "zoom_in_action": "QKeySequence.StandardKey.ZoomIn",
    "zoom_out_action": "QKeySequence.StandardKey.ZoomOut",
    "zoom_reset_action": "Ctrl+0",
    "editor_canvas_theme_action": "Ctrl+Alt+Shift+E",
    "editor_font_action": "Ctrl+Shift+[",
    "display_font_action": "Ctrl+Shift+]",
    "documentation_action": "QKeySequence.StandardKey.HelpContents",
    "quick_start_action": "Shift+F1",
    "shortcuts_action": "Ctrl+Shift+/",
}
for name, value in expected.items():
    assert shortcuts.get(name) == value, (name, shortcuts.get(name), value)

# Standalone-only shortcut exceptions are preserved intentionally.
assert shortcuts.get("open_action") == "QKeySequence.StandardKey.Open"
assert shortcuts.get("tabbed_mode_action") == "Ctrl+Alt+Shift+1"
assert shortcuts.get("classic_mode_action") == "Ctrl+Alt+Shift+2"
assert shortcuts.get("next_tabbed_tab_action") == "Ctrl+Tab"
assert shortcuts.get("previous_tabbed_tab_action") == "Ctrl+Shift+Tab"

# No duplicate explicit string shortcuts were introduced.
owners: dict[str, list[str]] = defaultdict(list)
for name, value in shortcuts.items():
    if value and not value.startswith("QKeySequence.StandardKey."):
        owners[value.casefold()].append(name)
for sequence, names in owners.items():
    assert len(names) == 1, (sequence, names)

# Heading shortcuts remain the common Ctrl+Shift+0..6 family.
assert 'f"Ctrl+Shift+{level}"' in APP

# Item 27: live application-menu taxonomy drives the dialog.
assert 'def _shortcut_catalog(self) -> dict[str, list[tuple[str, QAction | str]]]:' in APP
for menu in ("File", "Edit", "Markdown", "Insert", "View", "Settings", "Help"):
    assert f'            "{menu}": [' in APP
assert 'category.addItems(["All", *catalog.keys()])' in APP
assert 'category.setAccessibleName("Shortcut menu")' in APP
assert 'QLabel("Menu:", dialog)' in APP
assert 'QLabel("Tab:", dialog)' not in APP

# Execute only dependency-free fuzzy helper code from the actual source.
module_nodes = [ast.Import(names=[ast.alias(name="re")])]
for node in ast.parse((ROOT / "widgets/shortcut_search.py").read_text()).body:
    if isinstance(node, ast.Assign):
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if any(name in {"_SHORTCUT_TOKEN_RE", "_SHORTCUT_TOKEN_ALIASES"} for name in names):
            module_nodes.append(node)
    elif isinstance(node, ast.FunctionDef) and node.name in {"_shortcut_tokens", "_shortcut_query_matches"}:
        module_nodes.append(node)
mini = ast.Module(body=module_nodes, type_ignores=[])
ast.fix_missing_locations(mini)
namespace: dict[str, object] = {}
exec(compile(mini, str(ROOT / "widgets/shortcut_search.py"), "exec"), namespace)
tokens = namespace["_shortcut_tokens"]("Ctrl+Alt+Shift+N")
match = namespace["_shortcut_query_matches"]
assert match("control shift n", tokens)
assert match("shift+ctrl+n", tokens)
assert match("ctl n", tokens)
assert match("alt ctrl", tokens)
assert not match("ctrl q", tokens)

# Protected runtime methods remain source-identical to 0.1.6.
protected_methods = {
    "_create_menus": "84a57a51fdd31f0a011381757652cf401df7df44be8ac5cd74ccb8772e2316e4",
    "_create_tabbed_toolbar": "7ddad5c5378eb289d43618179f381689046329f3699f9e8d21cb67fe6dd6da39",
    "_create_classic_toolbar": "8e373a83fe1127bee2f15a81f6812f70f8b5941b7a899708cb4a2b56589a2170",
    "delete_file": "3461c4e858ac0132244044054b07655211c4aa2574d937d9bf3ac0aede958746",
    "save_document": "b9f7c8ea705e882378536f8d7eaa39b3cf87e9d1a53387faf4827b2051d95ec4",
    "save_as": "cb1256a59b14e4bb08e15ec793455d0ef1188849013e686195bf3271f3759536",
    "rename_file": "b207112638cc043ee8e90119ef117c050d1937e7259f334f82b8605aa29d6bde",
    "set_theme": "8584a1f40a77b7c2c03b0e2a9b63a2e2d685d50a378ed366d57fff9bd65c3225",
    "_refresh_action_icons": "05fefe02cdf63f969edb188ecfaffb3224cfb1f6bf82594bc5106a73dbf99362",
    "_restore_preferences": "ced8c83afac145b75f680875cc4601b5d89332d5721c9641fc4c9e3c48a73221",
    "toggle_locked_mode": "860fead83fb4045ebe6dd6dc1e47aef9e652265fdea1f366620d935f4f9e0864",
}
for name, expected_hash in protected_methods.items():
    actual = source_hash(name)
    assert actual == expected_hash, (name, actual, expected_hash)

# Protected modules and current icon family are unchanged from 0.1.6.
protected_files = {
    "source_editor.py": "0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py": "e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py": "b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "legacy_ricopad.py": "2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
    "settings_io.py": "9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
}
for name, expected_hash in protected_files.items():
    actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
    assert actual == expected_hash, (name, actual, expected_hash)
assert tree_hash(ROOT / "assets" / "toolbar-icons") == "58e8a5226e911b5fed81adcd896e8fb108b7a0aa972f04fdd63cb3c4e4ccdf51"

# Carry forward safer Markopad Delete and Item 14 state-aware Undo/Redo.
assert '# Keep the live editor. It is now the only guaranteed surviving copy.' in APP
assert 'File deleted from disk; the open document is retained.' in APP
assert 'self.undo_action.setEnabled(mutable and document.isUndoAvailable())' in APP
assert 'self.redo_action.setEnabled(mutable and document.isRedoAvailable())' in APP

print("Markopad 0.1.7 shortcut parity/fuzzy inventory contract passed.")
