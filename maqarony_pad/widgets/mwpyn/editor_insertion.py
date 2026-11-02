#!/usr/bin/env python3
# ==============================================================================
# Markdown source-editor insertion and clipboard methods — x3.0 extraction.
# The method definitions below are text-identical to their x2.0 baseline.
# GPLv3-or-later; preserved original implementation and product messages.
# ==============================================================================

from __future__ import annotations

import re

from PyQt6.QtCore import QMimeData, Qt, QTimer
from PyQt6.QtGui import QInputMethodEvent, QKeyEvent, QTextCursor


class EditorInsertionMixin:

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Insert and modifiers in (
            Qt.KeyboardModifier.NoModifier,
            Qt.KeyboardModifier.KeypadModifier,
        ):
            enabled = not self.overwriteMode()
            self.setOverwriteMode(enabled)
            self.overwrite_mode_changed.emit(enabled)
            event.accept()
            return

        if modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_Slash:
            self.toggle_comment()
            event.accept()
            return

        if self.isReadOnly():
            if self._is_mutating_key_event(event):
                self.view_only_edit_attempt.emit()
                event.accept()
                return
            super().keyPressEvent(event)
            return

        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current = cursor.block().text()
            leading = current[: len(current) - len(current.lstrip(" \t"))]
            if not self._replacement_fits(start, end, 1 + len(leading)):
                self._reject_document_growth(); return
            self._insert_newline_with_indent()
            return
        if key == Qt.Key.Key_Tab and not (modifiers & Qt.KeyboardModifier.ControlModifier):
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                self.unindent_selection_or_line()
            else:
                if not cursor.hasSelection() and not self._replacement_fits(start, end, self._tab_width_spaces):
                    self._reject_document_growth(); return
                self.indent_selection_or_insert_spaces()
            return
        text = event.text()
        if text and any(ch.isprintable() for ch in text):
            if not self._replacement_fits(start, end, len(text)):
                self._reject_document_growth(); return
        if key == Qt.Key.Key_Backtab:
            self.unindent_selection_or_line()
            return
        super().keyPressEvent(event)

    def inputMethodEvent(self, event: QInputMethodEvent) -> None:  # noqa: N802
        if self.isReadOnly() and (event.commitString() or event.preeditString()):
            self.view_only_edit_attempt.emit()
            event.accept()
            return
        commit = event.commitString()
        if commit:
            cursor = self.textCursor()
            if not self._replacement_fits(cursor.selectionStart(), cursor.selectionEnd(), len(commit)):
                self._reject_document_growth()
                event.accept()
                return
        super().inputMethodEvent(event)

    def insertFromMimeData(self, source: QMimeData) -> None:  # noqa: N802
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        if source is None or not source.hasText():
            self.paste_rejected.emit("Clipboard content is not plain text and was not pasted.")
            return
        try:
            text = source.text()
        except Exception as error:
            self.paste_rejected.emit(f"Clipboard text could not be read: {error}")
            return
        self.insert_guarded_text(text)

    def insert_guarded_text(self, text: str) -> bool:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return False
        text = str(text).replace("\x00", "")
        if len(text) > self.MAX_PASTE_CHARACTERS:
            self.paste_rejected.emit("Clipboard text is too large to paste safely.")
            return False
        if not text:
            return True
        cursor = self.textCursor()
        document_length = max(0, self.document().characterCount() - 1)
        selected_length = abs(cursor.selectionEnd() - cursor.selectionStart())
        if document_length - selected_length + len(text) > self.MAX_DOCUMENT_CHARACTERS:
            self.paste_rejected.emit("The paste would exceed MaqaronyPad's source document safety limit.")
            return False
        selection_start = min(cursor.selectionStart(), cursor.selectionEnd())
        selection_end = max(cursor.selectionStart(), cursor.selectionEnd())
        if cursor.hasSelection() and selection_start == 0 and selection_end >= document_length:
            self._pending_full_paste = text
            self._full_paste_generation += 1
            generation = self._full_paste_generation
            self._decoration_timer.stop()
            self.setExtraSelections([])
            QTimer.singleShot(0, lambda: self._apply_pending_full_paste(generation))
            return True
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self._schedule_decoration_refresh()
        return True

    def _apply_pending_full_paste(self, generation: int) -> None:
        if generation != self._full_paste_generation or self.isReadOnly():
            return
        text = self._pending_full_paste
        self._pending_full_paste = None
        if text is not None:
            self.replace_document_text(text)
            self.setFocus()

    def dragEnterEvent(self, event) -> None:  # noqa: N802
        mime = event.mimeData()
        if mime.hasUrls() and any(url.isLocalFile() for url in mime.urls()):
            event.acceptProposedAction()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event) -> None:  # noqa: N802
        mime = event.mimeData()
        if mime.hasUrls() and any(url.isLocalFile() for url in mime.urls()):
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event) -> None:  # noqa: N802
        mime = event.mimeData()
        if mime.hasUrls():
            paths = [url.toLocalFile() for url in mime.urls() if url.isLocalFile()]
            if paths:
                self.files_dropped.emit(paths)
                event.acceptProposedAction()
                return
        super().dropEvent(event)

    def insert_code_fence(self, language: str = "") -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        cursor = self.textCursor()
        selected = cursor.selectedText().replace("\u2029", "\n")
        max_run = max((len(match.group(0)) for match in re.finditer(r"`+", selected)), default=0)
        fence = "`" * max(3, max_run + 1)
        lang = re.sub(r"[^A-Za-z0-9_+.#-]", "", language.strip())[:64]
        opening = fence + lang
        content = selected
        if content and not content.endswith("\n"):
            content += "\n"
        insertion = f"{opening}\n{content}{fence}"
        if not self._replacement_fits(cursor.selectionStart(), cursor.selectionEnd(), len(insertion)):
            self._reject_document_growth()
            return
        cursor.beginEditBlock()
        cursor.insertText(insertion)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def insert_link(self, label: str, url: str) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        safe_label = str(label).replace("\n", " ").replace("]", r"\]")
        safe_url = str(url).replace(" ", "%20").replace(")", r"\)")
        insertion = f"[{safe_label}]({safe_url})"
        cursor = self.textCursor()
        if not self._replacement_fits(cursor.selectionStart(), cursor.selectionEnd(), len(insertion)):
            self._reject_document_growth(); return
        cursor.insertText(insertion)

    def insert_horizontal_rule(self) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        cursor = self.textCursor()
        required = 4 + (1 if cursor.block().text() else 0)
        if not self._replacement_fits(cursor.position(), cursor.position(), required):
            self._reject_document_growth(); return
        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.beginEditBlock()
        if cursor.block().text():
            cursor.insertText("\n")
        cursor.insertText("___\n")
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def insert_table(self, rows: int, columns: int) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        rows = max(1, min(100, int(rows)))
        columns = max(1, min(20, int(columns)))
        header = "| " + " | ".join(f"Column {i + 1}" for i in range(columns)) + " |"
        divider = "| " + " | ".join("---" for _ in range(columns)) + " |"
        body = ["| " + " | ".join("" for _ in range(columns)) + " |" for _ in range(max(0, rows - 1))]
        text = "\n".join([header, divider, *body])
        cursor = self.textCursor()
        additional = len(text) + (1 if cursor.positionInBlock() != 0 else 0)
        if not self._replacement_fits(cursor.selectionStart(), cursor.selectionEnd(), additional):
            self._reject_document_growth(); return
        cursor.beginEditBlock()
        if cursor.positionInBlock() != 0:
            cursor.insertText("\n")
        cursor.insertText(text)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def duplicate_current_line_or_selection(self) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        cursor = self.textCursor()
        cursor.beginEditBlock()
        if cursor.hasSelection():
            selected = cursor.selectedText().replace("\u2029", "\n")
            addition = len(selected)
            cursor.setPosition(cursor.selectionEnd())
            insertion = selected
        else:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            line = cursor.selectedText()
            addition = len(line) + 1
            cursor.clearSelection()
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
            insertion = "\n" + line
        if max(0, self.document().characterCount() - 1) + addition > self.MAX_DOCUMENT_CHARACTERS:
            cursor.endEditBlock()
            self.paste_rejected.emit("Duplication would exceed MaqaronyPad's source document safety limit.")
            return
        cursor.insertText(insertion)
        cursor.endEditBlock()
        self.setTextCursor(cursor)

    def indent_selection_or_insert_spaces(self) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        cursor = self.textCursor()
        if not cursor.hasSelection():
            if not self._replacement_fits(cursor.position(), cursor.position(), self._tab_width_spaces):
                self._reject_document_growth()
                return
            cursor.insertText(" " * self._tab_width_spaces)
            return
        start, end = self._selected_block_range(cursor)
        probe = QTextCursor(self.document()); probe.setPosition(start)
        line_count = 0
        while probe.position() <= end:
            line_count += 1
            if not probe.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        if not self._replacement_fits(start, end, (end - start) + line_count * self._tab_width_spaces):
            self._reject_document_growth(); return
        cursor.beginEditBlock()
        cursor.setPosition(start)
        while cursor.position() <= end:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.insertText(" " * self._tab_width_spaces)
            end += self._tab_width_spaces
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    def unindent_selection_or_line(self) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        cursor = self.textCursor()
        start, end = self._selected_block_range(cursor)
        cursor.beginEditBlock()
        cursor.setPosition(start)
        while cursor.position() <= end:
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            block_text = cursor.block().text()
            if block_text.startswith("\t"):
                remove_count = 1
            else:
                remove_count = min(self._tab_width_spaces, len(block_text) - len(block_text.lstrip(" ")))
            for _ in range(remove_count):
                cursor.deleteChar()
            end -= remove_count
            if not cursor.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        cursor.endEditBlock()

    def _insert_newline_with_indent(self) -> None:
        """Insert a Markdown-aware newline while keeping source authoritative."""
        cursor = self.textCursor()
        current = cursor.block().text()
        leading = current[: len(current) - len(current.lstrip(" \t"))]
        body = current[len(leading):]

        patterns = (
            (re.compile(r"^([-+*])\s+\[([ xX])\]\s?(.*)$"), "task"),
            (re.compile(r"^([-+*])\s+(.*)$"), "bullet"),
            (re.compile(r"^(\d+)([.)])\s+(.*)$"), "number"),
            (re.compile(r"^(>)\s?(.*)$"), "quote"),
        )
        continuation = leading
        empty_structure = False
        for pattern, kind in patterns:
            match = pattern.match(body)
            if not match:
                continue
            if kind == "task":
                content = match.group(3)
                empty_structure = not content.strip()
                continuation = f"{leading}{match.group(1)} [ ] "
            elif kind == "bullet":
                content = match.group(2)
                empty_structure = not content.strip()
                continuation = f"{leading}{match.group(1)} "
            elif kind == "number":
                content = match.group(3)
                empty_structure = not content.strip()
                continuation = f"{leading}{int(match.group(1)) + 1}{match.group(2)} "
            else:
                content = match.group(2)
                empty_structure = not content.strip()
                continuation = f"{leading}> "
            break

        if empty_structure:
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.removeSelectedText()
            cursor.insertText(leading)
            cursor.endEditBlock()
        else:
            cursor.insertText("\n" + continuation)
        self.setTextCursor(cursor)
