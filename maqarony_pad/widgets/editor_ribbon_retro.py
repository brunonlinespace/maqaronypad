#!/usr/bin/env python3
"""Existing MaqaronyPad Tabbed/Classic presentation, relocated without behaviour changes."""
from __future__ import annotations

import os
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QLabel, QMenu, QPushButton, QScrollArea, QSizePolicy, QTabWidget,
    QToolBar, QToolButton, QVBoxLayout, QWidget,
)

# Existing host-owned lookups are bound at import time by app.py.
# Keep their original definitions and values in the application module.

class EditorRibbonRetroMixin:
    def _show_toolbar_context_menu(self, global_pos) -> None:
        menu = QMenu(self)
        menu.addAction(self.tabbed_mode_action)
        menu.addAction(self.classic_mode_action)
        menu.addSeparator()
        menu.addAction(self.customize_classic_action)
        menu.exec(global_pos)

    def _enable_toolbar_context_menu(self, widget: QWidget) -> None:
        widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        if bool(widget.property("maqaronyPadToolbarContextConnected")):
            return
        widget.customContextMenuRequested.connect(
            lambda pos, target=widget: self._show_toolbar_context_menu(target.mapToGlobal(pos))
        )
        widget.setProperty("maqaronyPadToolbarContextConnected", True)

    def _style_command_button(self, button: QToolButton, *, tabbed: bool = False) -> None:
        """Apply MaqaronyPad's exact icon-only 52px command-button geometry."""
        button.setIconSize(QSize(36, 36))
        button.setFixedSize(52, 52)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        button.setAutoRaise(False)
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        button.setStyleSheet("")
        action = button.defaultAction()
        if action is not None and action.menu() is not None:
            button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

    @staticmethod
    def _tabbed_separator(toolbar: QToolBar) -> None:
        toolbar.addSeparator()

    def _tabbed_add_action(self, toolbar: QToolBar, action: QAction) -> None:
        toolbar.addAction(action)
        button = toolbar.widgetForAction(action)
        if isinstance(button, QToolButton):
            self._style_command_button(button, tabbed=True)
            self._enable_toolbar_context_menu(button)
            button.setAccessibleName(action.text().split("\t", 1)[0].replace("&", "").replace("…", "").strip())
            self.tabbed_buttons.append(button)

    def _create_tabbed_toolbar(self) -> None:
        self.tabbed_buttons: list[QToolButton] = []
        self.tabbed_toolbars: list[QToolBar] = []
        self.tabbed_tabs = QTabWidget(self.tabbed_container)
        self.tabbed_tabs.setDocumentMode(True)
        self.tabbed_tabs.setMovable(False)
        self.tabbed_tabs.setTabsClosable(False)
        self.tabbed_tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabbed_tabs.tabBar().setExpanding(False)
        # Only the tab strip scrolls. Each selected page uses QToolBar's native
        # extension/overflow chevron when its one-line command row runs out of space.
        self.tabbed_tabs.tabBar().setUsesScrollButtons(True)
        self.tabbed_tabs.tabBar().installEventFilter(self)
        self._tabbed_collapsed = False
        self._tabbed_expanded_minimum_height = self.tabbed_tabs.minimumHeight()
        self._tabbed_expanded_maximum_height = self.tabbed_tabs.maximumHeight()
        self.tabbed_tabs.currentChanged.connect(self._sync_collapsed_tabbed_page)
        self.tabbed_layout.addWidget(self.tabbed_tabs)
        pages = {
            "File": [
                [self.new_action, self.new_window_action, self.open_action, self.save_action, self.save_as_action, self.save_exit_action],
                [self.duplicate_file_action, self.rename_file_action, self.delete_file_action, self.external_editor_action, self.open_folder_action, self.properties_action],
                [self.print_action, self.export_pdf_action],
                [self.exit_action],
            ],
            "Home": [
                [self.cut_action, self.copy_action, self.paste_action, self.paste_plain_action, self.delete_action, self.select_all_action],
                [self.undo_action, self.redo_action, self.duplicate_line_action, self.delete_line_action, self.comment_action, self.find_action, self.goto_action, self.replace_action],
                [self.bold_action, self.italic_action, self.strike_action, self.code_tabbed_action],
                [self.bullet_action, self.number_action, self.task_action, self.quote_action, self.indent_action, self.outdent_action],
                [self.heading_tabbed_action],
            ],
            "Insert": [
                [self.image_action, self.link_action, self.edit_link_action, self.remove_link_action],
                [self.table_action],
                [self.date_time_action, self.date_action, self.time_action],
                [self.rule_action, self.symbol_action],
            ],
            "View": [
                [self.fullscreen_action, self.status_bar_action],
                [self.word_wrap_action, self.line_numbers_action, self.editor_canvas_theme_action, self.view_only_action],
                [self.source_only_action, self.split_action, self.preview_only_action],
                [self.editor_toolbar_menu_action],
                [self.zoom_in_action, self.zoom_out_action, self.zoom_reset_action],
                [self.tab_width_action, self.editor_font_action, self.display_font_action],
            ],
            "Settings": [
                [self.theme_light_action, self.theme_dark_action, self.theme_system_action],
                [self.icon_harmony_action, self.icon_humility_action, self.icon_heritage_action],
                [self.drop_active_action, self.drop_new_window_action],
                [self.dirty_duplicate_tabbed_action, self.dirty_external_tabbed_action],
            ],
            "Help": [
                [self.documentation_action, self.quick_start_action, self.shortcuts_action],
                [self.github_action, self.issue_action],
                [self.about_action],
            ],
        }
        for name, groups in pages.items():
            page = QWidget(self.tabbed_tabs)
            layout = QVBoxLayout(page)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(0)
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            toolbar = QToolBar(name, page)
            toolbar.setObjectName(f"maqaronyPadTabbed{name}Toolbar")
            toolbar.setMovable(False)
            toolbar.setFloatable(False)
            toolbar.setOrientation(Qt.Orientation.Horizontal)
            toolbar.setIconSize(QSize(36, 36))
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            self._enable_toolbar_context_menu(toolbar)
            toolbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            toolbar.setMinimumHeight(56)
            toolbar.setMaximumHeight(56)
            if toolbar.layout() is not None:
                toolbar.layout().setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
                toolbar.layout().setContentsMargins(2, 2, 2, 2)
                toolbar.layout().setSpacing(2)
            for index, actions in enumerate(groups):
                if index:
                    self._tabbed_separator(toolbar)
                for action in actions:
                    self._tabbed_add_action(toolbar, action)
            layout.addWidget(toolbar, 0, Qt.AlignmentFlag.AlignTop)
            self.tabbed_toolbars.append(toolbar)
            self.tabbed_tabs.addTab(page, name)
        # Home is the default Tabbed page on every new window/startup.
        home_index = next((i for i in range(self.tabbed_tabs.count()) if self.tabbed_tabs.tabText(i) == "Home"), 0)
        self.tabbed_tabs.setCurrentIndex(home_index)

    def _classic_toolbar_catalog(self) -> list[tuple[str, str, str, QAction]]:
        """Classic inventory in flattened AppMenu order.

        Ordinary submenu commands are exposed flat. The only toolbar flyouts are
        the two approved dirty-document policy controls. Exactly-binary radio
        choices use one compact toggle presentation while the AppMenu retains its
        canonical mutually-exclusive actions.
        """
        items = [
            # File (including flattened More Actions)
            ("File", "new", "New", self.new_action),
            ("File", "new_window", "New Window", self.new_window_action),
            ("File", "open", "Open", self.open_action),
            ("File", "save", "Save", self.save_action),
            ("File", "save_as", "Save As", self.save_as_action),
            ("File", "duplicate_file", "Duplicate File", self.duplicate_file_action),
            ("File", "rename_file", "Rename", self.rename_file_action),
            ("File", "delete_file", "Delete File", self.delete_file_action),
            ("File", "external_editor", "Open in External Editor", self.external_editor_action),
            ("File", "open_folder", "Open Containing Folder", self.open_folder_action),
            ("File", "properties", "Properties", self.properties_action),
            ("File", "print", "Print", self.print_action),
            ("File", "export_pdf", "Export PDF", self.export_pdf_action),
            ("File", "save_exit", "Save and Exit", self.save_exit_action),
            ("File", "exit", "Exit", self.exit_action),

            # Edit
            ("Edit", "undo", "Undo", self.undo_action),
            ("Edit", "redo", "Redo", self.redo_action),
            ("Edit", "cut", "Cut", self.cut_action),
            ("Edit", "copy", "Copy", self.copy_action),
            # Legacy Classic IDs intentionally retain their pre-0.2.3 behavior so
            # existing customized bars preserve semantic intent across the Paste
            # correction: old paste_markdown was smart; old paste was literal.
            ("Edit", "paste_markdown", "Paste", self.paste_action),
            ("Edit", "paste", "Paste as Plain Text", self.paste_plain_action),
            ("Edit", "delete", "Delete", self.delete_action),
            ("Edit", "comment", "Toggle Comment", self.comment_action),
            ("Edit", "duplicate_line", "Duplicate Line / Selection", self.duplicate_line_action),
            ("Edit", "delete_line", "Delete Line", self.delete_line_action),
            ("Edit", "select_all", "Select All", self.select_all_action),
            ("Edit", "find", "Find", self.find_action),
            ("Edit", "goto", "Go To Line...", self.goto_action),
            ("Edit", "replace", "Find and Replace", self.replace_action),

            # Markdown
            ("Markdown", "bold", "Bold", self.bold_action),
            ("Markdown", "italic", "Italic", self.italic_action),
            ("Markdown", "strike", "Strikethrough", self.strike_action),
            ("Markdown", "quote", "Quote Block", self.quote_action),
            ("Markdown", "bullet", "Bullet List", self.bullet_action),
            ("Markdown", "number", "Numbered List", self.number_action),
            ("Markdown", "task", "Task List", self.task_action),
            ("Markdown", "indent", "Indent", self.indent_action),
            ("Markdown", "outdent", "Outdent", self.outdent_action),
            ("Markdown", "inline_code", "Inline Code", self.inline_code_action),
            ("Markdown", "code_block", "Code Block", self.code_fence_action),
        ]
        items.extend(("Markdown", f"heading_{level}", action.iconText() or action.text(), action) for level, action in enumerate(self.heading_actions))
        items.extend([
            # Insert (flattened Link submenu)
            ("Insert", "image", "Image Reference", self.image_action),
            ("Insert", "link", "Insert Link", self.link_action),
            ("Insert", "edit_link", "Edit Link", self.edit_link_action),
            ("Insert", "remove_link", "Remove Link", self.remove_link_action),
            ("Insert", "table", "Table", self.table_action),
            ("Insert", "date_time", "Date and Time", self.date_time_action),
            ("Insert", "date", "Date Only", self.date_action),
            ("Insert", "time", "Time Only", self.time_action),
            ("Insert", "rule", "Horizontal Rule", self.rule_action),
            ("Insert", "symbol", "Symbol", self.symbol_action),

            # View (flattened Editor Layout / Toolbar / Zoom / Miscellaneous)
            ("View", "fullscreen", "Full Screen", self.fullscreen_action),
            ("View", "status_bar", "Show Status", self.status_bar_action),
            ("View", "word_wrap", "Word Wrap", self.word_wrap_action),
            ("View", "line_numbers", "Line Numbers", self.line_numbers_action),
            ("View", "editor_canvas", "Dark Editor", self.editor_canvas_theme_action),
            ("View", "view_only", "Locked Mode", self.view_only_action),
            ("View", "source", "Source Only", self.source_only_action),
            ("View", "split", "Source + Preview", self.split_action),
            ("View", "preview", "Preview Only", self.preview_only_action),
            ("View", "editor_toolbar", "Editor Toolbar", self.editor_toolbar_menu_action),
            ("View", "zoom_in", "Zoom In", self.zoom_in_action),
            ("View", "zoom_out", "Zoom Out", self.zoom_out_action),
            ("View", "zoom_reset", "Reset Zoom", self.zoom_reset_action),
            ("View", "tab_width", "Tab Width...", self.tab_width_action),
            ("View", "source_font", "Source Font...", self.editor_font_action),
            ("View", "preview_font", "Preview Font...", self.display_font_action),

            # Settings. App Theme is three-way so stays flat. App Drag-and-Drop is
            # exactly binary so Classic uses one compact toggle. Only the final two
            # policy menuActions remain flyouts.
            ("Settings", "theme_light", "Light", self.theme_light_action),
            ("Settings", "theme_dark", "Dark", self.theme_dark_action),
            ("Settings", "theme_system", "System", self.theme_system_action),
            ("Settings", "drop_mode", "App Drag-and-Drop", self.drop_mode_toggle_action),
            ("Settings", "dirty_duplicate_policy", "Duplicate File with Unsaved Changes", self.dirty_duplicate_tabbed_action),
            ("Settings", "dirty_external_policy", "Open Externally with Unsaved Changes", self.dirty_external_tabbed_action),

            # Help
            ("Help", "documentation", "Documentation", self.documentation_action),
            ("Help", "quick_start", "Quick Tour…", self.quick_start_action),
            ("Help", "shortcuts", "Keyboard Shortcuts", self.shortcuts_action),
            ("Help", "github", "GitHub Repository", self.github_action),
            ("Help", "issue", "Raise an Issue", self.issue_action),
            ("Help", "about", "About MaqaronyPad", self.about_action),
        ])
        return items

    def _create_classic_toolbar(self) -> None:
        self.classic_toolbar = QToolBar("MaqaronyPad", self)
        self.classic_toolbar.setObjectName("classicToolbar")
        self.classic_toolbar.setMovable(False); self.classic_toolbar.setIconSize(QSize(36, 36))
        self._enable_toolbar_context_menu(self.classic_toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.classic_toolbar)
        self.rebuild_classic_toolbar()

    def rebuild_classic_toolbar(self) -> None:
        self.classic_toolbar.clear(); selected = set(self.classic_toolbar_items); last_group = None
        for group, item_id, _label, action in self._classic_toolbar_catalog():
            if item_id not in selected:
                continue
            if last_group is not None and group != last_group:
                self.classic_toolbar.addSeparator()
            self.classic_toolbar.addAction(action); last_group = group
        self._apply_toolbar_button_style()

    def show_classic_toolbar_dialog(self) -> None:
        dialog = QDialog(self); dialog.setWindowTitle(dialog_title("Customise Classic Bar")); dialog.setWindowIcon(self.windowIcon()); dialog.resize(560, 620)
        outer = QVBoxLayout(dialog)
        intro = QLabel("Tick the controls you want on the Classic toolbar. All commands remain available from the application menus regardless of toolbar selection.", dialog)
        intro.setWordWrap(True); outer.addWidget(intro)
        scroll = QScrollArea(dialog); scroll.setWidgetResizable(True); body = QWidget(scroll); body_layout = QVBoxLayout(body)
        checks: dict[str, QCheckBox] = {}; current_group = None; group_layout = None
        for group, item_id, label, _action in self._classic_toolbar_catalog():
            if group != current_group:
                box = QGroupBox(group, body); group_layout = QVBoxLayout(box); body_layout.addWidget(box); current_group = group
            check = QCheckBox(label, body); check.setChecked(item_id in self.classic_toolbar_items); group_layout.addWidget(check); checks[item_id] = check
        body_layout.addStretch(1); scroll.setWidget(body); outer.addWidget(scroll, 1)
        controls = QHBoxLayout(); default_button = QPushButton("Default", dialog); controls.addWidget(default_button); controls.addStretch(1)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel, parent=dialog); controls.addWidget(buttons); outer.addLayout(controls)
        def restore_default() -> None:
            defaults = set(CLASSIC_TOOLBAR_DEFAULT)
            for item_id, check in checks.items(): check.setChecked(item_id in defaults)
        def save_selection() -> None:
            self.classic_toolbar_items = [item_id for _group, item_id, _label, _action in self._classic_toolbar_catalog() if checks[item_id].isChecked()]
            self.rebuild_classic_toolbar(); self.persist_preferences(); dialog.accept()
        default_button.clicked.connect(restore_default); buttons.accepted.connect(save_selection); buttons.rejected.connect(dialog.reject); dialog.exec()

    def cycle_tabbed_tab(self, step: int) -> None:
        """Move to the next/previous Tabbed toolbar page when Tabbed is active."""
        if self.toolbar_mode != "tabbed" or self.tabbed_tabs.count() <= 0:
            return
        self.tabbed_tabs.setCurrentIndex((self.tabbed_tabs.currentIndex() + step) % self.tabbed_tabs.count())

    def _sync_compact_toolbar_toggles(self) -> None:
        """Synchronise the remaining synthetic binary toolbar control."""
        new_window = self.drop_open_mode == "new_window"
        self.drop_mode_toggle_action.setChecked(new_window)
        drop_label = "Opens on New Window" if new_window else "Opens on Active Window"
        self.drop_mode_toggle_action.setToolTip(f"App Drag-and-Drop — {drop_label}")

        path = asset_path(
            self._icon_family_directory(), self._effective_scheme(),
            "drop-new-window.png" if new_window else "drop-active.png",
        )
        if path.is_file():
            self.drop_mode_toggle_action.setIcon(QIcon(str(path)))

    def toggle_toolbar_style(self) -> None:
        self.set_toolbar_mode("classic" if self.toolbar_mode == "tabbed" else "tabbed")

    def toggle_drop_open_mode(self) -> None:
        self.set_drop_open_mode("new_window" if self.drop_open_mode == "active_window" else "active_window")

    def set_toolbar_mode(self, mode: str) -> None:
        mode = {"ribbon": "tabbed", "retro": "classic"}.get(mode, mode)
        if mode not in {"tabbed", "classic"}: return
        self.toolbar_mode = mode
        self._apply_toolbar_mode(); self.persist_preferences()

    def _apply_toolbar_mode(self) -> None:
        tabbed = self.toolbar_mode == "tabbed"
        self.tabbed_container.setVisible(tabbed)
        self.classic_toolbar.setVisible(not tabbed)
        self.menuBar().setVisible(True)
        self.tabbed_mode_action.setChecked(tabbed); self.classic_mode_action.setChecked(not tabbed)
        self._sync_compact_toolbar_toggles()

    def set_drop_open_mode(self, mode: str) -> None:
        if mode not in {"active_window", "new_window"}: return
        self.drop_open_mode = mode
        self.drop_active_action.setChecked(mode == "active_window")
        self.drop_new_window_action.setChecked(mode == "new_window")
        self._sync_compact_toolbar_toggles()
        self.persist_preferences()

    @staticmethod
    def _is_appimage_runtime() -> bool:
        """True only for the mounted final AppImage runtime, never Portable/source."""
        return bool(os.environ.get("APPIMAGE"))

    def _style_appimage_overflow_button(self, toolbar: QToolBar) -> None:
        """Make Qt's native toolbar overflow control legible inside AppImage.

        Portable/source runs intentionally keep the host style untouched because their
        overflow controls already render correctly.
        """
        if not self._is_appimage_runtime():
            return
        extension = toolbar.findChild(QToolButton, "qt_toolbar_ext_button")
        if extension is None:
            return
        extension.setArrowType(Qt.ArrowType.NoArrow)
        extension.setText("›")
        extension.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        extension.setAutoRaise(False)
        extension.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        extension.setMinimumWidth(28)
        extension.setMaximumWidth(32)
        font = extension.font()
        font.setBold(True)
        font.setPointSize(max(18, font.pointSize()))
        extension.setFont(font)
        if self._effective_scheme() == "dark":
            fg, bg, border = "#F1F3F4", "#34383D", "#7C858D"
        else:
            fg, bg, border = "#202124", "#F1F3F4", "#7A838A"
        extension.setStyleSheet(
            "QToolButton {"
            f"color: {fg}; background: {bg}; border: 1px solid {border};"
            "border-radius: 4px; padding: 0px; margin: 1px;"
            "}"
            "QToolButton:hover { border-width: 2px; }"
        )
        extension.setToolTip("More commands")

    def _refresh_appimage_overflow_buttons(self) -> None:
        if not self._is_appimage_runtime():
            return
        for toolbar in getattr(self, "tabbed_toolbars", []):
            self._style_appimage_overflow_button(toolbar)
        if hasattr(self, "classic_toolbar"):
            self._style_appimage_overflow_button(self.classic_toolbar)

    def _apply_toolbar_button_style(self) -> None:
        """Keep Tabbed and Classic toolbars icon-only with identical geometry."""
        for toolbar in getattr(self, "tabbed_toolbars", []):
            toolbar.setIconSize(QSize(36, 36))
            toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        for button in getattr(self, "tabbed_buttons", []):
            self._style_command_button(button, tabbed=True)
        if hasattr(self, "classic_toolbar"):
            self.classic_toolbar.setIconSize(QSize(36, 36))
            self.classic_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            for action in self.classic_toolbar.actions():
                widget = self.classic_toolbar.widgetForAction(action)
                if isinstance(widget, QToolButton):
                    self._style_command_button(widget, tabbed=False)
                    self._enable_toolbar_context_menu(widget)
        # The AppImage uses a self-contained Qt style, so explicitly enhance only
        # its native extension control; Portable/source remains host-native.
        QTimer.singleShot(0, self._refresh_appimage_overflow_buttons)

    def _collapsed_tabbed_height(self) -> int:
        bar = self.tabbed_tabs.tabBar(); return max(bar.height(), bar.sizeHint().height(), 1) + 2

    def _sync_collapsed_tabbed_page(self, _index=None) -> None:
        if not getattr(self, "_tabbed_collapsed", False): return
        current = self.tabbed_tabs.currentWidget()
        if current is not None: current.setVisible(False)

    def set_tabbed_collapsed(self, collapsed: bool, *, persist: bool = True) -> None:
        collapsed = bool(collapsed)
        if collapsed == getattr(self, "_tabbed_collapsed", False): return
        self._tabbed_collapsed = collapsed; current = self.tabbed_tabs.currentWidget()
        if collapsed:
            if current is not None: current.setVisible(False)
            height = self._collapsed_tabbed_height(); self.tabbed_tabs.setMinimumHeight(height); self.tabbed_tabs.setMaximumHeight(height)
            self.statusBar().showMessage("Tabbed controls hidden. Click a tab title once to reveal them.", 3000)
        else:
            self.tabbed_tabs.setMaximumHeight(self._tabbed_expanded_maximum_height); self.tabbed_tabs.setMinimumHeight(self._tabbed_expanded_minimum_height)
            if current is not None: current.setVisible(True)
            self.statusBar().showMessage("Tabbed controls revealed.", 2000)
        self.tabbed_tabs.updateGeometry()
        if persist and hasattr(self, "settings"): self.persist_preferences()
