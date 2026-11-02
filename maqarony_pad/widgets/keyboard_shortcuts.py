#!/usr/bin/env python3
"""Existing MaqaronyPad keyboard-shortcut dialog query helpers."""
from __future__ import annotations

import re


_SHORTCUT_TOKEN_RE = re.compile(r"[a-z0-9]+|[^\w\s+]", re.IGNORECASE)
_SHORTCUT_TOKEN_ALIASES = {
    "control": "ctrl",
    "ctrl": "ctrl",
    "ctl": "ctrl",
}


def _shortcut_tokens(value: str) -> tuple[str, ...]:
    """Return comparable shortcut tokens without imposing modifier order."""
    return tuple(
        _SHORTCUT_TOKEN_ALIASES.get(token, token)
        for token in _SHORTCUT_TOKEN_RE.findall(value.casefold())
    )


def _shortcut_query_matches(query: str, shortcut_tokens: tuple[str, ...]) -> bool:
    """Match aliases, optional plus signs and reordered shortcut modifiers."""
    query_tokens = _shortcut_tokens(query)
    return bool(query_tokens) and all(
        token in shortcut_tokens for token in query_tokens
    )

import importlib.util as _importlib_util
# Retain dependency-free shortcut search for QA without a Qt installation.
if _importlib_util.find_spec("PyQt6") is not None:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QAction, QKeySequence
    from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QMenu, QTableWidget, QTableWidgetItem, QVBoxLayout)


def _shortcut_catalog(self) -> dict[str, list[tuple[str, QAction | str]]]:
    """Return every assigned shortcut, grouped by the live AppMenu taxonomy.

    AppMenu actions are collected recursively so nested menu commands stay
    synchronized with the Keyboard Shortcuts dialog automatically. Only
    shortcuts that intentionally have no AppMenu QAction are appended
    explicitly below.
    """

    def collect(menu: QMenu) -> list[tuple[str, QAction | str]]:
        entries: list[tuple[str, QAction | str]] = []
        for action in menu.actions():
            submenu = action.menu()
            if submenu is not None:
                entries.extend(collect(submenu))
                continue
            if action.shortcut().toString(
                QKeySequence.SequenceFormat.NativeText
            ).strip():
                entries.append((action.text(), action))
        return entries

    catalog: dict[str, list[tuple[str, QAction | str]]] = {
        "File": collect(self.file_menu),
        "Edit": collect(self.edit_menu),
        "Markdown": collect(self.markdown_menu),
        "Insert": collect(self.insert_menu),
        "View": collect(self.view_menu),
        "Settings": collect(self.settings_menu),
        "Help": collect(self.help_menu),
    }

    # These shortcuts are intentionally not represented by AppMenu QActions.
    catalog["Edit"].extend((
        ("Find Next", self.find_next_action),
        ("Find Previous", self.find_previous_action),
        ("Close Find/Replace", self.dismiss_find_action),
        ("Toggle Overwrite Mode", "Insert"),
    ))
    catalog["View"].extend((
        ("Toggle Editor Toolbar", self.toolbar_mode_shortcut_action),
        ("Next Tabbed Tab", self.next_tabbed_tab_action),
        ("Previous Tabbed Tab", self.previous_tabbed_tab_action),
    ))
    return catalog


def show_shortcuts(self) -> None:
    """Show the live shortcut inventory with Plus-style fuzzy filtering."""
    if self.shortcuts_dialog is not None:
        self.shortcuts_dialog.show()
        self.shortcuts_dialog.raise_()
        self.shortcuts_dialog.activateWindow()
        return

    dialog = QDialog(self)
    dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    dialog.setWindowTitle(dialog_title("Keyboard Shortcuts"))
    dialog.setWindowIcon(self.windowIcon())
    dialog.setModal(False)
    dialog.resize(700, 560)

    outer = QVBoxLayout(dialog)
    filter_row = QHBoxLayout()
    search = QLineEdit(dialog)
    search.setPlaceholderText("Search commands or shortcuts")
    search.setClearButtonEnabled(True)
    search.setAccessibleName("Search keyboard shortcuts")
    catalog = self._shortcut_catalog()
    category = QComboBox(dialog)
    category.setAccessibleName("Shortcut menu")
    category.addItems(["All", *catalog.keys()])
    category.setCurrentIndex(0)
    filter_row.addWidget(search, 1)
    filter_row.addWidget(QLabel("Menu:", dialog))
    filter_row.addWidget(category)
    outer.addLayout(filter_row)

    rows: list[tuple[str, str, str, str, tuple[str, ...]]] = []
    seen: set[tuple[str, str]] = set()
    for menu_name, entries in catalog.items():
        for label, action_or_shortcut in entries:
            shortcut = (
                action_or_shortcut.shortcut().toString(
                    QKeySequence.SequenceFormat.NativeText
                )
                if isinstance(action_or_shortcut, QAction)
                else str(action_or_shortcut).strip()
            )
            clean_label = label.replace("&", "").replace("…", "").strip()
            if not shortcut or not clean_label or (clean_label, shortcut) in seen:
                continue
            seen.add((clean_label, shortcut))
            rows.append((
                menu_name,
                clean_label,
                shortcut,
                clean_label.casefold(),
                _shortcut_tokens(shortcut),
            ))
    rows.sort(key=lambda row: row[1].casefold())

    table = QTableWidget(len(rows), 2, dialog)
    table.setHorizontalHeaderLabels(["Command", "Shortcut"])
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setVisible(False)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    for row_index, (_menu_name, label, shortcut, _label_search, _shortcut_tokens_value) in enumerate(rows):
        table.setItem(row_index, 0, QTableWidgetItem(label))
        table.setItem(row_index, 1, QTableWidgetItem(shortcut))
    table.resizeColumnsToContents()
    outer.addWidget(table, 1)

    no_matches = QLabel("No matching shortcuts.", dialog)
    no_matches.setAlignment(Qt.AlignmentFlag.AlignCenter)
    no_matches.hide()
    outer.addWidget(no_matches)

    def apply_filter() -> None:
        query = search.text().strip().casefold()
        selected = category.currentText()
        any_visible = False
        for row_index, (menu_name, _label, _shortcut, label_search, shortcut_tokens) in enumerate(rows):
            row_visible = (
                (selected == "All" or selected == menu_name)
                and (
                    not query
                    or query in label_search
                    or _shortcut_query_matches(query, shortcut_tokens)
                )
            )
            table.setRowHidden(row_index, not row_visible)
            any_visible = any_visible or row_visible
        table.setVisible(any_visible)
        no_matches.setVisible(not any_visible)

    search.textChanged.connect(apply_filter)
    category.currentTextChanged.connect(apply_filter)
    apply_filter()

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, dialog)
    ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
    if ok_button is not None:
        ok_button.setText("OK")
    buttons.accepted.connect(dialog.close)
    outer.addWidget(buttons)
    dialog.finished.connect(lambda _result: setattr(self, "shortcuts_dialog", None))
    self.shortcuts_dialog = dialog
    dialog.show()
    dialog.raise_()
    dialog.activateWindow()
    search.setFocus(Qt.FocusReason.ShortcutFocusReason)
