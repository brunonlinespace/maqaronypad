#!/usr/bin/env python3
"""Static callback/architecture audit for MaqaronyPad 0.3.4 without PyQt6."""
from __future__ import annotations
import ast
from pathlib import Path

from source_contract import contract_text
ROOT = Path(__file__).resolve().parents[1]
source = contract_text(ROOT)
tree = ast.parse(source)
window = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MaqaronyPadWindow")
methods = {node.name for node in window.body if isinstance(node, ast.FunctionDef)}
view_source = (ROOT / "widgets/window_search_view.py").read_text(encoding="utf-8")
view_tree = ast.parse(view_source)
view = next(node for node in view_tree.body if isinstance(node, ast.ClassDef) and node.name == "WindowSearchViewMixin")
view_methods = {node.name for node in view.body if isinstance(node, ast.FunctionDef)}
assert not (view_methods & methods), "MRO would shadow extracted search/view method"
methods |= view_methods
printing_source=(ROOT / "widgets/mwpyn/editor_printing.py").read_text(encoding="utf-8")
printing_tree=ast.parse(printing_source)
printing=next(node for node in printing_tree.body if isinstance(node,ast.ClassDef) and node.name=="EditorPrintingMixin")
printing_methods={node.name for node in printing.body if isinstance(node,ast.FunctionDef)}
assert not (printing_methods & methods), "MRO would shadow extracted printing method"
methods |= printing_methods
preferences_source=(ROOT / "widgets/mwpyn/editor_preferences.py").read_text(encoding="utf-8")
preferences_tree=ast.parse(preferences_source)
preferences=next(node for node in preferences_tree.body if isinstance(node,ast.ClassDef) and node.name=="EditorPreferencesMixin")
preferences_methods={node.name for node in preferences.body if isinstance(node,ast.FunctionDef)}
assert not (preferences_methods & methods), "MRO would shadow extracted preference method"
methods |= preferences_methods

source += "\n" + view_source
retro_source=(ROOT / 'widgets/editor_ribbon_retro.py').read_text(encoding='utf-8')
retro_tree=ast.parse(retro_source)
retro=next(node for node in retro_tree.body if isinstance(node,ast.ClassDef) and node.name=='EditorRibbonRetroMixin')
retro_methods={node.name for node in retro.body if isinstance(node, ast.FunctionDef)}
assert not (retro_methods & methods), 'MRO shadows a moved Tabbed/Classic toolbar method'
methods |= retro_methods
source += "\n" + retro_source
command_source=(ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
command_tree=ast.parse(command_source)
command=next(node for node in command_tree.body if isinstance(node,ast.ClassDef) and node.name=='EditorCommandsAppearanceMixin')
command_methods={node.name for node in command.body if isinstance(node,ast.FunctionDef)}
assert not(command_methods & methods), 'MRO shadows a moved command or appearance method'
methods |= command_methods
source += '\n' + command_source
life_source=(ROOT/'widgets/mwpyn/editor_lifecycle.py').read_text(encoding='utf-8')
life_tree=ast.parse(life_source)
life=next(node for node in life_tree.body if isinstance(node,ast.ClassDef) and node.name=='EditorLifecycleMixin')
life_methods={node.name for node in life.body if isinstance(node,ast.FunctionDef)}
assert not(life_methods & methods), 'MRO shadows a lifecycle method'
methods |= life_methods
source += '\n' + life_source
required = {
    "new_document", "open_dialog", "save_document", "save_as", "save_and_exit",
    "new_window", "duplicate_file", "rename_file", "delete_file", "open_containing_folder",
    "open_external_editor", "show_properties", "print_document", "export_pdf",
    "paste", "delete_selection", "delete_current_line", "toggle_find_panel", "show_find_panel", "hide_find_panel",
    "clear_search_results", "refresh_search", "find_next", "find_previous", "replace_one", "replace_all", "goto_line",
    "insert_code_block", "insert_link", "edit_link", "remove_link", "insert_image",
    "insert_table", "insert_symbol", "set_view_mode", "toggle_word_wrap",
    "toggle_line_numbers", "toggle_locked_mode", "toggle_fullscreen", "choose_display_font", "choose_editor_font", "choose_tab_width",
    "set_zoom", "adjust_zoom_from_wheel", "cycle_tabbed_tab", "set_toolbar_mode", "set_theme", "set_drop_open_mode",
    "show_classic_toolbar_dialog", "rebuild_classic_toolbar", "set_tabbed_collapsed", "_focus_current_view",
    "toggle_editor_canvas_light", "_apply_editor_canvas_theme", "_apply_presentation_safely",
    "_restore_preferences", "persist_preferences",
    "_apply_preview_link_color", "_apply_preview_quote_effect", "_apply_toolbar_button_style",
    "show_quick_tour", "show_shortcuts", "show_documentation", "open_github_repository", "report_an_issue", "show_about",
    "handle_backing_path_event", "reload_external_change", "save_version_as",
    "_bind_document_watcher", "_clear_document_watcher", "_set_backing_state",
    "_external_change_action", "_confirm_close_missing_backing", "_sync_undo_redo_state",
}
missing = sorted(required - methods)
assert not missing, f"Missing MaqaronyPadWindow runtime methods: {missing}"
for removed in ("toggle_button_labels", "show_retro_toolbar_dialog", "set_ribbon_collapsed", "set_interface_mode"):
    assert removed not in methods, f"obsolete method remains: {removed}"
assert "QSplitter" in source and "MarkdownPreview" in source and "MarkopadSourceEditor" in source
assert 'mode not in {"source", "split", "preview"}' in source
assert 'self.view_mode != "preview"' in source
assert "QStackedWidget" not in source
assert "setAcceptRichText" not in source
assert not (ROOT / "markdown_codec.py").exists()
assert "open_recent" not in source.lower() and "Open Recent" not in source
assert 'self.source_only_action = self._action("Source Only", lambda: self.set_view_mode("source"), "Ctrl+1"' in source
assert 'self.split_action = self._action("Source + Preview", lambda: self.set_view_mode("split"), "Ctrl+2"' in source
assert 'self.preview_only_action = self._action("Preview Only", lambda: self.set_view_mode("preview"), "Ctrl+3"' in source
assert 'self.date_time_action = self._action("Date and Time"' in source and '"F5"' in source
assert 'APP_VERSION = "1.0.0-x13.0"' in source
print("MaqaronyPad 1.0.0-x13.0 runtime-method/architecture audit passed.")
