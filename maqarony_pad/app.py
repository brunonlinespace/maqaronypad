#!/usr/bin/env python3
# ==============================================================================
# MaqaronyPad - focused Markdown editor
# Copyright (C) 2026 Bruno Machado
# GPLv3-or-later
# ==============================================================================
from __future__ import annotations

import argparse
import html
import locale
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QEvent, QFileSystemWatcher, QSize, Qt, QTimer, QUrl
from PyQt6.QtGui import (
    QAction, QActionGroup, QColor, QDesktopServices, QFont, QFontDatabase,
    QIcon, QKeySequence, QPalette, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat,
)
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import (
    QApplication, QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFontDialog, QFormLayout, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QInputDialog,
    QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton, QScrollArea,
    QSizePolicy, QSpinBox, QSplitter, QStatusBar, QTabWidget, QTableWidget, QTableWidgetItem,
    QToolBar, QToolButton, QVBoxLayout, QWizard, QWizardPage, QWidget,
)

from document_io import (
    MAX_FILE_BYTES, SUPPORTED_EXTENSIONS, FileSnapshot, FileStateChangedError,
    absolute_user_path, current_file_state, encode_document, fsync_directory, load_document,
    path_lexists, read_regular_file, rename_path_no_replace,
    safe_atomic_save, write_new_bytes,
)
from legacy_ricopad import strip_legacy_envelope
from widgets.mwpyn.editor_preview import MarkdownPreview
from widgets.mwpyn.editor_source import MarkopadSourceEditor
from widgets.mwpyn.character_count import count_markdown_characters
from settings_io import load_settings, save_settings
import editor_platform_startup as _editor_platform_startup
from editor_platform_startup import (program_dir, project_root, asset_path, application_icon, host_process_environment, parse_args, main)

APP_NAME = "MaqaronyPad"
APP_VERSION = "1.0.2"
APP_ID = "maqaronypad"
APP_ORG = "brunonlinespace"
ORGANIZATION_DOMAIN = "github.com/brunonlinespace"
DESKTOP_ID = "maqaronypad"
APP_TAGLINE = "Friendly. Fast. Focused."
CONFIG_DIR = Path.home() / ".config" / APP_ORG / APP_ID
CONFIG_FILE = CONFIG_DIR / "maqaronypad.json"
MAX_SEARCH_MATCHES = 10_000
MAX_SEARCH_QUERY_CHARACTERS = 4096
GITHUB_URL = "https://github.com/brunonlinespace/maqaronypad"
ISSUES_URL = GITHUB_URL + "/issues"
CLASSIC_TOOLBAR_DEFAULT = [
    # Selected by default; rebuild_classic_toolbar() renders them in AppMenu order.
    "new", "open", "save", "exit",
    "undo", "redo", "find",
    "bold", "italic", "inline_code",
    "image", "link",
    "source", "split", "preview", "editor_toolbar",
]

def dialog_title(name: str) -> str:
    """Pad-family title convention: window/dialog name followed by application name."""
    return f"{name} — {APP_NAME}"


def load_json_settings() -> dict:
    return load_settings(CONFIG_FILE)


def save_json_settings(data: dict) -> None:
    save_settings(CONFIG_FILE, data)




def apply_theme(app: QApplication, theme: str) -> None:
    theme = theme if theme in {"system", "dark", "light"} else "system"
    app.setStyleSheet("")
    app.setPalette(app.style().standardPalette())
    if theme == "system":
        return
    palette = QPalette()
    if theme == "dark":
        palette.setColor(QPalette.ColorRole.Window, QColor("#202326"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#F1F3F4"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#151719"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#202326"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#F1F3F4"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#101214"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#F1F3F4"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#292D31"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F1F3F4"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#158B86"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#8E969E"))
    else:
        # Marko-family Light application palette. Keep application chrome
        # independent from the persisted Dark Editor canvas preference.
        palette = app.style().standardPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#D4D4D4"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#2A2A2A"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#F4F4F4"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#E4E4E4"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#F4F4F4"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#2A2A2A"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#2A2A2A"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#E4E4E4"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#2A2A2A"))
        palette.setColor(QPalette.ColorRole.Light, QColor("#F4F4F4"))
        palette.setColor(QPalette.ColorRole.Midlight, QColor("#D0D0D0"))
        palette.setColor(QPalette.ColorRole.Mid, QColor("#B2B2B2"))
        palette.setColor(QPalette.ColorRole.Dark, QColor("#767676"))
        palette.setColor(QPalette.ColorRole.Shadow, QColor("#545454"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#0B8781"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#767676"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#0068A6"))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#0068A6"))
    app.setPalette(palette)


class EditorMessageStatusBar(QStatusBar):
    """Keep editor feedback at left without hiding document indicators."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.message_label = QLabel("", self)
        self.message_label.setMinimumWidth(0)
        self.message_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.message_label.setToolTip("")
        self._message_timer = QTimer(self)
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self.clearMessage)

    def showMessage(self, message, timeout=4000, *, warning_id=None):
        from widgets.message_conventions import (
            DEFAULT_MESSAGE_DURATION_MS, is_critical_status, status_sentence,
        )
        text = status_sentence(message)
        critical = is_critical_status(text)
        recovering = text.startswith(("Loaded ", "Saved ", "Saved as ", "Saved MaqaronyPad version as ", "Deleted "))
        if getattr(self, "_critical_editor_message", False) and not (critical or recovering):
            return
        self._critical_editor_message = critical
        # A warning's owner is supplied by its producer, not inferred from
        # message wording. Routine/recovery messages own no warning identity.
        self._warning_id = warning_id if critical else None
        self.message_label.setText(text)
        self.message_label.setToolTip(text)
        self._message_timer.stop()
        if not critical:
            self._message_timer.start(DEFAULT_MESSAGE_DURATION_MS)

    def clearMessage(self, *, warning_id=None):
        # Backing-file recovery must never dismiss another unresolved warning.
        if warning_id is not None and getattr(self, "_warning_id", None) != warning_id:
            return
        self._message_timer.stop()
        self._critical_editor_message = False
        self._warning_id = None
        self.message_label.clear()
        self.message_label.setToolTip("")


class FindPanel(QFrame):
    def __init__(self, window: "MaqaronyPadWindow") -> None:
        super().__init__(window)
        self.window = window
        self.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QGridLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        self.find_edit = QLineEdit(self)
        self.find_edit.setMaxLength(MAX_SEARCH_QUERY_CHARACTERS)
        self.find_edit.setPlaceholderText("Find")
        self.replace_edit = QLineEdit(self)
        self.replace_edit.setPlaceholderText("Replace")
        self.case_box = QCheckBox("Match case", self)
        self.count_label = QLabel("", self)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.previous_button = QPushButton("Previous", self)
        self.next_button = QPushButton("Next", self)
        repl_btn = QPushButton("Replace", self)
        all_btn = QPushButton("Replace All", self)
        close_btn = QPushButton("Close", self)
        layout.addWidget(self.find_edit, 0, 0, 1, 3)
        layout.addWidget(self.previous_button, 0, 3)
        layout.addWidget(self.next_button, 0, 4)
        layout.addWidget(self.case_box, 0, 5)
        layout.addWidget(self.count_label, 0, 6)
        layout.addWidget(self.replace_edit, 1, 0, 1, 3)
        layout.addWidget(repl_btn, 1, 3)
        layout.addWidget(all_btn, 1, 4)
        layout.addWidget(close_btn, 1, 6)
        self.find_edit.textChanged.connect(window.refresh_search)
        self.case_box.toggled.connect(window.refresh_search)
        self.find_edit.returnPressed.connect(window.find_next)
        self.previous_button.clicked.connect(window.find_previous)
        self.next_button.clicked.connect(window.find_next)
        repl_btn.clicked.connect(window.replace_one)
        all_btn.clicked.connect(window.replace_all)
        close_btn.clicked.connect(window.hide_find_panel)
        self.hide()


import widgets.mwpyn.editor_lifecycle as _editor_lifecycle
from widgets.mwpyn.editor_lifecycle import EditorLifecycleMixin
_editor_lifecycle.dialog_title = dialog_title
_editor_lifecycle.save_json_settings = save_json_settings
from widgets.window_search_view import WindowSearchViewMixin
import widgets.mwpyn.editor_printing as _editor_printing
_editor_printing.dialog_title = dialog_title
from widgets.mwpyn.editor_printing import EditorPrintingMixin
import widgets.mwpyn.editor_preferences as _editor_preferences
from widgets.mwpyn.editor_preferences import EditorPreferencesMixin
import widgets.editor_ribbon_retro as _editor_ribbon_retro
from widgets.editor_ribbon_retro import EditorRibbonRetroMixin
_editor_ribbon_retro.CLASSIC_TOOLBAR_DEFAULT = CLASSIC_TOOLBAR_DEFAULT
_editor_ribbon_retro.dialog_title = dialog_title
_editor_ribbon_retro.asset_path = asset_path
# Preserve the original persistence helper without using the module before import.
_editor_preferences.save_json_settings = save_json_settings
import widgets.editor_commands_appearance as _editor_commands_appearance
from widgets.editor_commands_appearance import EditorCommandsAppearanceMixin
# Preserve the original main-module globals used by the relocated methods.
_editor_commands_appearance.APP_NAME = APP_NAME
_editor_commands_appearance.asset_path = asset_path
_editor_commands_appearance.dialog_title = dialog_title
_editor_commands_appearance.save_json_settings = save_json_settings
_editor_commands_appearance.apply_theme = apply_theme

# Existing dialog methods live in function-only UI modules; no new dialog classes.
import widgets.about_dialog as _about_dialog
import widgets.quick_tour as _quick_tour
import widgets.keyboard_shortcuts as _keyboard_shortcuts
_about_dialog.APP_NAME = APP_NAME
_about_dialog.APP_TAGLINE = APP_TAGLINE
_about_dialog.APP_VERSION = APP_VERSION
_about_dialog.CONFIG_FILE = CONFIG_FILE
_about_dialog.GITHUB_URL = GITHUB_URL
_about_dialog.application_icon = application_icon
_about_dialog.asset_path = asset_path
_about_dialog.dialog_title = dialog_title
_keyboard_shortcuts.dialog_title = dialog_title

class MaqaronyPadWindow(EditorLifecycleMixin, EditorCommandsAppearanceMixin, EditorRibbonRetroMixin, EditorPreferencesMixin, EditorPrintingMixin, WindowSearchViewMixin, QMainWindow):
    show_about = _about_dialog.show_about
    show_quick_tour = _quick_tour.show_quick_tour
    _shortcut_catalog = _keyboard_shortcuts._shortcut_catalog
    show_shortcuts = _keyboard_shortcuts.show_shortcuts
    def __init__(self, initial_path: str | None = None, *, theme_override: str | None = None) -> None:
        super().__init__()
        self.settings = load_json_settings()
        # Privacy migration: r1 briefly remembered recently opened files. MaqaronyPad r2
        # never keeps that history; delete the obsolete preference if it exists.
        if "recent_files" in self.settings:
            self.settings.pop("recent_files", None)
            save_json_settings(self.settings)
        self.theme = theme_override or str(self.settings.get("theme", "light"))
        self.icon_family = str(self.settings.get("icon_family", "harmony"))
        if self.icon_family not in {"harmony", "humility", "heritage", "halcyon"}:
            self.icon_family = "harmony"
        # 0.0.2 renames the user-facing toolbar modes. Migrate the old
        # Ricopad-era preference names without losing the user's selection.
        stored_toolbar = str(self.settings.get("toolbar", self.settings.get("interface", "tabbed")))
        stored_toolbar = {"ribbon": "tabbed", "retro": "classic"}.get(stored_toolbar, stored_toolbar)
        self.toolbar_mode = stored_toolbar if stored_toolbar in {"tabbed", "classic"} else "tabbed"
        self.settings.pop("interface", None)
        self.settings.pop("button_labels", None)
        self.settings.pop("external_editor", None)
        self.view_mode = str(self.settings.get("view_mode", "split"))
        if self.view_mode not in {"source", "split", "preview"}:
            self.view_mode = "split"
        stored_editable_view = str(self.settings.get("last_editable_view_mode", ""))
        if stored_editable_view not in {"source", "split"}:
            stored_editable_view = self.view_mode if self.view_mode in {"source", "split"} else "split"
        self.last_editable_view_mode = stored_editable_view
        # Item 32: remember the user's last real text surface. Menus/toolbars can
        # temporarily take Qt focus, but commands must still respect whether the
        # user was interacting with Source or Preview.
        self._active_text_surface = "preview" if self.view_mode == "preview" else "source"
        self.drop_open_mode = str(self.settings.get("drop_open_mode", "active_window"))
        if self.drop_open_mode not in {"active_window", "new_window"}:
            self.drop_open_mode = "active_window"
        self.editor_canvas_light = bool(self.settings.get("editor_canvas_light", True))
        stored_classic = self.settings.get("classic_toolbar_items", self.settings.get("retro_toolbar_items", CLASSIC_TOOLBAR_DEFAULT))
        self.classic_toolbar_items = (
            [str(item) for item in stored_classic]
            if isinstance(stored_classic, list) else list(CLASSIC_TOOLBAR_DEFAULT)
        )
        # 0.2.2 condenses the old mutually-exclusive Classic drag/drop pair into
        # one compact toggle without losing an existing user's toolbar choice.
        if any(item in self.classic_toolbar_items for item in ("drop_active", "drop_new_window")):
            self.classic_toolbar_items = [
                item for item in self.classic_toolbar_items
                if item not in {"drop_active", "drop_new_window"}
            ]
            if "drop_mode" not in self.classic_toolbar_items:
                self.classic_toolbar_items.append("drop_mode")
        # 0.2.6 replaces the synthetic Tabbed/Classic toolbar toggle and separate
        # Classic-customisation button with one Editor Toolbar flyout. Preserve an
        # existing Classic selection by mapping either historical control to the
        # new flyout at the first matching position.
        legacy_toolbar_items = {"toolbar_style", "customize_classic"}
        if any(item in self.classic_toolbar_items for item in legacy_toolbar_items):
            migrated: list[str] = []
            inserted = False
            for item in self.classic_toolbar_items:
                if item in legacy_toolbar_items:
                    if not inserted:
                        migrated.append("editor_toolbar")
                        inserted = True
                    continue
                migrated.append(item)
            self.classic_toolbar_items = migrated
        self.settings.pop("retro_toolbar_items", None)
        self.about_dialog: QDialog | None = None
        self.shortcuts_dialog: QDialog | None = None
        self.tutorial_dialog: QWizard | None = None
        self.tutorial_seen = bool(self.settings.get("tutorial_seen", False))
        self.current_path: Path | None = None
        # For normal files this is the same location. When a document was opened
        # through a symlink, current_path retains MaqaronyPad's historical resolved
        # document path while backing_path retains the opened path entry solely
        # for change detection and safe save-through-symlink validation.
        self.backing_path: Path | None = None
        self.file_encoding = "utf-8"
        self.file_bom = b""
        self.file_newline = "\n"
        self.disk_signature = None
        self.disk_snapshot: FileSnapshot | None = None
        self.backing_state = "normal"
        self._overwrite_snapshot: FileSnapshot | None = None
        self.legacy_ricopad_loaded = False
        self._loading = False
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.fileChanged.connect(self._queue_backing_check)
        self.file_watcher.directoryChanged.connect(self._queue_backing_check)
        self.backing_check_timer = QTimer(self)
        self.backing_check_timer.setSingleShot(True)
        self.backing_check_timer.setInterval(160)
        self.backing_check_timer.timeout.connect(self.handle_backing_path_event)
        self._search_matches: list[tuple[int, int]] = []
        self._current_search_index = -1
        self._search_results_truncated = False
        self._search_refresh_suspended = False
        self.zoom_percent = int(self.settings.get("zoom", 100))
        self.zoom_percent = max(50, min(300, self.zoom_percent))
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(180)
        self.preview_timer.timeout.connect(self.refresh_preview_now)
        self.setWindowIcon(application_icon())
        self.setAcceptDrops(True)
        self.resize(1180, 760)
        self.setMinimumSize(720, 480)

        # Cache the grapheme-cluster count for the Markdown source document.
        # Cursor-only movement must never trigger a document-wide recount.
        self._cached_status_char_count = None
        self._create_actions()
        self._create_menus()
        self._create_central_ui()
        self._create_tabbed_toolbar()
        self._create_classic_toolbar()
        self._create_status_bar()
        self._restore_preferences()
        self._apply_toolbar_mode()
        self._apply_editor_appearance()
        self._update_ui_state()
        QApplication.instance().installEventFilter(self)

        if initial_path:
            QTimer.singleShot(0, lambda: self.open_path(initial_path))
        else:
            self.new_document(force=True)
        if not self.tutorial_seen:
            QTimer.singleShot(0, self.show_quick_tour)

    # ---------- action / UI construction ----------


    def _create_central_ui(self) -> None:
        central = QWidget(self)
        outer = QVBoxLayout(central); outer.setContentsMargins(0, 0, 0, 0); outer.setSpacing(0)
        self.tabbed_container = QWidget(central)
        self.tabbed_layout = QVBoxLayout(self.tabbed_container); self.tabbed_layout.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.tabbed_container)

        self.editor = MarkopadSourceEditor(central)
        self.editor.setObjectName("maqaronyPadSourceEditor")
        self.comment_action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.editor.addAction(self.comment_action)
        self.preview = MarkdownPreview(central)
        self.preview.setObjectName("maqaronyPadPreview")
        self.preview.setAcceptDrops(False)
        self.preview.missing_link_requested.connect(
            lambda: self.statusBar().showMessage("The linked file could not be found.", 4000)
        )
        self.splitter = QSplitter(Qt.Orientation.Horizontal, central)
        self.splitter.addWidget(self.editor); self.splitter.addWidget(self.preview)
        self.splitter.setStretchFactor(0, 3); self.splitter.setStretchFactor(1, 2)
        self.external_banner = QFrame(central)
        self.external_banner.setFrameShape(QFrame.Shape.StyledPanel)
        banner_layout = QHBoxLayout(self.external_banner)
        self.external_label = QLabel("This file changed on disk after it was opened.", self.external_banner)
        self.external_label.setWordWrap(True)
        banner_layout.addWidget(self.external_label, 1)
        self.reload_external_button = QPushButton("Reload from Disk", self.external_banner)
        self.reload_external_button.clicked.connect(self.reload_external_change)
        self.save_version_button = QPushButton("Save Version As…", self.external_banner)
        self.save_version_button.clicked.connect(self.save_version_as)
        banner_layout.addWidget(self.reload_external_button)
        banner_layout.addWidget(self.save_version_button)
        self.external_banner.hide()
        outer.addWidget(self.external_banner)
        outer.addWidget(self.splitter, 1)
        self.find_panel = FindPanel(self)
        outer.addWidget(self.find_panel)
        self.setCentralWidget(central)

        self.editor.textChanged.connect(self._on_text_changed)
        self.editor.cursorPositionChanged.connect(self.update_status)
        self.editor.document().modificationChanged.connect(lambda _m: self._update_ui_state())
        self.editor.document().undoAvailable.connect(lambda _available: self._sync_undo_redo_state())
        self.editor.document().redoAvailable.connect(lambda _available: self._sync_undo_redo_state())
        self.editor.paste_rejected.connect(lambda msg: self.statusBar().showMessage(msg, 6000))
        self.editor.view_only_edit_attempt.connect(lambda: self.statusBar().showMessage("Editing is disabled while Locked Mode is enabled.", 3000))
        self.editor.overwrite_mode_changed.connect(self._on_editor_overwrite_mode_changed)
        self.editor.files_dropped.connect(self._handle_dropped_files)









    def _create_status_bar(self) -> None:
        bar = EditorMessageStatusBar(self); self.setStatusBar(bar)
        self.status_indicators_label = QLabel("", bar)
        self.status_indicators_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_indicators_label.setMinimumWidth(0)
        bar.addWidget(bar.message_label, 1)
        bar.addPermanentWidget(self.status_indicators_label)

    def _on_editor_overwrite_mode_changed(self, enabled: bool) -> None:
        self.update_status()
        self.statusBar().showMessage(
            "Overwrite mode enabled." if enabled else "Insert mode enabled.", 2500
        )

    # ---------- preferences / appearance ----------
    def _apply_presentation_safely(self, callback) -> None:
        """Run presentation-only work without changing the source document dirty state."""
        document = self.editor.document()
        was_modified = bool(document.isModified())
        callback()
        if bool(document.isModified()) != was_modified:
            document.setModified(was_modified)
        self._update_ui_state()





















    def toggle_status_bar(self, checked: bool) -> None:
        self.statusBar().setVisible(bool(checked)); self.persist_preferences()



    def toggle_fullscreen(self, checked: bool) -> None:
        self.showFullScreen() if bool(checked) else self.showNormal()

    def toggle_locked_mode(self, checked: bool) -> None:
        requested = bool(checked)
        should_confirm = bool(self.settings.get("confirm_locked_mode_disable", True))
        if self.editor.isReadOnly() and not requested and should_confirm:
            dialog = QMessageBox(self)
            dialog.setWindowTitle(dialog_title("Disable Locked Mode?"))
            dialog.setIcon(QMessageBox.Icon.Warning)
            dialog.setText("Locked Mode protects files from accidental changes.")
            dialog.setInformativeText("Continue only when you intend to edit the document.")
            dont_ask = QCheckBox("Don't ask again when disabling Locked Mode", dialog)
            dialog.setCheckBox(dont_ask)
            keep = dialog.addButton("Keep Locked", QMessageBox.ButtonRole.RejectRole)
            cont = dialog.addButton("Continue", QMessageBox.ButtonRole.AcceptRole)
            dialog.setDefaultButton(keep); dialog.setEscapeButton(keep); dialog.exec()
            if dialog.clickedButton() is not cont:
                self.view_only_action.blockSignals(True); self.view_only_action.setChecked(True); self.view_only_action.blockSignals(False)
                return
            if dont_ask.isChecked():
                self.settings["confirm_locked_mode_disable"] = False
        self.editor.set_view_only(requested)
        self.view_only_action.blockSignals(True); self.view_only_action.setChecked(requested); self.view_only_action.blockSignals(False)
        self.persist_preferences()
        self.statusBar().showMessage("Locked Mode enabled." if requested else "Locked Mode disabled.", 3000)
        self._update_ui_state()








    # ---------- document lifecycle ----------
























    def schedule_preview(self) -> None:
        if self.preview.isVisible(): self.preview_timer.start()

    def _apply_preview_link_color(self, link_color: QColor | None = None) -> None:
        if link_color is None:
            link_color = QColor("#174EA6" if self.editor_canvas_light else "#82AAFF")
        document = self.preview.document()
        cursor = QTextCursor(document)
        cursor.beginEditBlock()
        block = document.firstBlock()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.isValid() and fragment.charFormat().isAnchor():
                    cursor.setPosition(fragment.position())
                    cursor.setPosition(
                        fragment.position() + fragment.length(), QTextCursor.MoveMode.KeepAnchor
                    )
                    fmt = fragment.charFormat()
                    fmt.setForeground(link_color)
                    cursor.setCharFormat(fmt)
                iterator += 1
            block = block.next()
        cursor.endEditBlock()

    def _apply_preview_quote_effect(self) -> None:
        if not bool(self.settings.get("preview_italic_quotes", False)) or self._preview_base_font().italic():
            return
        document = self.preview.document()
        cursor = QTextCursor(document)
        italic = QTextCharFormat()
        italic.setFontItalic(True)
        cursor.beginEditBlock()
        block = document.firstBlock()
        while block.isValid():
            if block.blockFormat().hasProperty(QTextFormat.Property.BlockQuoteLevel):
                cursor.setPosition(block.position())
                cursor.setPosition(
                    block.position() + max(0, block.length() - 1), QTextCursor.MoveMode.KeepAnchor
                )
                if cursor.hasSelection():
                    cursor.mergeCharFormat(italic)
            block = block.next()
        cursor.endEditBlock()

    def refresh_preview_now(self) -> None:
        if not self.preview.isVisible():
            return
        self.preview.render_markdown(self.editor.toPlainText())
        self._apply_preview_link_color()
        self._apply_preview_quote_effect()

    def _on_text_changed(self) -> None:
        # Also invalidate during programmatic loads, while _loading is true.
        self._cached_status_char_count = None
        if self._loading: return
        self.schedule_preview()
        if not self._search_refresh_suspended:
            self.refresh_search()
        self.update_status(); self._update_ui_state()

    # ---------- markdown editing ----------
    def insert_text(self, text: str) -> None:
        if self.editor.isReadOnly() or self.view_mode == "preview": return
        self.editor.insert_guarded_text(text)

    def insert_code_block(self) -> None:
        language, ok = QInputDialog.getText(self, dialog_title("Code Block"), "Language (optional):")
        if ok: self.editor.insert_code_fence(language)

    def insert_link(self) -> None:
        cursor = self.editor.textCursor(); selected = cursor.selectedText().replace("\u2029", " ")
        label, ok = QInputDialog.getText(self, dialog_title("Insert Link"), "Link text:", text=selected or "Link")
        if not ok: return
        url, ok = QInputDialog.getText(self, dialog_title("Insert Link"), "URL:")
        if ok and url.strip(): self.editor.insert_link(label, url.strip())

    def _link_at_cursor(self):
        cursor = self.editor.textCursor(); block = cursor.block(); text = block.text(); pos = cursor.position() - block.position()
        pattern = re.compile(r"(?<!!)\[([^\]]*)\]\(([^\n)]*)\)")
        for match in pattern.finditer(text):
            if match.start() <= pos <= match.end(): return block.position() + match.start(), block.position() + match.end(), match.group(1), match.group(2)
        return None

    def edit_link(self) -> None:
        found = self._link_at_cursor()
        if not found: self.statusBar().showMessage("Place the cursor inside a Markdown link first.", 3500); return
        start, end, label, url = found
        new_label, ok = QInputDialog.getText(self, dialog_title("Edit Link"), "Link text:", text=label)
        if not ok: return
        new_url, ok = QInputDialog.getText(self, dialog_title("Edit Link"), "URL:", text=url)
        if not ok: return
        cursor = QTextCursor(self.editor.document()); cursor.setPosition(start); cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(f"[{new_label.replace(']', r'\]')}]({new_url.replace(' ', '%20').replace(')', r'\)')})")

    def remove_link(self) -> None:
        found = self._link_at_cursor()
        if not found: self.statusBar().showMessage("Place the cursor inside a Markdown link first.", 3500); return
        start, end, label, _url = found
        cursor = QTextCursor(self.editor.document()); cursor.setPosition(start); cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor); cursor.insertText(label)

    def insert_image(self) -> None:
        kind, ok = QInputDialog.getItem(
            self, dialog_title("Image Reference"), "Image source:",
            ["Local file (relative path)", "Web URL"], 0, False
        )
        if not ok:
            return
        if kind.startswith("Web"):
            url, ok = QInputDialog.getText(self, dialog_title("Image URL"), "URL:")
            if not ok or not url.strip():
                return
            reference = url.strip().replace(" ", "%20").replace(")", r"\)")
            alt_default = "Image"
        else:
            if not self.current_path:
                QMessageBox.information(
                    self, dialog_title("Save First"),
                    "Save the Markdown document first so MaqaronyPad can insert a portable relative image path."
                )
                return
            path, _ = QFileDialog.getOpenFileName(
                self, dialog_title("Choose Image"), str(self.current_path.parent),
                "Images (*.png *.jpg *.jpeg *.gif *.webp *.svg);;All Files (*)"
            )
            if not path:
                return
            target = Path(path).resolve()
            try:
                reference = os.path.relpath(target, self.current_path.parent).replace(os.sep, "/")
            except ValueError:
                QMessageBox.warning(
                    self, dialog_title("Portable Image Reference"),
                    "This image cannot be expressed as a relative path from the Markdown document. "
                    "Move/copy it onto the same filesystem and try again."
                )
                return
            reference = reference.replace(" ", "%20").replace(")", r"\)")
            alt_default = target.stem
        alt, ok = QInputDialog.getText(self, dialog_title("Image Description"), "Alternative text:", text=alt_default)
        if not ok:
            return
        safe_alt = alt.replace("]", r"\]")
        self.insert_text(f"![{safe_alt}]({reference})")

    def insert_table(self) -> None:
        dialog = QDialog(self); dialog.setWindowTitle(dialog_title("Table"))
        form = QFormLayout(dialog); rows = QSpinBox(dialog); cols = QSpinBox(dialog); rows.setRange(1, 100); cols.setRange(1, 20); rows.setValue(3); cols.setValue(3)
        form.addRow("Rows:", rows); form.addRow("Columns:", cols)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); form.addRow(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted: self.editor.insert_table(rows.value(), cols.value())

    def _insert_curated_symbol(self, symbol: str, dialog: QDialog | None = None) -> None:
        if self.editor.isReadOnly() or self.view_mode == "preview":
            if dialog is not None:
                dialog.reject()
            return
        if self.editor.insert_guarded_text(symbol):
            if dialog is not None:
                dialog.accept()
            self.editor.setFocus()
            self.editor.ensureCursorVisible()

    def _open_more_symbols(self, dialog: QDialog | None = None) -> None:
        if dialog is not None:
            dialog.accept()
        if sys.platform == "win32":
            system_root = os.environ.get("SystemRoot", r"C:\Windows")
            candidates = (os.path.join(system_root, "System32", "charmap.exe"), "charmap.exe")
            missing = "Windows Character Map could not be found on this system."
        else:
            candidates = ("kcharselect", "gucharmap", "gnome-characters", "charmap")
            missing = (
                "No supported character-map application was found.\n\n"
                "Install KCharSelect, GNOME Characters, or Gucharmap to use this option."
            )
        environment = host_process_environment()
        host_path = environment.get("PATH")
        for command in candidates:
            executable = command if os.path.isfile(command) else shutil.which(command, path=host_path)
            if not executable:
                continue
            try:
                subprocess.Popen(
                    [executable], env=environment, start_new_session=(sys.platform != "win32")
                )
                self.editor.setFocus()
                return
            except OSError:
                continue
        QMessageBox.information(self, dialog_title("More Symbols"), missing)
        self.editor.setFocus()

    def insert_symbol(self) -> None:
        if self.editor.isReadOnly() or self.view_mode == "preview":
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(dialog_title("Symbols"))
        dialog.setModal(True)
        layout = QGridLayout(dialog)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setHorizontalSpacing(5)
        layout.setVerticalSpacing(5)
        symbols = (
            "©", "®", "™", "°", "•", "·", "—", "–",
            "…", "→", "←", "↑", "↓", "✓", "✗", "§",
            "£", "€", "$", "¥", "¢", "±", "×", "÷",
            "≠", "≤", "≥", "≈", "∞", "µ", "¶", "№",
            "★", "☆", "♥", "♦", "♣", "♠", "☐", "☑",
        )
        columns = 8
        for index, symbol in enumerate(symbols):
            button = QToolButton(dialog)
            button.setText(symbol)
            button.setToolTip(f"Insert {symbol}")
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setFixedSize(34, 30)
            button.clicked.connect(
                lambda _checked=False, value=symbol: self._insert_curated_symbol(value, dialog)
            )
            layout.addWidget(button, index // columns, index % columns)
        row = (len(symbols) + columns - 1) // columns
        separator = QFrame(dialog)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator, row, 0, 1, columns)
        more_button = QPushButton("More Symbols…", dialog)
        more_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        more_button.clicked.connect(lambda _checked=False: self._open_more_symbols(dialog))
        layout.addWidget(more_button, row + 1, 0, 1, columns)
        dialog.adjustSize()
        screen = self.screen() or QApplication.primaryScreen()
        if screen is not None:
            geometry = screen.availableGeometry()
            dialog.move(
                geometry.center().x() - dialog.width() // 2,
                geometry.center().y() - dialog.height() // 2,
            )
        dialog.exec()
        self.editor.setFocus()

    def _preview_is_active_text_surface(self) -> bool:
        return (
            self.view_mode in {"split", "preview"}
            and getattr(self, "_active_text_surface", "source") == "preview"
        )

    def _copy_active_text_surface(self) -> None:
        if self._preview_is_active_text_surface():
            self.preview.copy()
        else:
            self.editor.copy()

    def _select_all_active_text_surface(self) -> None:
        if self._preview_is_active_text_surface():
            self.preview.selectAll()
        else:
            self.editor.selectAll()

    def _reset_content_splitter(self) -> None:
        if self.view_mode != "split":
            return
        self._last_splitter_sizes = [3, 2]
        self.splitter.setSizes([3, 2])
        # Persist the resulting canonical 3:2 position immediately.
        self.persist_preferences()

    def paste(self) -> None:
        clipboard = QApplication.clipboard()
        mime = clipboard.mimeData()
        if mime.hasHtml():
            html = mime.html()
            if len(html) > self.editor.MAX_PASTE_CHARACTERS:
                self.statusBar().showMessage("Clipboard HTML is too large to convert safely.", 5000)
                return
            doc = QTextDocument()
            doc.setHtml(html)
            try:
                text = doc.toMarkdown()
            except AttributeError:
                text = doc.toPlainText()
            # Smart Paste must not smuggle large embedded data images into an
            # otherwise ordinary portable text document.
            text = re.sub(
                r"!\[([^\]]*)\]\(data:[^\n)]*\)",
                lambda m: m.group(1) or "[embedded image omitted]",
                text, flags=re.IGNORECASE,
            )
        else:
            text = mime.text() if mime.hasText() else ""
        if not text:
            self.statusBar().showMessage("Clipboard does not contain text that can be pasted.", 3500)
            return
        self.editor.insert_guarded_text(text)

    def delete_selection(self) -> None:
        if self.editor.isReadOnly() or self.view_mode == "preview":
            return
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        elif not cursor.atEnd():
            cursor.deleteChar()


    def delete_current_line(self) -> None:
        if self.editor.isReadOnly() or self.view_mode == "preview": return
        cursor = self.editor.textCursor(); cursor.beginEditBlock(); cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock); cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        if not cursor.atEnd(): cursor.deleteChar()
        elif cursor.position() > 0: cursor.deletePreviousChar()
        cursor.endEditBlock()

    # ---------- search ----------














    def goto_line(self) -> None:
        maximum = max(1, self.editor.document().blockCount()); current = self.editor.textCursor().blockNumber() + 1
        line, ok = QInputDialog.getInt(self, dialog_title("Go To Line"), "Line:", current, 1, maximum)
        if not ok: return
        block = self.editor.document().findBlockByNumber(line - 1); cursor = QTextCursor(block); self.editor.setTextCursor(cursor); self.editor.ensureCursorVisible(); self.editor.setFocus()

    # ---------- file utilities ----------
    def new_window(self) -> None:
        args = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, str(project_root() / "main.py")]
        subprocess.Popen(args, cwd=str(project_root()))










    # ---------- print/export ----------



    # ---------- help ----------



    def show_documentation(self) -> None:
        doc = program_dir()/"docs"/"README.md"; text = doc.read_text(encoding="utf-8") if doc.is_file() else "Documentation is not installed."
        dialog = QDialog(self); dialog.setWindowTitle(dialog_title("Documentation")); dialog.setWindowIcon(self.windowIcon()); dialog.resize(760, 620)
        layout = QVBoxLayout(dialog); view = MarkdownPreview(dialog); view.set_document_path(str(doc) if doc.is_file() else None); view.render_markdown(text); layout.addWidget(view)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, dialog); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons); dialog.exec()

    def open_github_repository(self) -> None:
        QDesktopServices.openUrl(QUrl(GITHUB_URL))

    def report_an_issue(self) -> None:
        QDesktopServices.openUrl(QUrl(ISSUES_URL))


    # ---------- state / events ----------


    def update_status(self) -> None:
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.positionInBlock() + 1
        total_chars = getattr(self, "_cached_status_char_count", None)
        if total_chars is None:
            total_chars = count_markdown_characters(self.editor.document())
            self._cached_status_char_count = total_chars
        mode = "Overwrite" if self.editor.overwriteMode() else "Insert"
        document_text = f"Ln {line}/{self.editor.document().blockCount()} Col {col} Chars {total_chars:,}"
        newline = {"\n": "LF", "\r\n": "CRLF", "\r": "CR"}.get(self.file_newline, "LF")
        view = {"source": "Source", "split": "Split", "preview": "Preview"}.get(self.view_mode, "Split")
        indicators = f"{mode} · {document_text} · {self.file_encoding.upper()} {newline} · {view} {self.zoom_percent}%"
        self.status_indicators_label.setText(indicators)
        self.status_indicators_label.setToolTip(indicators)
    def _handle_dropped_files(self, paths: list) -> None:
        supported = [str(p) for p in paths if Path(str(p)).suffix.lower() in SUPPORTED_EXTENSIONS]
        if not supported: return
        if self.drop_open_mode == "new_window":
            for path in supported: self.new_window_with_file(path)
            return
        self.open_path(supported[0])
        for path in supported[1:]: self.new_window_with_file(path)

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        if event.mimeData().hasUrls() and any(url.isLocalFile() for url in event.mimeData().urls()): event.acceptProposedAction(); return
        event.ignore()

    def dropEvent(self, event) -> None:  # noqa: N802
        paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]; self._handle_dropped_files(paths); event.acceptProposedAction()

    def new_window_with_file(self, path: str) -> None:
        args = [sys.executable, path] if getattr(sys, "frozen", False) else [sys.executable, str(project_root()/"main.py"), path]
        subprocess.Popen(args, cwd=str(project_root()))

    def eventFilter(self, obj, event):  # noqa: N802
        if event.type() == QEvent.Type.FocusIn and isinstance(obj, QWidget) and hasattr(self, "editor"):
            surface = None
            if obj is self.editor or self.editor.isAncestorOf(obj):
                surface = "source"
            elif obj is self.preview or self.preview.isAncestorOf(obj):
                surface = "preview"
            if surface is not None and surface != getattr(self, "_active_text_surface", None):
                self._active_text_surface = surface
                self._update_ui_state()
        if (
            event.type() == QEvent.Type.MouseButtonDblClick
            and hasattr(self, "splitter")
            and obj is self.splitter.handle(1)
            and event.button() == Qt.MouseButton.LeftButton
            and self.view_mode == "split"
        ):
            self._reset_content_splitter()
            event.accept()
            return True
        tabbed_tabs = getattr(self, "tabbed_tabs", None)
        if tabbed_tabs is not None and obj is tabbed_tabs.tabBar():
            if event.type() == QEvent.Type.MouseButtonPress and getattr(self, "_tabbed_collapsed", False) and event.button() == Qt.MouseButton.LeftButton:
                index = tabbed_tabs.tabBar().tabAt(event.position().toPoint())
                if index >= 0: tabbed_tabs.setCurrentIndex(index); self.set_tabbed_collapsed(False); return True
            if event.type() == QEvent.Type.MouseButtonDblClick and not getattr(self, "_tabbed_collapsed", False) and event.button() == Qt.MouseButton.LeftButton and tabbed_tabs.tabBar().tabAt(event.position().toPoint()) >= 0:
                self.set_tabbed_collapsed(True); return True
            if event.type() == QEvent.Type.Wheel:
                delta = event.angleDelta().y() or event.angleDelta().x()
                if delta and tabbed_tabs.count() > 0: tabbed_tabs.setCurrentIndex((tabbed_tabs.currentIndex() + (-1 if delta > 0 else 1)) % tabbed_tabs.count()); return True
        if event.type() == QEvent.Type.ApplicationActivate and self.current_path:
            QTimer.singleShot(0, self.handle_backing_path_event)
        return super().eventFilter(obj, event)

    def closeEvent(self, event) -> None:  # noqa: N802
        if self.maybe_save(): self.persist_preferences(); event.accept()
        else: event.ignore()








def smoke_test(theme: str) -> int:
    """Run real QAction transitions in both AppDir and final frozen AppImage.

    Startup-only checks previously missed a missing-module exception raised
    inside EditorMessageStatusBar.showMessage when switching theme/icon family.
    In PyQt6 an uncaught QAction callback exception may abort the process.
    """
    app = QApplication.instance() or QApplication(["maqaronypad-smoke"])
    apply_theme(app, theme)
    window = MaqaronyPadWindow(theme_override=theme)
    window.editor.load_text("# MaqaronyPad\n\n- [ ] portable\n- [x] source faithful\n")
    window.refresh_preview_now()
    checks = [
        window.editor.toPlainText().startswith("# MaqaronyPad"),
        window.preview.isReadOnly(),
        window.editor.MAX_DOCUMENT_CHARACTERS == 25_000_000,
        APP_NAME == "MaqaronyPad",
        app.applicationVersion() == APP_VERSION,
    ]
    previous_theme = window.theme
    for selected_theme in ("system", "dark", "light"):
        action = getattr(window, f"theme_{selected_theme}_action")
        action.trigger()  # Same Qt signal/slot route as a real AppMenu click.
        checks.extend((window.theme == selected_theme, action.isChecked()))
        checks.append(not window.new_action.icon().isNull())
        if previous_theme != selected_theme:
            checks.append(window.statusBar().message_label.text() == f"Theme: {selected_theme.capitalize()}.")
        previous_theme = selected_theme
    for family in ("harmony", "humility", "heritage", "halcyon"):
        action = window.icon_family_actions[family]
        action.trigger()
        checks.extend((
            window.icon_family == family,
            action.isChecked(),
            window.statusBar().message_label.text() == f"Maqa Icons {family.title()}.",
            not window.new_action.icon().isNull(),
        ))
    window.close()
    return 0 if all(checks) else 3


# Preserve the original late-bound startup globals. Assign only after all are defined.
_editor_platform_startup.APP_ID = APP_ID
_editor_platform_startup.APP_NAME = APP_NAME
_editor_platform_startup.APP_VERSION = APP_VERSION
_editor_platform_startup.APP_ORG = APP_ORG
_editor_platform_startup.ORGANIZATION_DOMAIN = ORGANIZATION_DOMAIN
_editor_platform_startup.DESKTOP_ID = DESKTOP_ID
_editor_platform_startup.MaqaronyPadWindow = MaqaronyPadWindow
_editor_platform_startup.apply_theme = apply_theme
_editor_platform_startup.load_json_settings = load_json_settings
_editor_platform_startup.smoke_test = smoke_test

if __name__ == "__main__":
    raise SystemExit(main())
