"""Unicode-aware Chars for MaqaronyPad's *Markdown source* QTextDocument.

Use Qt's extended-grapheme boundaries on the literal source text in each
QTextBlock. Count one logical newline between blocks, including empty lines.
Per-block revision/userData caches avoid segmenting unchanged text; the host
window also caches the document total until textChanged. No cursor-only full
text extraction, and no change to editing, file-size or security limits.
"""
from __future__ import annotations

from PyQt6.QtCore import QTextBoundaryFinder
from PyQt6.QtGui import QTextBlockUserData


class _SourceGraphemeCount(QTextBlockUserData):
    def __init__(self, revision: int, count: int) -> None:
        super().__init__()
        self.revision = revision
        self.count = count


def _count_graphemes(text: str) -> int:
    if not text:
        return 0
    finder = QTextBoundaryFinder(QTextBoundaryFinder.BoundaryType.Grapheme, text)
    count = 0
    while finder.toNextBoundary() != -1:
        count += 1
    return count


def count_markdown_characters(document) -> int:
    """Count grapheme clusters in Markdown *source*, not rendered preview."""
    count = 0
    block = document.begin()
    while block.isValid():
        revision = block.revision()
        cached = block.userData()
        if not isinstance(cached, _SourceGraphemeCount) or cached.revision != revision:
            cached = _SourceGraphemeCount(revision, _count_graphemes(block.text()))
            block.setUserData(cached)
        count += cached.count
        next_block = block.next()
        if next_block.isValid():
            count += 1  # Logical newline between source lines.
        block = next_block
    return count
