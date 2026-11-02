#!/usr/bin/env python3
# Existing x4 method bodies relocated unchanged for the x5 printing/document-information stage.
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QTextDocument
from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
from PyQt6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QGroupBox, QLineEdit, QVBoxLayout


class EditorPrintingMixin:

    def show_properties(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle(dialog_title("Properties"))
        dialog.setWindowIcon(self.windowIcon())
        dialog.setMinimumWidth(640)
        layout = QVBoxLayout(dialog); layout.setContentsMargins(18, 16, 18, 14); layout.setSpacing(12)

        def add_group(title: str, rows) -> None:
            box = QGroupBox(title, dialog)
            form = QFormLayout(box); form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            for label, value in rows:
                field = QLineEdit(str(value), box); field.setReadOnly(True); field.setCursorPosition(0); form.addRow(label, field)
            layout.addWidget(box)

        path = self.current_path
        if path is not None:
            try:
                stat_result = path.stat()
                permissions = oct(stat_result.st_mode & 0o777)
                modified = datetime.fromtimestamp(stat_result.st_mtime).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
                size = f"{stat_result.st_size:,} bytes"
            except OSError:
                permissions = modified = size = "Unavailable"
            name, location, full_path = path.name, str(path.parent), str(path)
        else:
            name, location, full_path = "Untitled.md", "Not saved", "Not saved"
            permissions = modified = size = "Unavailable"

        add_group("File", (("Name", name), ("Location", location), ("Full path", full_path), ("Size", size), ("Modified", modified), ("Permissions", permissions)))
        add_group("Document", (("Lines", f"{self.editor.blockCount():,}"), ("Characters", f"{max(0, self.editor.document().characterCount() - 1):,}"), ("Encoding", self.file_encoding), ("Newline", {"\n":"LF", "\r\n":"CRLF", "\r":"CR"}.get(self.file_newline, "LF")), ("Locked Mode", "On" if self.editor.isReadOnly() else "Off"), ("Edit mode", "Overwrite" if self.editor.overwriteMode() else "Insert")))
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, dialog); buttons.accepted.connect(dialog.accept); layout.addWidget(buttons)
        dialog.exec()

    def _printable_document(self) -> QTextDocument:
        doc = QTextDocument(self); doc.setDefaultFont(QApplication.font())
        if self.current_path: doc.setBaseUrl(QUrl.fromLocalFile(str(self.current_path.parent) + "/"))
        try: doc.setMarkdown(self.editor.toPlainText())
        except AttributeError: doc.setPlainText(self.editor.toPlainText())
        return doc

    def print_document(self) -> None:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution); dialog = QPrintDialog(printer, self); dialog.setWindowTitle(dialog_title("Print"))
        if dialog.exec() == QDialog.DialogCode.Accepted: self._printable_document().print(printer)

    def export_pdf(self) -> None:
        initial = str((self.current_path.with_suffix(".pdf") if self.current_path else Path.home()/"Untitled.pdf"))
        path, _ = QFileDialog.getSaveFileName(self, dialog_title("Export PDF"), initial, "PDF (*.pdf)")
        if not path: return
        if not path.lower().endswith(".pdf"): path += ".pdf"
        destination = Path(path)
        try:
            previous_stat = destination.stat()
            previous_fingerprint = (previous_stat.st_ino, previous_stat.st_size, previous_stat.st_mtime_ns)
        except OSError:
            previous_fingerprint = None
        printer = QPrinter(QPrinter.PrinterMode.HighResolution); printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat); printer.setOutputFileName(path); self._printable_document().print(printer)
        try:
            current_stat = destination.stat()
            fingerprint = (current_stat.st_ino, current_stat.st_size, current_stat.st_mtime_ns)
            if current_stat.st_size > 0 and fingerprint != previous_fingerprint:
                with destination.open("rb") as output:
                    is_pdf = output.read(5) == b"%PDF-"
                if is_pdf:
                    self.statusBar().showMessage(f"Exported PDF to {path}", 4000)
        except OSError:
            pass

