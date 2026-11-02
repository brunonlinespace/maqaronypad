#!/usr/bin/env python3
# Markdown source-editor formatting methods — extracted unchanged for x2.0.
# The original method bodies and public method names are preserved.
from __future__ import annotations

import re
from PyQt6.QtGui import QTextCursor


class EditorFormattingMixin:
    def toggle_comment(self) -> None:
        """Toggle a Markdown-compatible HTML comment around the selection or current line."""
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return

        cursor = self.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText().replace("\u2029", "\n")
            stripped = selected.strip()
            if stripped.startswith("<!--") and stripped.endswith("-->"):
                leading = len(selected) - len(selected.lstrip())
                trailing = len(selected) - len(selected.rstrip())
                core = selected[leading: len(selected) - trailing if trailing else None]
                core = core[4:-3]
                if core.startswith(" "):
                    core = core[1:]
                if core.endswith(" "):
                    core = core[:-1]
                replacement = selected[:leading] + core + (selected[len(selected)-trailing:] if trailing else "")
            else:
                replacement = f"<!-- {selected} -->"
            if not self._replacement_fits(
                cursor.selectionStart(), cursor.selectionEnd(), len(replacement)
            ):
                self._reject_document_growth()
                return
            cursor.insertText(replacement)
            self.setTextCursor(cursor)
            return

        cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
        text = cursor.selectedText()
        stripped = text.strip()
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            leading = len(text) - len(text.lstrip())
            trailing = len(text) - len(text.rstrip())
            core = text[leading: len(text) - trailing if trailing else None][4:-3]
            if core.startswith(" "):
                core = core[1:]
            if core.endswith(" "):
                core = core[:-1]
            replacement = text[:leading] + core + (text[len(text)-trailing:] if trailing else "")
        else:
            replacement = f"<!-- {text} -->"
        if not self._replacement_fits(
            cursor.selectionStart(), cursor.selectionEnd(), len(replacement)
        ):
            self._reject_document_growth()
            return
        cursor.insertText(replacement)
        self.setTextCursor(cursor)
    def _selected_block_range(self, cursor: QTextCursor) -> tuple[int, int]:
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        start_cursor = QTextCursor(self.document())
        start_cursor.setPosition(start)
        start_cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
        end_cursor = QTextCursor(self.document())
        end_cursor.setPosition(end)
        if end > start and end_cursor.positionInBlock() == 0:
            end_cursor.movePosition(QTextCursor.MoveOperation.PreviousBlock)
        end_cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock)
        return start_cursor.position(), end_cursor.position()
    def _transform_selected_blocks(self, transform) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        cursor = self.textCursor()
        start, end = self._selected_block_range(cursor)
        probe = QTextCursor(self.document())
        probe.setPosition(start)
        lines = []
        while probe.position() <= end:
            lines.append(probe.block().text())
            if not probe.movePosition(QTextCursor.MoveOperation.NextBlock):
                break
        replacement = "\n".join(transform(lines))
        if not self._replacement_fits(start, end, len(replacement)):
            self._reject_document_growth()
            return
        edit = QTextCursor(self.document())
        edit.setPosition(start)
        edit.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
        edit.beginEditBlock()
        edit.insertText(replacement)
        edit.endEditBlock()
        self.setTextCursor(edit)
    def _toggle_inline(self, left: str, right: str | None = None) -> None:
        if self.isReadOnly():
            self.view_only_edit_attempt.emit()
            return
        right = left if right is None else right
        cursor = self.textCursor()
        start, end = cursor.selectionStart(), cursor.selectionEnd()
        document = self.document()
        selected = cursor.selectedText().replace("\u2029", "\n")
        # Toggle delimiters around an existing selection when the exact pair is
        # immediately outside it; otherwise wrap the selected text.
        if cursor.hasSelection() and start >= len(left):
            before = "".join(document.characterAt(i) for i in range(start - len(left), start))
            after = "".join(document.characterAt(i) for i in range(end, min(end + len(right), document.characterCount() - 1)))
            if before == left and after == right:
                edit = QTextCursor(document)
                edit.beginEditBlock()
                edit.setPosition(end)
                edit.setPosition(end + len(right), QTextCursor.MoveMode.KeepAnchor)
                edit.removeSelectedText()
                edit.setPosition(start - len(left))
                edit.setPosition(start, QTextCursor.MoveMode.KeepAnchor)
                edit.removeSelectedText()
                edit.endEditBlock()
                edit.setPosition(start - len(left))
                edit.setPosition(end - len(left), QTextCursor.MoveMode.KeepAnchor)
                self.setTextCursor(edit)
                return
        replacement = left + selected + right
        if not self._replacement_fits(start, end, len(replacement)):
            self._reject_document_growth()
            return
        cursor.beginEditBlock()
        cursor.insertText(replacement)
        cursor.endEditBlock()
        # Keep the content selected, not the delimiters.
        new_cursor = self.textCursor()
        insertion_end = new_cursor.position()
        new_cursor.setPosition(insertion_end - len(right) - len(selected))
        new_cursor.setPosition(insertion_end - len(right), QTextCursor.MoveMode.KeepAnchor)
        self.setTextCursor(new_cursor)
    def toggle_bold(self) -> None:
        self._toggle_inline("**")
    def toggle_italic(self) -> None:
        self._toggle_inline("*")
    def toggle_strikethrough(self) -> None:
        self._toggle_inline("~~")
    def toggle_inline_code(self) -> None:
        cursor = self.textCursor()
        selected = cursor.selectedText().replace("\u2029", "\n")
        max_run = max((len(match.group(0)) for match in re.finditer(r"`+", selected)), default=0)
        delimiter = "`" * max(1, max_run + 1)
        self._toggle_inline(delimiter)
    def apply_heading(self, level: int) -> None:
        level = max(0, min(6, int(level)))
        def transform(lines):
            output = []
            for line in lines:
                content = re.sub(r"^\s{0,3}#{1,6}(?:\s+|$)", "", line)
                if level:
                    leading = line[: len(line) - len(line.lstrip(" "))][:3]
                    output.append(leading + ("#" * level) + " " + content.lstrip())
                else:
                    output.append(content)
            return output
        self._transform_selected_blocks(transform)
    def toggle_bullet_list(self) -> None:
        def transform(lines):
            if len(lines) == 1 and not lines[0].strip():
                return [lines[0] + "- "]
            meaningful = [line for line in lines if line.strip()]
            remove = bool(meaningful) and all(re.match(r"^\s*[-+*]\s+", line) for line in meaningful)
            output = []
            for line in lines:
                if not line.strip():
                    output.append(line)
                    continue
                indent = line[: len(line) - len(line.lstrip())]
                body = line[len(indent):]
                if remove:
                    body = re.sub(r"^[-+*]\s+", "", body)
                    output.append(indent + body)
                else:
                    body = re.sub(r"^(?:[-+*]|\d+[.)])\s+", "", body)
                    output.append(indent + "- " + body)
            return output
        self._transform_selected_blocks(transform)
    def toggle_numbered_list(self) -> None:
        def transform(lines):
            if len(lines) == 1 and not lines[0].strip():
                return [lines[0] + "1. "]
            meaningful = [line for line in lines if line.strip()]
            remove = bool(meaningful) and all(re.match(r"^\s*\d+[.)]\s+", line) for line in meaningful)
            output = []
            number = 1
            for line in lines:
                if not line.strip():
                    output.append(line)
                    continue
                indent = line[: len(line) - len(line.lstrip())]
                body = line[len(indent):]
                if remove:
                    body = re.sub(r"^\d+[.)]\s+", "", body)
                    output.append(indent + body)
                else:
                    body = re.sub(r"^(?:[-+*]|\d+[.)])\s+", "", body)
                    output.append(f"{indent}{number}. {body}")
                    number += 1
            return output
        self._transform_selected_blocks(transform)
    def toggle_blockquote(self) -> None:
        def transform(lines):
            meaningful = [line for line in lines if line.strip()]
            remove = bool(meaningful) and all(re.match(r"^\s*>\s?", line) for line in meaningful)
            output = []
            for line in lines:
                indent = line[: len(line) - len(line.lstrip())]
                body = line[len(indent):]
                output.append(indent + (re.sub(r"^>\s?", "", body) if remove else "> " + body))
            return output
        self._transform_selected_blocks(transform)
    def toggle_task_list(self) -> None:
        def transform(lines):
            if len(lines) == 1 and not lines[0].strip():
                return [lines[0] + "- [ ] "]
            meaningful = [line for line in lines if line.strip()]
            remove = bool(meaningful) and all(re.match(r"^\s*[-+*]\s+\[[ xX]\]\s+", line) for line in meaningful)
            output = []
            for line in lines:
                if not line.strip():
                    output.append(line)
                    continue
                indent = line[: len(line) - len(line.lstrip())]
                body = line[len(indent):]
                if remove:
                    body = re.sub(r"^[-+*]\s+\[[ xX]\]\s+", "", body)
                    output.append(indent + body)
                else:
                    body = re.sub(r"^(?:[-+*]\s+\[[ xX]\]\s+|[-+*]\s+|\d+[.)]\s+)", "", body)
                    output.append(indent + "- [ ] " + body)
            return output
        self._transform_selected_blocks(transform)
