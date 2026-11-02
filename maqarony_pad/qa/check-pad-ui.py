#!/usr/bin/env python3
"""Dependency-light audit of MaqaronyPad 0.3.3 Pad-family UI/privacy conventions."""
from __future__ import annotations
import ast
import hashlib
import struct
from pathlib import Path

from source_contract import contract_text
ROOT = Path(__file__).resolve().parents[1]
source = contract_text(ROOT)
printing_source=(ROOT / "widgets/mwpyn/editor_printing.py").read_text(encoding="utf-8")
command_source=(ROOT / "widgets/editor_commands_appearance.py").read_text(encoding="utf-8")
lifecycle_source=(ROOT / "widgets/mwpyn/editor_lifecycle.py").read_text(encoding="utf-8")
tree = ast.parse(source)
command_tree=ast.parse(command_source)
printing_tree=ast.parse(printing_source)
lifecycle_tree=ast.parse(lifecycle_source)

# Dialog-title convention: convenience dialogs use "Dialog — MaqaronyPad".
static_title_arg = {
    ("QMessageBox", "question"): 1,
    ("QMessageBox", "warning"): 1,
    ("QMessageBox", "critical"): 1,
    ("QMessageBox", "information"): 1,
    ("QFileDialog", "getOpenFileName"): 1,
    ("QFileDialog", "getSaveFileName"): 1,
    ("QInputDialog", "getText"): 1,
    ("QInputDialog", "getItem"): 1,
    ("QInputDialog", "getInt"): 1,
    ("QFontDialog", "getFont"): 2,
}
checked = 0
for node in (item for one_tree in (tree,printing_tree,command_tree,lifecycle_tree) for item in ast.walk(one_tree)):
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        continue
    owner = node.func.value.id if isinstance(node.func.value, ast.Name) else None
    key = (owner, node.func.attr)
    if key not in static_title_arg:
        continue
    idx = static_title_arg[key]
    assert len(node.args) > idx
    title = node.args[idx]
    assert isinstance(title, ast.Call) and isinstance(title.func, ast.Name) and title.func.id == "dialog_title", (
        f"Pad title convention missing for {owner}.{node.func.attr} at line {node.lineno}"
    )
    checked += 1
assert checked >= 25, checked
source += "\n" + printing_source + "\n" + (ROOT / "widgets/mwpyn/editor_preferences.py").read_text(encoding="utf-8") + "\n" + (ROOT / "widgets/editor_ribbon_retro.py").read_text(encoding="utf-8") + "\n" + command_source + "\n" + lifecycle_source
assert 'dialog.setWindowTitle(dialog_title("About"))' in source
assert 'dialog.setWindowTitle(dialog_title("Documentation"))' in source
assert 'dialog.setWindowTitle(dialog_title("Customise Classic Bar"))' in source
assert 'dialog.setWindowTitle(dialog_title("Table"))' in source
assert 'dialog.setWindowTitle(dialog_title("Print"))' in source
assert 'lock_suffix = " — Locked Mode" if self.editor.isReadOnly() else ""' in source
assert 'self.setWindowTitle(f"{\'*\' if modified else \'\'}{name} — {APP_NAME}{lock_suffix}")' in source

# Privacy: no current UI or state records file history.
assert "Open Recent" not in source and "open_recent" not in source.lower() and "RECENT_LIMIT" not in source
assert 'self.settings.pop("recent_files", None)' in source

# 0.0.2 terminology and migration.
assert 'self.toolbar_menu = view.addMenu("Editor Toolbar")' in source
assert 'self.tabbed_mode_action = self._action("Modern (default)"' in source
assert 'self.classic_mode_action = self._action("Classic"' in source
assert 'self.customize_classic_action = self._action("Customise Classic Bar…"' in source
assert 'self.editor_layout_menu_action = layout.menuAction()' in source
assert 'self.editor_toolbar_menu_action = self.toolbar_menu.menuAction()' in source
assert '"editor_layout_menu_action":"toolbar-tabbed", "editor_toolbar_menu_action":"toolbar-classic"' in source
assert 'action.setIcon(QIcon())' in source
assert '("View", "editor_toolbar", "Editor Toolbar", self.editor_toolbar_menu_action)' in source
assert '("View", "customize_classic", "Customise Classic Bar...", self.customize_classic_action)' not in source
assert 'self.toolbar_mode = stored_toolbar if stored_toolbar in {"tabbed", "classic"} else "tabbed"' in source
assert '"toolbar": self.toolbar_mode' in source
assert '"classic_toolbar_items": list(self.classic_toolbar_items)' in source
assert '"tabbed_collapsed": bool(getattr(self, "_tabbed_collapsed", False))' in source
assert 'APP_TAGLINE = "Friendly. Fast. Focused."' in source
assert 'self.settings.pop("external_editor", None)' in source
# Old names may exist only in migration literals, never as current action/menu labels.
for forbidden in ('self._action("Ribbon"', 'self._action("Retro"', 'view.addMenu("Interface")', 'self._action("Button Labels"'):
    assert forbidden not in source, forbidden
assert 'show_button_labels' not in source and 'toggle_button_labels' not in source

# Tabbed is one line per tab and uses QToolBar's native extension/overflow.
assert 'class RibbonScrollArea' not in source
assert 'self.tabbed_toolbars: list[QToolBar]' in source
assert 'toolbar = QToolBar(name, page)' in source
assert 'toolbar.setMovable(False)' in source and 'toolbar.setFloatable(False)' in source
assert 'toolbar.setIconSize(QSize(36, 36))' in source
assert 'toolbar.setMinimumHeight(56)' in source and 'toolbar.setMaximumHeight(56)' in source
assert 'Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop' in source
assert 'def _tabbed_separator(toolbar: QToolBar) -> None:' in source
assert 'toolbar.addSeparator()' in source
assert 'maqarony_padRibbonSection' not in source
start = source.index('def _create_tabbed_toolbar')
end = source.index('def _classic_toolbar_catalog', start)
tabbed = source[start:end]
assert 'setHorizontalScrollBarPolicy' not in tabbed
assert '[self.editor_toolbar_menu_action]' in tabbed
assert '[self.toolbar_style_toggle_action, self.customize_classic_action]' not in tabbed
assert 'self.tabbed_tabs.tabText(i) == "Home"' in tabbed
assert 'self.tabbed_tabs.setCurrentIndex(home_index)' in tabbed

# Heading is one Tabbed dropdown; Classic retains individual headings.
assert 'self.heading_tabbed_action = QAction("Heading", self)' in source
assert 'for action in self.heading_actions:' in source
assert 'self.heading_tabbed_action.setMenu(self.heading_tabbed_menu)' in source
assert '[self.heading_tabbed_action]' in tabbed
classic_start = source.index('def _classic_toolbar_catalog')
classic_end = source.index('def _create_classic_toolbar', classic_start)
classic = source[classic_start:classic_end]
assert 'self.heading_actions' in classic

# Exact shared button geometry, icon-only style and bordered desktop decoration.
assert 'button.setFixedSize(52, 52)' in source
assert 'button.setIconSize(QSize(36, 36))' in source
assert 'button.setAutoRaise(False)' in source
assert 'button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)' in source
assert 'ToolButtonTextUnderIcon' not in source

# Reviewed Edit/View menu order and labels.
menu_start = source.index('def _create_menus')
menu_end = source.index('def _apply_editor_appearance', menu_start)
menus = source[menu_start:menu_end]
for required in (
    'more = self.file_menu.addMenu("More Actions")', 'markdown.addMenu("Heading")', 'insert.addMenu("Link")',
    'zoom = view.addMenu("Editor Zoom")', 'layout = view.addMenu("Editor Layout")',
    'self.toolbar_menu = view.addMenu("Editor Toolbar")', 'more_settings = view.addMenu("Editor Miscellaneous")',
    'theme_menu = settings.addMenu("App Theme")', 'behaviour = settings.addMenu("App Drag-and-Drop")',
):
    assert required in menus, required
for forbidden in ('view.addMenu("Theme")', 'view.addMenu("Behaviour")', 'view.addMenu("Overall Theme")'):
    assert forbidden not in menus, forbidden
edit_start = menus.index('self.edit_menu = bar.addMenu("&Edit")')
markdown_start = menus.index('self.markdown_menu = bar.addMenu("&Markdown")')
edit_block = menus[edit_start:markdown_start]
edit_order = [
    'self.undo_action', 'self.redo_action', 'self.cut_action', 'self.copy_action',
    'self.paste_action', 'self.paste_plain_action', 'self.delete_action',
    'self.duplicate_line_action', 'self.delete_line_action', 'self.select_all_action',
    'self.find_action', 'self.goto_action', 'self.replace_action',
]
positions = [edit_block.index(item) for item in edit_order]
assert positions == sorted(positions), positions
view_start = menus.index('self.view_menu = bar.addMenu("&View")')
help_start = menus.index('self.help_menu = bar.addMenu("&Help")')
view_block = menus[view_start:help_start]
view_order = [
    'self.fullscreen_action', 'self.status_bar_action', 'self.word_wrap_action',
    'self.line_numbers_action', 'self.editor_canvas_theme_action', 'self.view_only_action',
    'layout = view.addMenu("Editor Layout")', 'self.toolbar_menu = view.addMenu("Editor Toolbar")',
    'zoom = view.addMenu("Editor Zoom")', 'more_settings = view.addMenu("Editor Miscellaneous")',
]
positions = [view_block.index(item) for item in view_order]
assert positions == sorted(positions), positions
assert 'more_settings.addAction(self.tab_width_action)' in view_block
assert 'more_settings.addSeparator()' in view_block
assert 'more_settings.addAction(self.editor_font_action)' in view_block
assert 'more_settings.addAction(self.display_font_action)' in view_block
assert 'zoom.addAction(self.zoom_in_action); zoom.addAction(self.zoom_out_action); zoom.addSeparator(); zoom.addAction(self.zoom_reset_action)' in view_block
assert 'theme_menu.addAction(self.theme_light_action); theme_menu.addAction(self.theme_dark_action); theme_menu.addAction(self.theme_system_action)' in menus

# Reviewed labels, registered keybindings and menu-only syntax hints.
for text in (
    '"Quote Block\\t>"', '"Code Block\\t```"',
    '"Image Reference…"', '"Table…"', '"Date and Time"', '"Date Only"', '"Time Only"',
    '"Symbol…"', '"Preview Font..."', '"Raise an Issue"', '"Save and Exit"',
    '"Duplicate Line / Selection"', '"Go To Line..."', '"Modern (default)"', '"Tab Width..."',
    '"Source Font..."', '"Dark Editor"', '"Opens on Active Window"', '"Opens on New Window"',
):
    assert text in source, text
shortcut_specs = (
    'self.external_editor_action = self._action("Open in External Editor", self.open_external_editor, "Ctrl+Shift+E")',
    'self.rename_file_action = self._action("Rename…", self.rename_file, "F2")',
    'self.duplicate_file_action = self._action("Duplicate File", self.duplicate_file, "Ctrl+Shift+D")',
    'self.open_folder_action = self._action("Open Containing Folder", self.open_containing_folder, "Ctrl+Shift+O")',
    'self.redo_action = self._action("Redo", lambda: self.editor.redo(), "Ctrl+Y")',
    'self.replace_action = self._action("Find and Replace", lambda: self.toggle_find_panel(True), "Ctrl+H")',
    'self.find_next_action = self._action("Find Next", self.find_next, "F3")',
    'self.find_previous_action = self._action("Find Previous", self.find_previous, "Shift+F3")',
    'self.comment_action = self._action("Toggle Comment", lambda: self.editor.toggle_comment(), "Ctrl+/")',
    'self.bullet_action = self._action("Bullet List", lambda: self.editor.toggle_bullet_list(), "Ctrl+L")',
    'self.number_action = self._action("Numbered List", lambda: self.editor.toggle_numbered_list(), "Ctrl+Shift+L")',
    'self.task_action = self._action("Task List", lambda: self.editor.toggle_task_list())',
    'f"Ctrl+Shift+{level}"',
    'self.image_action = self._action("Image Reference…", self.insert_image, "Ctrl+Shift+I")',
    'self.table_action = self._action("Table…", self.insert_table, "Ctrl+Shift+T")',
    'self.rule_action = self._action("Horizontal Rule", lambda: self.editor.insert_horizontal_rule(), "Ctrl+Shift+H")',
    'self.export_pdf_action = self._action("Export PDF…", self.export_pdf, "Ctrl+Shift+P")',
    'self.indent_action = self._action("Indent", lambda: self.editor.indent_selection_or_insert_spaces(), "Ctrl+]")',
    'self.outdent_action = self._action("Outdent", lambda: self.editor.unindent_selection_or_line(), "Ctrl+[")',
    '"Ctrl+;"', '"Ctrl+:"', '"Shift+F5"',
    'self.view_only_action = self._action("Locked Mode", self.toggle_locked_mode, "F12", checkable=True)',
    '"Ctrl+1", checkable=True', '"Ctrl+2", checkable=True', '"Ctrl+3", checkable=True',
    '"Ctrl+Alt+Shift+W", checkable=True', '"Ctrl+Alt+Shift+L", checkable=True',
    '"Ctrl+Alt+Shift+S", checkable=True',
    'self.next_tabbed_tab_action = self._action("Next Tabbed Tab", lambda: self.cycle_tabbed_tab(1), "Ctrl+Tab")',
    'self.previous_tabbed_tab_action = self._action("Previous Tabbed Tab", lambda: self.cycle_tabbed_tab(-1), "Ctrl+Shift+Tab")',
    'self.quick_start_action = self._action("Quick Tour…", self.show_quick_tour, "Shift+F1")',
    'self.new_window_action = self._action("New Window", self.new_window, "Ctrl+Alt+Shift+N")',
    'self.editor_canvas_theme_action = self._action(',
    '"Dark Editor", self.toggle_editor_canvas_light, "Ctrl+Alt+Shift+E", checkable=True',
    'self.editor_font_action = self._action("Source Font...", self.choose_editor_font, "Ctrl+Shift+[")',
    'self.display_font_action = self._action("Preview Font...", self.choose_display_font, "Ctrl+Shift+]")',
)
for spec in shortcut_specs:
    assert spec in source, spec
# 0.2.7 current shortcut/menu contract: App Theme has no keyboard shortcuts;
# Editor Toolbar is a flyout, while Ctrl+Alt+Shift+T remains a shortcut-only mode switch.
assert 'self.theme_light_action = self._action("Light", lambda: self.set_theme("light"), checkable=True)' in source
assert 'self.theme_dark_action = self._action("Dark", lambda: self.set_theme("dark"), checkable=True)' in source
assert 'self.theme_system_action = self._action("System", lambda: self.set_theme("system"), checkable=True)' in source
assert 'Ctrl+Alt+Shift+1' not in source
assert 'Ctrl+Alt+Shift+2' not in source
assert 'Ctrl+Alt+Shift+3' not in source
assert 'self.tabbed_mode_action = self._action("Modern (default)", lambda: self.set_toolbar_mode("tabbed"), checkable=True)' in source
assert 'self.classic_mode_action = self._action("Classic", lambda: self.set_toolbar_mode("classic"), checkable=True)' in source
assert 'toolbar_style_toggle_action' not in source
assert 'def toggle_toolbar_style(self) -> None:' in source
assert '"Toggle Editor Toolbar", self.toggle_toolbar_style, "Ctrl+Alt+Shift+T"' in source
assert 'self.save_as_action = self._action("Save As…", self.save_as)' in source
assert 'self.task_action = self._action("Task List", lambda: self.editor.toggle_task_list())' in source
assert '[self.undo_action, self.redo_action, self.duplicate_line_action, self.delete_line_action, self.comment_action, self.find_action, self.goto_action, self.replace_action]' in source
file_start = menus.index('self.file_menu = bar.addMenu("&File")')
edit_start2 = menus.index('self.edit_menu = bar.addMenu("&Edit")')
file_block = menus[file_start:edit_start2]
assert file_block.index('self.file_menu.addAction(self.exit_action)') < file_block.index('self.file_menu.addAction(self.save_exit_action)')
assert 'def cycle_tabbed_tab(self, step: int) -> None:' in source
assert 'if self.toolbar_mode != "tabbed" or self.tabbed_tabs.count() <= 0:' in source
assert 'self.documentation_action = self._action("Documentation", self.show_documentation, QKeySequence.StandardKey.HelpContents)' in source
assert 'self.date_time_action = self._action("Date and Time"' in source and '"F5"' in source
assert 'self.dismiss_find_action = self._action("Close Find/Replace", self.hide_find_panel, "Esc")' in source
for removed in (
    'self.github_action = self._action("GitHub Repository", self.open_github_repository,',
    'self.issue_action = self._action("Raise an Issue", self.report_an_issue,',
    'self.about_action = self._action("About MaqaronyPad", self.show_about,',
):
    assert removed not in source, removed

# Hover tooltips surface actual QAction shortcuts; toolbar right-click exposes mode/customisation.
assert 'shortcut_text = action.shortcut().toString(QKeySequence.SequenceFormat.NativeText)' in source
assert 'action.setToolTip(f"{label} — {shortcut_text}" if shortcut_text else label)' in source
for required in (
    'def _show_toolbar_context_menu(self, global_pos) -> None:',
    'menu.addAction(self.tabbed_mode_action)', 'menu.addAction(self.classic_mode_action)',
    'menu.addAction(self.customize_classic_action)',
    'def _enable_toolbar_context_menu(self, widget: QWidget) -> None:',
    'Qt.ContextMenuPolicy.CustomContextMenu',
    'self._enable_toolbar_context_menu(toolbar)',
    'self._enable_toolbar_context_menu(self.classic_toolbar)',
    'self._enable_toolbar_context_menu(button)',
):
    assert required in source, required

# Dark Editor is checked exactly when the shared source/preview canvas is dark.
assert 'self.editor_canvas_theme_action.setChecked(not self.editor_canvas_light)' in source
assert 'self.editor_canvas_light = not bool(checked)' in source

# External Editor delegates the document to the desktop association, not an executable chooser.
ext_start = lifecycle_source.index('def open_external_editor')
ext_end = lifecycle_source.find('\n    def ', ext_start + 1)
ext_method = lifecycle_source[ext_start:ext_end if ext_end >= 0 else None]
assert 'QDesktopServices.openUrl(QUrl.fromLocalFile(str(target)))' in ext_method
assert '"Save Changes and Open"' in ext_method
assert '"Open Last Saved Version"' in ext_method
assert 'self._file_policy("dirty_external_action"' in ext_method
assert 'QFileDialog.getOpenFileName' not in ext_method
assert 'subprocess.Popen' not in ext_method

# Source/Preview appearance rules.
display_start = source.index('def choose_display_font')
display_end = source.index('def choose_editor_font', display_start)
display_method = source[display_start:display_end]
assert 'self.settings["preview_font"]' in display_method
assert 'editor_font_family' not in display_method and 'editor_font_size' not in display_method
assert 'dialog_title("Preview Font")' in display_method
assert 'self.preview.setPalette(preview_palette)' in source and 'self.preview.viewport().setPalette(preview_palette)' in source

# Tabbed collapse/reveal remains unchanged.
assert 'QEvent.Type.MouseButtonDblClick' in source and 'self.set_tabbed_collapsed(True)' in source
assert 'QEvent.Type.MouseButtonPress' in source and 'self.set_tabbed_collapsed(False)' in source

# Canonical Marko Plus command-icon family: paired 64x64 RGBA PNGs, no obsolete asset directory.
icon_root = ROOT / 'assets' / 'toolbar-icons'
assert icon_root.is_dir() and not (ROOT / 'assets' / 'ribbon-icons').exists()
sets = {}
for scheme in ('light', 'dark'):
    paths = sorted((icon_root / scheme).glob('*.png'))
    assert len(paths) == 122, (scheme, len(paths))
    sets[scheme] = {p.name for p in paths}
    for p in paths:
        data = p.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n', p
        width, height, bitdepth, color_type = struct.unpack('>IIBB', data[16:26])
        assert (width, height, bitdepth, color_type) == (64, 64, 8, 6), (p, width, height, bitdepth, color_type)
assert sets['light'] == sets['dark']
for required in ('new.png','open.png','save.png','task-list.png','source-only.png','source-preview.png','preview-only.png','toolbar-tabbed.png','toolbar-classic.png','about.png','app-theme.png','heading-group.png','code-group.png','link-group.png','system-theme.png','dark-mode.png','light-theme.png','comment-toggle.png'):
    assert required in sets['light'], required
    a=(icon_root/'light'/required).read_bytes(); b=(icon_root/'dark'/required).read_bytes()
    assert hashlib.sha256(a).digest() != hashlib.sha256(b).digest(), required

# Existing App Theme actions now participate in the canonical Marko Plus icon family.
icon_map_start = source.index('mapping = {')
icon_map_end = source.index('for attr, name in mapping.items()', icon_map_start)
icon_map = source[icon_map_start:icon_map_end]
for required in ('"theme_system_action":"system-theme"', '"theme_dark_action":"dark-mode"', '"theme_light_action":"light-theme"'):
    assert required in icon_map, required

# AppImage-only overflow enhancement must not alter Portable/source toolbar styling.
assert 'return bool(os.environ.get("APPIMAGE"))' in source
assert 'toolbar.findChild(QToolButton, "qt_toolbar_ext_button")' in source
assert 'extension.setText("›")' in source
assert 'extension.setMinimumWidth(28)' in source
assert 'QTimer.singleShot(0, self._refresh_appimage_overflow_buttons)' in source
overflow_start = source.index('def _style_appimage_overflow_button')
overflow_end = source.index('def _refresh_appimage_overflow_buttons', overflow_start)
overflow = source[overflow_start:overflow_end]
assert 'if not self._is_appimage_runtime()' in overflow and 'return' in overflow


# r7 Keyboard Shortcuts: current Ricopad two-column table plus MaqaronyPad search/tab filter.
assert 'self.shortcuts_dialog: QDialog | None = None' in source
catalog_start = source.index('def _shortcut_catalog')
shortcuts_start = source.index('def show_shortcuts', catalog_start)
shortcuts_end = source.index('def show_documentation', shortcuts_start)
catalog_block = source[catalog_start:shortcuts_start]
shortcuts = source[shortcuts_start:shortcuts_end]
for required in (
    'dialog.setWindowTitle(dialog_title("Keyboard Shortcuts"))',
    'dialog.setModal(False)',
    'dialog.resize(700, 560)',
    'search.setPlaceholderText("Search commands or shortcuts")',
    'search.setClearButtonEnabled(True)',
    'category.setAccessibleName("Shortcut menu")',
    'QLabel("Menu:", dialog)',
    '_shortcut_query_matches(query, shortcut_tokens)',
    'category.addItems(["All", *catalog.keys()])',
    'category.setCurrentIndex(0)',
    'table = QTableWidget(len(rows), 2, dialog)',
    'table.setHorizontalHeaderLabels(["Command", "Shortcut"])',
    'table.horizontalHeader().setStretchLastSection(True)',
    'table.verticalHeader().setVisible(False)',
    'table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)',
    'table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)',
    'QTableWidgetItem(label)',
    'QTableWidgetItem(shortcut)',
    'table.resizeColumnsToContents()',
    'if not shortcut or not clean_label',
    'table.setRowHidden(row_index, not row_visible)',
    'search.textChanged.connect(apply_filter)',
    'category.currentTextChanged.connect(apply_filter)',
    'QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, dialog)',
    'dialog.finished.connect(lambda _result: setattr(self, "shortcuts_dialog", None))',
):
    assert required in shortcuts, required
for required in (
    'def collect(menu: QMenu)',
    'entries.extend(collect(submenu))',
    '"File": collect(self.file_menu)',
    '"Edit": collect(self.edit_menu)',
    '"Markdown": collect(self.markdown_menu)',
    '"Insert": collect(self.insert_menu)',
    '"View": collect(self.view_menu)',
    '"Settings": collect(self.settings_menu)',
    '"Help": collect(self.help_menu)',
):
    assert required in catalog_block, required
for forbidden in (
    'self.new_action', 'self.save_action', 'self.bold_action',
    'self.image_action', 'self.fullscreen_action', 'self.theme_light_action',
    'self.documentation_action',
):
    assert forbidden not in catalog_block, forbidden
assert 'group = QGroupBox(tab_name, page)' not in shortcuts
assert 'QScrollArea(dialog)' not in shortcuts
assert 'QMessageBox.information(self, dialog_title("Keyboard Shortcuts")' not in shortcuts

# Help ordering/identity.
assert 'GITHUB_URL = "https://github.com/brunonlinespace/maqaronypad"' in source
help_start = menus.index('self.help_menu = bar.addMenu("&Help")')
help_block = menus[help_start:]
ordered = ['self.documentation_action', 'self.quick_start_action', 'self.shortcuts_action', 'self.github_action', 'self.issue_action', 'self.about_action']
pos = [help_block.index(item) for item in ordered]
assert pos == sorted(pos), pos

# Status bar intentionally omits redundant file format.
status_start = source.index('def update_status')
status_end = source.index('def _handle_dropped_files', status_start)
assert 'Markdown  ' not in source[status_start:status_end]

print("MaqaronyPad 0.3.3 Pad-family UI convention audit passed.")
