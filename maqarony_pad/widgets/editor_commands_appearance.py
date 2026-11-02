#!/usr/bin/env python3
"""Existing x8 command and appearance methods; definitions relocated unchanged."""
from __future__ import annotations

from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction, QActionGroup, QColor, QFont, QIcon, QKeySequence, QPalette
from PyQt6.QtWidgets import QApplication, QCheckBox, QDialog, QFontDialog, QGridLayout, QGroupBox, QInputDialog, QMenu

class EditorCommandsAppearanceMixin:

    def _action(self, text: str, slot=None, shortcut: str | QKeySequence | None = None, *, checkable=False) -> QAction:
        action = QAction(text, self)
        if slot is not None:
            action.triggered.connect(slot)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut) if isinstance(shortcut, str) else shortcut)
        action.setCheckable(checkable)
        label = text.replace("&", "").replace("…", "...").strip()
        shortcut_text = action.shortcut().toString(QKeySequence.SequenceFormat.NativeText)
        action.setToolTip(f"{label} — {shortcut_text}" if shortcut_text else label)
        return action

    def _create_actions(self) -> None:
        self.new_action = self._action("New", self.new_document, QKeySequence.StandardKey.New)
        self.new_window_action = self._action("New Window", self.new_window, "Ctrl+Alt+Shift+N")
        self.open_action = self._action("Open…", self.open_dialog, QKeySequence.StandardKey.Open)
        self.save_action = self._action("Save", self.save_document, QKeySequence.StandardKey.Save)
        self.save_as_action = self._action("Save As…", self.save_as)
        self.save_exit_action = self._action("Save and Exit", self.save_and_exit, "Ctrl+Shift+Q")
        self.duplicate_file_action = self._action("Duplicate File", self.duplicate_file, "Ctrl+Shift+D")
        self.rename_file_action = self._action("Rename…", self.rename_file, "F2")
        self.delete_file_action = self._action("Delete File", self.delete_file)
        self.open_folder_action = self._action("Open Containing Folder", self.open_containing_folder, "Ctrl+Shift+O")
        self.external_editor_action = self._action("Open in External Editor", self.open_external_editor, "Ctrl+Shift+E")
        self.properties_action = self._action("Properties", self.show_properties, "F4")
        self.print_action = self._action("Print…", self.print_document, QKeySequence.StandardKey.Print)
        self.export_pdf_action = self._action("Export PDF…", self.export_pdf, "Ctrl+Shift+P")
        self.exit_action = self._action("Exit", self.close, QKeySequence.StandardKey.Quit)

        self.undo_action = self._action("Undo", lambda: self.editor.undo(), QKeySequence.StandardKey.Undo)
        self.redo_action = self._action("Redo", lambda: self.editor.redo(), "Ctrl+Y")
        self.cut_action = self._action("Cut", lambda: self.editor.cut(), QKeySequence.StandardKey.Cut)
        self.copy_action = self._action("Copy", self._copy_active_text_surface, QKeySequence.StandardKey.Copy)
        self.paste_action = self._action("Paste", self.paste, QKeySequence.StandardKey.Paste)
        self.paste_plain_action = self._action("Paste as Plain Text", lambda: self.editor.paste(), "Ctrl+Shift+V")
        self.delete_action = self._action("Delete", self.delete_selection, "Delete")
        self.duplicate_line_action = self._action("Duplicate Line / Selection", lambda: self.editor.duplicate_current_line_or_selection(), "Ctrl+D")
        self.delete_line_action = self._action("Delete Line", self.delete_current_line, "Ctrl+Shift+K")
        self.select_all_action = self._action("Select All", self._select_all_active_text_surface, QKeySequence.StandardKey.SelectAll)
        self.comment_action = self._action("Toggle Comment", lambda: self.editor.toggle_comment(), "Ctrl+/")
        self.find_action = self._action("Find", lambda: self.toggle_find_panel(False), QKeySequence.StandardKey.Find)
        self.replace_action = self._action("Find and Replace", lambda: self.toggle_find_panel(True), "Ctrl+H")
        self.find_next_action = self._action("Find Next", self.find_next, "F3")
        self.find_previous_action = self._action("Find Previous", self.find_previous, "Shift+F3")
        self.goto_action = self._action("Go To Line...", self.goto_line, "Ctrl+G")
        self.dismiss_find_action = self._action("Close Find/Replace", self.hide_find_panel, "Esc")
        for action in (self.dismiss_find_action, self.find_next_action, self.find_previous_action):
            self.addAction(action)

        self.bold_action = self._action("Bold", lambda: self.editor.toggle_bold(), "Ctrl+B")
        self.italic_action = self._action("Italic", lambda: self.editor.toggle_italic(), "Ctrl+I")
        self.strike_action = self._action("Strikethrough", lambda: self.editor.toggle_strikethrough(), "Ctrl+Shift+X")
        self.quote_action = self._action("Quote Block", lambda: self.editor.toggle_blockquote())
        self.bullet_action = self._action("Bullet List", lambda: self.editor.toggle_bullet_list(), "Ctrl+L")
        self.number_action = self._action("Numbered List", lambda: self.editor.toggle_numbered_list(), "Ctrl+Shift+L")
        self.task_action = self._action("Task List", lambda: self.editor.toggle_task_list())
        self.indent_action = self._action("Indent", lambda: self.editor.indent_selection_or_insert_spaces(), "Ctrl+]")
        self.outdent_action = self._action("Outdent", lambda: self.editor.unindent_selection_or_line(), "Ctrl+[")
        self.inline_code_action = self._action("Inline Code", lambda: self.editor.toggle_inline_code(), "Ctrl+`")
        self.code_fence_action = self._action("Code Block", self.insert_code_block)
        # These are syntax/typing hints shown in menus only; they are deliberately
        # not registered QAction shortcuts because doing so would steal normal typing.
        self.quote_action.setText("Quote Block\t>")
        self.quote_action.setIconText("Quote Block")
        self.code_fence_action.setText("Code Block\t```")
        self.code_fence_action.setIconText("Code Block")
        self.heading_actions: list[QAction] = []
        for level in range(0, 7):
            label = "Normal Paragraph" if level == 0 else f"Heading {level}"
            action = self._action(label, lambda _checked=False, n=level: self.editor.apply_heading(n), f"Ctrl+Shift+{level}")
            self.heading_actions.append(action)
        # Tabbed uses one compact Heading dropdown; Classic keeps the individual
        # heading actions so users can personalise the toolbar at H1-H6 granularity.
        self.heading_tabbed_action = QAction("Heading", self)
        self.heading_tabbed_menu = QMenu(self)
        for action in self.heading_actions:
            self.heading_tabbed_menu.addAction(action)
        self.heading_tabbed_action.setMenu(self.heading_tabbed_menu)

        # Match Marko Plus: Tabbed exposes Inline Code and Code Block through one
        # shared Code flyout. The underlying actions remain the canonical actions
        # also used by menus and Classic customization.
        self.code_tabbed_action = QAction("Code", self)
        self.code_tabbed_menu = QMenu(self)
        self.code_tabbed_menu.addAction(self.inline_code_action)
        self.code_tabbed_menu.addAction(self.code_fence_action)
        self.code_tabbed_action.setMenu(self.code_tabbed_menu)

        self.link_action = self._action("Insert Link…", self.insert_link, "Ctrl+K")
        self.edit_link_action = self._action("Edit Link…", self.edit_link)
        self.remove_link_action = self._action("Remove Link", self.remove_link)
        self.rule_action = self._action("Horizontal Rule", lambda: self.editor.insert_horizontal_rule(), "Ctrl+Shift+H")
        self.image_action = self._action("Image Reference…", self.insert_image, "Ctrl+Shift+I")
        self.table_action = self._action("Table…", self.insert_table, "Ctrl+Shift+T")
        self.date_time_action = self._action("Date and Time", lambda: self.insert_text(datetime.now().strftime("%Y-%m-%d %H:%M")), "F5")
        self.date_action = self._action("Date Only", lambda: self.insert_text(datetime.now().strftime("%Y-%m-%d")), "Ctrl+;")
        self.time_action = self._action("Time Only", lambda: self.insert_text(datetime.now().strftime("%H:%M")), "Ctrl+:")
        self.symbol_action = self._action("Symbol…", self.insert_symbol, "Shift+F5")

        # Ctrl+1/Ctrl+2/Ctrl+3 keep the three reading layouts adjacent.
        self.source_only_action = self._action("Source Only", lambda: self.set_view_mode("source"), "Ctrl+1", checkable=True)
        self.split_action = self._action("Source + Preview", lambda: self.set_view_mode("split"), "Ctrl+2", checkable=True)
        self.preview_only_action = self._action("Preview Only", lambda: self.set_view_mode("preview"), "Ctrl+3", checkable=True)
        view_group = QActionGroup(self); view_group.setExclusive(True)
        for action in (self.source_only_action, self.split_action, self.preview_only_action):
            view_group.addAction(action)
        self.view_only_action = self._action("Locked Mode", self.toggle_locked_mode, "F12", checkable=True)
        self.word_wrap_action = self._action("Word Wrap", self.toggle_word_wrap, "Ctrl+Alt+Shift+W", checkable=True)
        self.line_numbers_action = self._action("Line Numbers", self.toggle_line_numbers, "Ctrl+Alt+Shift+L", checkable=True)
        self.status_bar_action = self._action("Show Status", self.toggle_status_bar, "Ctrl+Alt+Shift+S", checkable=True)
        self.fullscreen_action = self._action("Full Screen", self.toggle_fullscreen, "F11", checkable=True)
        self.zoom_in_action = self._action("Zoom In", lambda: self.set_zoom(self.zoom_percent + 10), QKeySequence.StandardKey.ZoomIn)
        self.zoom_out_action = self._action("Zoom Out", lambda: self.set_zoom(self.zoom_percent - 10), QKeySequence.StandardKey.ZoomOut)
        self.zoom_reset_action = self._action("Reset Zoom", lambda: self.set_zoom(100), "Ctrl+0")

        self.tabbed_mode_action = self._action("Modern (default)", lambda: self.set_toolbar_mode("tabbed"), checkable=True)
        self.classic_mode_action = self._action("Classic", lambda: self.set_toolbar_mode("classic"), checkable=True)
        # Shortcut-only mode switch: the old binary toolbar button remains removed,
        # but Ctrl+Alt+Shift+T continues to flip Modern/Classic globally.
        self.toolbar_mode_shortcut_action = self._action(
            "Toggle Editor Toolbar", self.toggle_toolbar_style, "Ctrl+Alt+Shift+T"
        )
        self.addAction(self.toolbar_mode_shortcut_action)
        self.next_tabbed_tab_action = self._action("Next Tabbed Tab", lambda: self.cycle_tabbed_tab(1), "Ctrl+Tab")
        self.previous_tabbed_tab_action = self._action("Previous Tabbed Tab", lambda: self.cycle_tabbed_tab(-1), "Ctrl+Shift+Tab")
        self.addAction(self.next_tabbed_tab_action); self.addAction(self.previous_tabbed_tab_action)
        toolbar_group = QActionGroup(self); toolbar_group.setExclusive(True)
        toolbar_group.addAction(self.tabbed_mode_action); toolbar_group.addAction(self.classic_mode_action)
        self.customize_classic_action = self._action("Customise Classic Bar…", self.show_classic_toolbar_dialog)

        self.drop_active_action = self._action(
            "Opens on Active Window", lambda: self.set_drop_open_mode("active_window"),
            checkable=True,
        )
        self.drop_new_window_action = self._action(
            "Opens on New Window", lambda: self.set_drop_open_mode("new_window"),
            checkable=True,
        )
        self.drop_active_action.setToolTip("App Drag-and-Drop — Opens on Active Window")
        self.drop_new_window_action.setToolTip("App Drag-and-Drop — Opens on New Window")
        drop_group = QActionGroup(self); drop_group.setExclusive(True)
        drop_group.addAction(self.drop_active_action); drop_group.addAction(self.drop_new_window_action)
        # Classic condenses the two AppMenu radio options into one binary toggle.
        self.drop_mode_toggle_action = self._action("App Drag-and-Drop", self.toggle_drop_open_mode, checkable=True)

        self.editor_canvas_theme_action = self._action(
            "Dark Editor", self.toggle_editor_canvas_light, "Ctrl+Alt+Shift+E", checkable=True
        )
        self.theme_system_action = self._action("System", lambda: self.set_theme("system"), checkable=True)
        self.theme_dark_action = self._action("Dark", lambda: self.set_theme("dark"), checkable=True)
        self.theme_light_action = self._action("Light", lambda: self.set_theme("light"), checkable=True)
        self.theme_light_action.setToolTip("App Theme — Light")
        self.theme_dark_action.setToolTip("App Theme — Dark")
        self.theme_system_action.setToolTip("App Theme — System")
        theme_group = QActionGroup(self); theme_group.setExclusive(True)
        for action in (self.theme_system_action, self.theme_dark_action, self.theme_light_action):
            theme_group.addAction(action)

        self.icon_family_actions = {}
        icon_group = QActionGroup(self); icon_group.setExclusive(True)
        for family, label in (
            ("harmony", "Maqa Icons Harmony"),
            ("humility", "Maqa Icons Humility"),
            ("heritage", "Maqa Icons Heritage"),
            ("halcyon", "Maqa Icons Halcyon"),
        ):
            action = self._action(
                label, lambda _checked=False, selected=family: self.set_icon_family(selected),
                checkable=True,
            )
            action.setToolTip(label)
            action.setChecked(family == self.icon_family)
            icon_group.addAction(action)
            self.icon_family_actions[family] = action
        self.icon_harmony_action = self.icon_family_actions["harmony"]
        self.icon_humility_action = self.icon_family_actions["humility"]
        self.icon_heritage_action = self.icon_family_actions["heritage"]
        self.icon_halcyon_action = self.icon_family_actions["halcyon"]

        duplicate_policy = self._file_policy("dirty_duplicate_action", {"ask", "current", "saved"})
        self.dirty_duplicate_actions: dict[str, QAction] = {}
        dirty_duplicate_group = QActionGroup(self); dirty_duplicate_group.setExclusive(True)
        for value, label in (("ask", "Ask Every Time"), ("current", "Duplicate Current Document"), ("saved", "Duplicate Last Saved Version")):
            action = self._action(label, lambda _checked=False, selected=value: self._set_file_policy("dirty_duplicate_action", selected), checkable=True)
            action.setChecked(value == duplicate_policy)
            dirty_duplicate_group.addAction(action)
            self.dirty_duplicate_actions[value] = action

        external_policy = self._file_policy("dirty_external_action", {"ask", "save", "saved"})
        self.dirty_external_actions: dict[str, QAction] = {}
        dirty_external_group = QActionGroup(self); dirty_external_group.setExclusive(True)
        for value, label in (("ask", "Ask Every Time"), ("save", "Save Changes and Open"), ("saved", "Open Last Saved Version")):
            action = self._action(label, lambda _checked=False, selected=value: self._set_file_policy("dirty_external_action", selected), checkable=True)
            action.setChecked(value == external_policy)
            dirty_external_group.addAction(action)
            self.dirty_external_actions[value] = action

        self.tab_width_action = self._action("Tab Width...", self.choose_tab_width)
        self.editor_font_action = self._action("Source Font...", self.choose_editor_font, "Ctrl+Shift+[")
        self.display_font_action = self._action("Preview Font...", self.choose_display_font, "Ctrl+Shift+]")

        self.documentation_action = self._action("Documentation", self.show_documentation, QKeySequence.StandardKey.HelpContents)
        self.quick_start_action = self._action("Quick Tour…", self.show_quick_tour, "Shift+F1")
        self.quick_start_action.setToolTip("Quick Tour… (Shift+F1)")
        self.shortcuts_action = self._action("Keyboard Shortcuts", self.show_shortcuts, "Ctrl+Shift+/")
        self.github_action = self._action("GitHub Repository", self.open_github_repository)
        self.issue_action = self._action("Raise an Issue", self.report_an_issue)
        self.about_action = self._action("About MaqaronyPad", self.show_about)
        self.about_action.setMenuRole(QAction.MenuRole.AboutRole)

    def _icon_family_directory(self) -> str:
        return {
            "harmony": "toolbar-icons", "humility": "toolbar-icons-classic",
            "heritage": "toolbar-icons-original", "halcyon": "toolbar-icons-aero",
        }[self.icon_family]

    def set_icon_family(self, family: str) -> None:
        if family not in {"harmony", "humility", "heritage", "halcyon"}:
            return
        self.icon_family = family
        self.icon_family_actions[family].setChecked(True)
        self._refresh_action_icons()
        self.persist_preferences()
        self.statusBar().showMessage(f"Maqa Icons {family.title()}.", 2500)

    def _effective_scheme(self) -> str:
        if self.theme in {"light", "dark"}:
            return self.theme
        color = QApplication.instance().palette().color(QPalette.ColorRole.Base)
        return "light" if color.lightness() >= 140 else "dark"

    def _refresh_action_icons(self) -> None:
        scheme = self._effective_scheme()
        # Marko Plus 0.4.4 is the canonical Marko command-icon family.
        # MaqaronyPad keeps its own command inventory/presentation, but shared command
        # semantics intentionally resolve to the same canonical assets.
        mapping = {
            "new_action":"new", "new_window_action":"new-window", "open_action":"open", "save_action":"save", "save_as_action":"save-as", "save_exit_action":"save-exit",
            "duplicate_file_action":"duplicate-file", "rename_file_action":"rename", "delete_file_action":"delete-file",
            "open_folder_action":"open-folder", "external_editor_action":"external-editor", "properties_action":"properties",
            "print_action":"print", "export_pdf_action":"export-pdf", "exit_action":"exit",
            "undo_action":"undo", "redo_action":"redo", "cut_action":"cut", "copy_action":"copy", "paste_action":"paste",
            "paste_plain_action":"paste-plain", "delete_action":"delete-text", "comment_action":"comment-toggle", "select_all_action":"select-all",
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
            "editor_layout_menu_action":"layout-markdown", "editor_toolbar_menu_action":"layout-ribbon",
            "drop_active_action":"drop-active", "drop_new_window_action":"drop-new-window",
            "tabbed_mode_action":"toolbar-tabbed", "classic_mode_action":"toolbar-classic",
            "editor_canvas_theme_action":"editor-canvas", "display_font_action":"font-dialog", "editor_font_action":"default-font",
            "heading_tabbed_action":"heading-group", "heading_menu_action":"heading-group", "code_tabbed_action":"code-group", "link_menu_action":"link-group",
            "app_icons_menu_action":"app-icons", "icon_harmony_action":"icons-new",
            "icon_humility_action":"icons-classic", "icon_heritage_action":"icons-legacy",
            "theme_tabbed_action":"app-theme", "drop_tabbed_action":"app-drag-and-drop",
            "dirty_duplicate_tabbed_action":"dirty-duplicate-policy", "dirty_external_tabbed_action":"dirty-external-policy",
            "theme_system_action":"theme-system", "theme_dark_action":"theme-dark", "theme_light_action":"theme-light",
            "tab_width_action":"tab-width", "quick_start_action":"tutorial",
            "shortcuts_action":"shortcuts", "documentation_action":"documentation", "github_action":"github",
            "issue_action":"issue", "about_action":"about",
        }
        for attr, name in mapping.items():
            action = getattr(self, attr, None)
            path = asset_path(self._icon_family_directory(), scheme, f"{name}.png")
            if action is not None and path.is_file():
                action.setIcon(QIcon(str(path)))
        for level, action in enumerate(self.heading_actions):
            path = asset_path(self._icon_family_directory(), scheme, f"heading-{level}.png")
            if path.is_file():
                action.setIcon(QIcon(str(path)))
        # Modern/Classic radio actions retain their dedicated icons in the
        # AppMenu and toolbar flyout; only the customisation entry is text-only.
        self.customize_classic_action.setIcon(QIcon())
        self._sync_compact_toolbar_toggles()
        if hasattr(self, "tabbed_buttons"):
            self._apply_toolbar_button_style()

    def _create_menus(self) -> None:
        bar = self.menuBar()
        bar.setNativeMenuBar(True)

        self.file_menu = bar.addMenu("&File")
        self.file_menu.addAction(self.new_action)
        self.file_menu.addAction(self.new_window_action)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        more = self.file_menu.addMenu("More Actions")
        more.addAction(self.duplicate_file_action)
        more.addAction(self.rename_file_action)
        more.addAction(self.delete_file_action)
        more.addSeparator()
        more.addAction(self.external_editor_action)
        more.addAction(self.open_folder_action)
        more.addSeparator()
        more.addAction(self.properties_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.print_action)
        self.file_menu.addAction(self.export_pdf_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        self.file_menu.addAction(self.save_exit_action)

        self.edit_menu = bar.addMenu("&Edit")
        edit = self.edit_menu
        edit.addAction(self.undo_action); edit.addAction(self.redo_action)
        edit.addSeparator()
        edit.addAction(self.cut_action); edit.addAction(self.copy_action); edit.addAction(self.paste_action); edit.addAction(self.paste_plain_action)
        edit.addSeparator()
        edit.addAction(self.delete_action)
        edit.addSeparator()
        edit.addAction(self.comment_action)
        edit.addAction(self.duplicate_line_action); edit.addAction(self.delete_line_action)
        edit.addSeparator()
        edit.addAction(self.select_all_action)
        edit.addSeparator()
        edit.addAction(self.find_action); edit.addAction(self.goto_action); edit.addAction(self.replace_action)

        self.markdown_menu = bar.addMenu("&Markdown")
        markdown = self.markdown_menu
        markdown.addAction(self.bold_action); markdown.addAction(self.italic_action); markdown.addAction(self.strike_action); markdown.addAction(self.quote_action)
        markdown.addSeparator()
        markdown.addAction(self.bullet_action); markdown.addAction(self.number_action); markdown.addAction(self.task_action)
        markdown.addSeparator()
        markdown.addAction(self.indent_action); markdown.addAction(self.outdent_action)
        markdown.addSeparator()
        markdown.addAction(self.inline_code_action); markdown.addAction(self.code_fence_action)
        markdown.addSeparator()
        headings = markdown.addMenu("Heading")
        for action in self.heading_actions:
            headings.addAction(action)
        self.heading_menu_action = headings.menuAction()

        self.insert_menu = bar.addMenu("&Insert")
        insert = self.insert_menu
        insert.addAction(self.image_action)
        links = insert.addMenu("Link")
        links.addAction(self.link_action); links.addAction(self.edit_link_action); links.addSeparator(); links.addAction(self.remove_link_action)
        self.link_menu_action = links.menuAction()
        insert.addSeparator()
        insert.addAction(self.table_action)
        insert.addSeparator()
        insert.addAction(self.date_time_action); insert.addAction(self.date_action); insert.addAction(self.time_action)
        insert.addSeparator()
        insert.addAction(self.rule_action); insert.addAction(self.symbol_action)

        self.view_menu = bar.addMenu("&View")
        view = self.view_menu
        view.addAction(self.fullscreen_action)
        view.addAction(self.status_bar_action)
        view.addSeparator()
        view.addAction(self.word_wrap_action)
        view.addAction(self.line_numbers_action)
        view.addAction(self.editor_canvas_theme_action)
        view.addSeparator()
        view.addAction(self.view_only_action)
        layout = view.addMenu("Editor Layout")
        layout.addAction(self.source_only_action); layout.addAction(self.split_action); layout.addAction(self.preview_only_action)
        self.editor_layout_menu_action = layout.menuAction()
        self.toolbar_menu = view.addMenu("Editor Toolbar")
        self.toolbar_menu.addAction(self.tabbed_mode_action); self.toolbar_menu.addAction(self.classic_mode_action)
        self.toolbar_menu.addSeparator(); self.toolbar_menu.addAction(self.customize_classic_action)
        self.editor_toolbar_menu_action = self.toolbar_menu.menuAction()
        view.addSeparator()
        zoom = view.addMenu("Editor Zoom")
        zoom.addAction(self.zoom_in_action); zoom.addAction(self.zoom_out_action); zoom.addSeparator(); zoom.addAction(self.zoom_reset_action)
        more_settings = view.addMenu("Editor Miscellaneous")
        more_settings.addAction(self.tab_width_action)
        more_settings.addSeparator()
        more_settings.addAction(self.editor_font_action)
        more_settings.addAction(self.display_font_action)

        self.settings_menu = bar.addMenu("&Settings")
        settings = self.settings_menu
        theme_menu = settings.addMenu("App Theme")
        theme_menu.addAction(self.theme_light_action); theme_menu.addAction(self.theme_dark_action); theme_menu.addAction(self.theme_system_action)
        self.theme_tabbed_action = theme_menu.menuAction()
        icon_menu = settings.addMenu("App Icons")
        for family in ("harmony", "humility", "heritage", "halcyon"):
            icon_menu.addAction(self.icon_family_actions[family])
        self.app_icons_menu_action = icon_menu.menuAction()
        behaviour = settings.addMenu("App Drag-and-Drop")
        behaviour.addAction(self.drop_active_action); behaviour.addAction(self.drop_new_window_action)
        self.drop_tabbed_action = behaviour.menuAction()
        settings.addSeparator()
        dirty_duplicate = settings.addMenu("Duplicate File with Unsaved Changes")
        for key in ("ask", "current", "saved"):
            dirty_duplicate.addAction(self.dirty_duplicate_actions[key])
        self.dirty_duplicate_tabbed_action = dirty_duplicate.menuAction()
        dirty_external = settings.addMenu("Open Externally with Unsaved Changes")
        for key in ("ask", "save", "saved"):
            dirty_external.addAction(self.dirty_external_actions[key])
        self.dirty_external_tabbed_action = dirty_external.menuAction()

        self.help_menu = bar.addMenu("&Help")
        help_menu = self.help_menu
        help_menu.addAction(self.documentation_action)
        help_menu.addSeparator()
        help_menu.addAction(self.quick_start_action); help_menu.addAction(self.shortcuts_action)
        help_menu.addSeparator()
        help_menu.addAction(self.github_action); help_menu.addAction(self.issue_action)
        help_menu.addSeparator()
        help_menu.addAction(self.about_action)
        self._refresh_action_icons()

    def _apply_editor_appearance(self) -> None:
        def apply() -> None:
            self.editor.set_editor_font(self._source_font_for_zoom())
            self._apply_editor_canvas_theme()
            self._apply_preview_font()
            self.update_status()
        self._apply_presentation_safely(apply)

    def _apply_editor_canvas_theme(self) -> None:
        scheme = "light" if self.editor_canvas_light else "dark"
        self.editor.set_color_scheme(scheme)
        palette = QPalette(self.editor.palette())
        if self.editor_canvas_light:
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#202124"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#0B8781"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        else:
            palette.setColor(QPalette.ColorRole.Base, QColor("#151719"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#F1F3F4"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#158B86"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        self.editor.setPalette(palette)
        self.editor.viewport().setPalette(palette)
        self.editor.line_number_area.update()
        # The editor-canvas switch governs both reading surfaces: source and Preview.
        preview_palette = QPalette(self.preview.palette())
        if self.editor_canvas_light:
            preview_palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            preview_palette.setColor(QPalette.ColorRole.Text, QColor("#202124"))
            link_color = QColor("#174EA6")
            preview_palette.setColor(QPalette.ColorRole.Highlight, QColor("#0B8781"))
            preview_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        else:
            preview_palette.setColor(QPalette.ColorRole.Base, QColor("#151719"))
            preview_palette.setColor(QPalette.ColorRole.Text, QColor("#F1F3F4"))
            link_color = QColor("#82AAFF")
            preview_palette.setColor(QPalette.ColorRole.Highlight, QColor("#158B86"))
            preview_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        preview_palette.setColor(QPalette.ColorRole.Link, link_color)
        preview_palette.setColor(QPalette.ColorRole.LinkVisited, link_color)
        self.preview.setPalette(preview_palette)
        self.preview.viewport().setPalette(preview_palette)
        self.preview.document().setDefaultStyleSheet(f"a {{ color: {link_color.name()}; }}")
        self._apply_preview_link_color(link_color)

    def toggle_editor_canvas_light(self, checked: bool) -> None:
        # User-facing action is "Dark Editor": checked means the canvas is dark.
        self.editor_canvas_light = not bool(checked)
        self.editor_canvas_theme_action.setChecked(bool(checked))
        self._apply_presentation_safely(self._apply_editor_canvas_theme)
        self.persist_preferences()
        self.statusBar().showMessage(
            "Editor canvas switched to a dark background."
            if not self.editor_canvas_light
            else "Editor canvas switched to a light background.", 3000
        )

    def set_theme(self, theme: str) -> None:
        if theme not in {"system", "dark", "light"}: return
        changed = theme != self.theme
        self.theme = theme
        apply_theme(QApplication.instance(), theme)
        self._apply_editor_appearance()
        self._refresh_action_icons()
        QTimer.singleShot(0, self._refresh_appimage_overflow_buttons)
        getattr(self, f"theme_{theme}_action").setChecked(True)
        self.persist_preferences()
        if changed:
            self.statusBar().showMessage(f"Theme: {theme.capitalize()}.", 2500)

    def _preview_base_font(self) -> QFont:
        font = QFont(QApplication.font()); stored = self.settings.get("preview_font")
        if isinstance(stored, str) and stored:
            candidate = QFont()
            if candidate.fromString(stored): font = candidate
        if font.pointSizeF() <= 0: font.setPointSizeF(10.0)
        return font

    def _apply_preview_font(self) -> None:
        font = self._preview_base_font()
        font.setPointSizeF(max(6.0, font.pointSizeF() * self.zoom_percent / 100.0))
        self.preview.document().setDefaultFont(font)

    def choose_display_font(self) -> None:
        dialog = QFontDialog(self._preview_base_font(), self)
        dialog.setWindowTitle(dialog_title("Preview Font"))
        dialog.setOption(QFontDialog.FontDialogOption.DontUseNativeDialog, True)
        effects = next((
            group for group in dialog.findChildren(QGroupBox)
            if group.title().replace("&", "").strip().casefold() == "effects"
        ), None)
        if effects is None or effects.layout() is None:
            return
        italic_quotes = QCheckBox("Italicize block quotations", effects)
        italic_quotes.setChecked(bool(self.settings.get("preview_italic_quotes", False)))
        effects_layout = effects.layout()
        if isinstance(effects_layout, QGridLayout):
            effects_layout.addWidget(
                italic_quotes, effects_layout.rowCount(), 0, 1, max(1, effects_layout.columnCount())
            )
        else:
            effects_layout.addWidget(italic_quotes)

        def update_effect_availability(font: QFont) -> None:
            already_italic = font.italic()
            italic_quotes.setEnabled(not already_italic)
            italic_quotes.setToolTip("The selected Preview font is already italic." if already_italic else "")

        dialog.currentFontChanged.connect(update_effect_availability)
        update_effect_availability(dialog.currentFont())
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        chosen = dialog.currentFont()
        self.settings["preview_font"] = chosen.toString()
        self.settings["preview_italic_quotes"] = italic_quotes.isChecked()
        save_json_settings(self.settings)
        self._apply_preview_font()
        self.refresh_preview_now()

    def choose_editor_font(self) -> None:
        chosen, ok = QFontDialog.getFont(self.editor.font(), self, dialog_title("Source Font"))
        if not ok:
            return
        self.settings["editor_font_family"] = chosen.family()
        self.settings["editor_font_size"] = chosen.pointSize()
        self.settings["editor_font_weight"] = int(chosen.weight())
        self.settings["editor_font_italic"] = chosen.italic()
        save_json_settings(self.settings)
        self._apply_editor_appearance()

    def choose_tab_width(self) -> None:
        value, ok = QInputDialog.getInt(self, dialog_title("Tab Width"), "Spaces per Tab:", self.editor._tab_width_spaces, 1, 16)
        if ok: self.editor.set_tab_width_spaces(value); self.persist_preferences()

    def _update_ui_state(self) -> None:
        modified = self.editor.document().isModified(); name = self.current_path.name if self.current_path else "Untitled.md"
        lock_suffix = " — Locked Mode" if self.editor.isReadOnly() else ""
        self.setWindowTitle(f"{'*' if modified else ''}{name} — {APP_NAME}{lock_suffix}")
        has_file = self.current_path is not None
        for action in (self.rename_file_action, self.delete_file_action, self.duplicate_file_action, self.external_editor_action): action.setEnabled(has_file)
        mutable = (
            not self.editor.isReadOnly()
            and self.view_mode != "preview"
            and not self._preview_is_active_text_surface()
        )
        mutation_actions = [self.cut_action, self.paste_action, self.paste_plain_action, self.delete_action, self.comment_action, self.bold_action, self.italic_action, self.strike_action, self.quote_action, self.bullet_action, self.number_action, self.task_action, self.indent_action, self.outdent_action, self.inline_code_action, self.code_fence_action, self.link_action, self.edit_link_action, self.remove_link_action, self.rule_action, self.image_action, self.table_action, self.date_time_action, self.date_action, self.time_action, self.symbol_action, self.duplicate_line_action, self.delete_line_action, *self.heading_actions]
        for action in mutation_actions: action.setEnabled(mutable)
        self.heading_tabbed_action.setEnabled(mutable)
        self._sync_undo_redo_state()
        self.update_status()

    def _sync_undo_redo_state(self) -> None:
        mutable = (
            not self.editor.isReadOnly()
            and self.view_mode != "preview"
            and not self._preview_is_active_text_surface()
        )
        document = self.editor.document()
        self.undo_action.setEnabled(mutable and document.isUndoAvailable())
        self.redo_action.setEnabled(mutable and document.isRedoAvailable())
