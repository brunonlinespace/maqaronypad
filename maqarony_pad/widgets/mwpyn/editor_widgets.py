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


@dataclass(frozen=True, slots=True)
class HighlightRule:
    pattern: re.Pattern[str]
    text_format: QTextCharFormat


MARKDOWN_COLOR_SCHEMES = {
    "dark": {
        "gutter_background": "#181B1D",
        "gutter_current": "#EFF0F1",
        "gutter_foreground": "#8B949E",
        "current_line": "#252A2E",
        "match_background": "#415A54",
        "match_foreground": "#FFFFFF",
        "heading": "#7DCFFF",
        "emphasis": "#E6B566",
        "strong": "#FFCC66",
        "strike": "#C792EA",
        "code": "#A7D46F",
        "quote": "#89DDFF",
        "list": "#F78C6C",
        "link": "#82AAFF",
        "image": "#C3E88D",
        "rule": "#B0BEC5",
        "comment": "#6A9955",
        "escape": "#FF5370",
        "table": "#89DDFF",
    },
    "light": {
        "gutter_background": "#F2F4F6",
        "gutter_current": "#202124",
        "gutter_foreground": "#687078",
        "current_line": "#EEF5FB",
        "match_background": "#C8E6C9",
        "match_foreground": "#16351B",
        "heading": "#005A9C",
        "emphasis": "#8A4B08",
        "strong": "#7A3E00",
        "strike": "#6A1B9A",
        "code": "#2E7D32",
        "quote": "#006064",
        "list": "#A13A16",
        "link": "#174EA6",
        "image": "#33691E",
        "rule": "#59636D",
        "comment": "#2E7D32",
        "escape": "#B00020",
        "table": "#006064",
    },
}


def _scheme(name: str) -> str:
    return "light" if name == "light" else "dark"


class MarkdownHighlighter(QSyntaxHighlighter):
    """Small, dependency-free Markdown highlighter with fenced-block state."""

    FENCE_STATE_BACKTICK = 1
    FENCE_STATE_TILDE = 2

    def __init__(self, document: QTextDocument, color_scheme: str = "dark") -> None:
        super().__init__(document)
        self._color_scheme = _scheme(color_scheme)
        self._build_formats()

    @staticmethod
    def _format(color: str, *, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        fmt.setFontWeight(QFont.Weight.Bold if bold else QFont.Weight.Normal)
        fmt.setFontItalic(italic)
        return fmt

    def _build_formats(self) -> None:
        colors = MARKDOWN_COLOR_SCHEMES[self._color_scheme]
        self.heading_format = self._format(colors["heading"], bold=True)
        self.strong_format = self._format(colors["strong"], bold=True)
        self.emphasis_format = self._format(colors["emphasis"], italic=True)
        self.strike_format = self._format(colors["strike"])
        self.code_format = self._format(colors["code"])
        self.quote_format = self._format(colors["quote"])
        self.list_format = self._format(colors["list"], bold=True)
        self.link_format = self._format(colors["link"])
        self.image_format = self._format(colors["image"])
        self.rule_format = self._format(colors["rule"], bold=True)
        self.comment_format = self._format(colors["comment"], italic=True)
        self.escape_format = self._format(colors["escape"])
        self.table_format = self._format(colors["table"])

    def set_color_scheme(self, color_scheme: str) -> None:
        selected = _scheme(color_scheme)
        if selected == self._color_scheme:
            return
        self._color_scheme = selected
        self._build_formats()
        self.rehighlight()

    @staticmethod
    def _apply_pattern(highlighter, text: str, pattern: str, fmt: QTextCharFormat, flags=0) -> None:
        for match in re.finditer(pattern, text, flags):
            highlighter.setFormat(match.start(), match.end() - match.start(), fmt)

    def highlightBlock(self, text: str) -> None:  # noqa: N802 - Qt API name
        previous = self.previousBlockState()
        stripped = text.lstrip()

        if previous in (self.FENCE_STATE_BACKTICK, self.FENCE_STATE_TILDE):
            delimiter = "```" if previous == self.FENCE_STATE_BACKTICK else "~~~"
            self.setFormat(0, len(text), self.code_format)
            if stripped.startswith(delimiter):
                self.setCurrentBlockState(0)
            else:
                self.setCurrentBlockState(previous)
            return

        fence = re.match(r"^\s*(`{3,}|~{3,})([^`]*)$", text)
        if fence:
            self.setFormat(0, len(text), self.code_format)
            self.setCurrentBlockState(
                self.FENCE_STATE_BACKTICK if fence.group(1).startswith("`")
                else self.FENCE_STATE_TILDE
            )
            return

        self.setCurrentBlockState(0)

        # Block-level tokens first.
        heading = re.match(r"^\s{0,3}(#{1,6})(?:\s+|$)", text)
        if heading:
            self.setFormat(heading.start(1), len(heading.group(1)), self.heading_format)
            self.setFormat(heading.end(1), len(text) - heading.end(1), self.heading_format)
        quote = re.match(r"^\s{0,3}>\s?", text)
        if quote:
            self.setFormat(quote.start(), quote.end() - quote.start(), self.quote_format)
        list_marker = re.match(r"^(\s*)(?:[-+*]|\d+[.)])\s+", text)
        if list_marker:
            marker_start = len(list_marker.group(1))
            self.setFormat(marker_start, list_marker.end() - marker_start, self.list_format)
        task = re.match(r"^\s*[-+*]\s+\[[ xX]\]\s+", text)
        if task:
            self.setFormat(task.start(), task.end() - task.start(), self.list_format)
        if re.match(r"^\s{0,3}(?:_{3,}|-{3,}|\*{3,})\s*$", text):
            self.setFormat(0, len(text), self.rule_format)
        if text.count("|") >= 2 and re.match(r"^\s*\|?.*\|.*\|?\s*$", text):
            for match in re.finditer(r"\|", text):
                self.setFormat(match.start(), 1, self.table_format)

        # Inline code must be coloured before emphasis so asterisks inside code
        # do not look like formatting delimiters.
        code_ranges = []
        for match in re.finditer(r"(`+)(.+?)\1", text):
            self.setFormat(match.start(), match.end() - match.start(), self.code_format)
            code_ranges.append((match.start(), match.end()))

        def outside_code(start: int, end: int) -> bool:
            return not any(start < code_end and end > code_start for code_start, code_end in code_ranges)

        inline_rules = (
            (r"!\[[^\]\n]*\]\([^\n)]*\)", self.image_format),
            (r"(?<!!)\[[^\]\n]+\]\([^\n)]*\)", self.link_format),
            (r"\*\*[^\n*]+\*\*|__[^\n_]+__", self.strong_format),
            (r"~~[^\n~]+~~", self.strike_format),
            (r"(?<!\*)\*[^\n*]+\*(?!\*)|(?<!_)_[^\n_]+_(?!_)", self.emphasis_format),
            (r"\\[\\`*{}_\[\]()#+\-.!>]", self.escape_format),
            (r"<!--.*?-->", self.comment_format),
        )
        for pattern, fmt in inline_rules:
            for match in re.finditer(pattern, text):
                if outside_code(match.start(), match.end()):
                    self.setFormat(match.start(), match.end() - match.start(), fmt)


class LineNumberArea(QWidget):
    def __init__(self, editor: "MarkopadSourceEditor") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # noqa: N802
        self.editor.paint_line_number_area(event)
