#!/usr/bin/env python3
# ==============================================================================
# MaqaronyPad - Markdown source editor
# Copyright (C) 2026 Bruno Machado
# GPLv3-or-later
#
# Generic editor architecture adapted from the Sheepy Pad source-editor core,
# with Markdown-specific highlighter and structural matching inspired by the
# language-aware evolution in Timblee Pad. MaqaronyPad remains fully standalone.
# ==============================================================================

from __future__ import annotations

import re
from dataclasses import dataclass

from PyQt6.QtCore import QMimeData, QRect, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QInputMethodEvent,
    QKeyEvent,
    QKeySequence,
    QPainter,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QSyntaxHighlighter,
)
from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget



from widgets.mwpyn.editor_formatting import EditorFormattingMixin
from widgets.mwpyn.editor_insertion import EditorInsertionMixin
from widgets.mwpyn.editor_widgets import (HighlightRule, MARKDOWN_COLOR_SCHEMES, _scheme, MarkdownHighlighter, LineNumberArea)


from widgets.mwpyn.editor_search_view import EditorSearchViewMixin
class MarkopadSourceEditor(EditorSearchViewMixin, EditorInsertionMixin, EditorFormattingMixin, QPlainTextEdit):
    """Hardened Markdown source editor used by MaqaronyPad."""

    paste_rejected = pyqtSignal(str)
    view_only_edit_attempt = pyqtSignal()
    files_dropped = pyqtSignal(list)
    overwrite_mode_changed = pyqtSignal(bool)

    BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}", ")": "(", "]": "[", "}": "{"}
    OPENING_BRACKETS = "([{" 
    MAX_PASTE_CHARACTERS = 5_000_000
    MAX_DOCUMENT_CHARACTERS = 25_000_000
    MAX_BRACKET_SCAN_CHARACTERS = 250_000
    MAX_FENCE_SCAN_BLOCKS = 20_000

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setUndoRedoEnabled(True)
        self.setCenterOnScroll(False)
        self._line_numbers_visible = True
        self.line_number_area = LineNumberArea(self)
        self._tab_width_spaces = 4
        self._color_scheme = "dark"
        self._search_selections: list[QTextEdit.ExtraSelection] = []
        self._refreshing_extra_selections = False
        self._pending_full_paste: str | None = None
        self._full_paste_generation = 0
        self._highlighter = MarkdownHighlighter(self.document(), self._color_scheme)

        self._decoration_timer = QTimer(self)
        self._decoration_timer.setSingleShot(True)
        self._decoration_timer.setInterval(0)
        self._decoration_timer.timeout.connect(self._refresh_extra_selections)

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._schedule_decoration_refresh)
        self.textChanged.connect(self._schedule_decoration_refresh)
        self.horizontalScrollBar().rangeChanged.connect(
            lambda _minimum, _maximum: QTimer.singleShot(
                0, self._resize_gutter_above_horizontal_scrollbar
            )
        )
        self._update_line_number_area_width()
        self._schedule_decoration_refresh()
        QTimer.singleShot(0, self._resize_gutter_above_horizontal_scrollbar)

    # ---------- presentation ----------











    # ---------- safe mutation ----------
    def set_view_only(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if enabled:
            self._pending_full_paste = None
            self._full_paste_generation += 1
        self.setReadOnly(enabled)
        self._schedule_decoration_refresh()

    def _replacement_fits(self, start: int, end: int, replacement_length: int) -> bool:
        current = max(0, self.document().characterCount() - 1)
        removed = max(0, int(end) - int(start))
        return current - removed + max(0, int(replacement_length)) <= self.MAX_DOCUMENT_CHARACTERS

    def _reject_document_growth(self) -> None:
        self.paste_rejected.emit("The edit would exceed MaqaronyPad's source document safety limit.")

    @staticmethod
    def _is_mutating_key_event(event: QKeyEvent) -> bool:
        if event.key() in (
            Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_Return,
            Qt.Key.Key_Enter, Qt.Key.Key_Tab, Qt.Key.Key_Backtab,
        ):
            return True
        for standard_key in (
            QKeySequence.StandardKey.Cut, QKeySequence.StandardKey.Paste,
            QKeySequence.StandardKey.Undo, QKeySequence.StandardKey.Redo,
        ):
            if event.matches(standard_key):
                return True
        return bool(event.text() and any(ch.isprintable() for ch in event.text()))







    def replace_document_text(self, text: str, *, mark_modified: bool = True) -> bool:
        text = str(text).replace("\x00", "")
        if len(text) > self.MAX_DOCUMENT_CHARACTERS:
            self.paste_rejected.emit("The replacement would exceed MaqaronyPad's source document safety limit.")
            return False
        self._decoration_timer.stop()
        self.setExtraSelections([])
        highlighter = self._highlighter
        highlighter.setDocument(None)
        cursor = QTextCursor(self.document())
        cursor.beginEditBlock()
        try:
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.insertText(text)
            self.setTextCursor(cursor)
        finally:
            cursor.endEditBlock()
            highlighter.setDocument(self.document())
            highlighter.rehighlight()
        self.document().setModified(bool(mark_modified))
        self._schedule_decoration_refresh()
        return True

    def load_text(self, text: str) -> bool:
        if len(text) > self.MAX_DOCUMENT_CHARACTERS:
            self.paste_rejected.emit("The Markdown source exceeds MaqaronyPad's editor safety limit.")
            return False
        ok = self.replace_document_text(text, mark_modified=False)
        if ok:
            self.document().setModified(False)
        return ok

    # ---------- drops ----------




    # ---------- decoration compositor ----------









    # ---------- Markdown transformations ----------



















