#!/usr/bin/env python3
"""Existing MaqaronyPad about dialog presentation methods, relocated unchanged."""
from __future__ import annotations
import html
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


def show_about(self) -> None:
    if self.about_dialog is not None:
        self.about_dialog.show(); self.about_dialog.raise_(); self.about_dialog.activateWindow(); return
    dialog = QDialog(self); dialog.setWindowTitle(dialog_title("About")); dialog.setWindowIcon(self.windowIcon()); dialog.setModal(False); dialog.setMinimumWidth(390)
    layout = QVBoxLayout(dialog); layout.setContentsMargins(24, 22, 24, 18); layout.setSpacing(10)
    logo = QLabel(dialog); logo.setAlignment(Qt.AlignmentFlag.AlignCenter); about_art = asset_path("icons", "maqaronypad-about.png"); pixmap = (QIcon(str(about_art)).pixmap(112, 112) if about_art.is_file() else application_icon().pixmap(112, 112))
    if not pixmap.isNull(): logo.setPixmap(pixmap); layout.addWidget(logo)
    title = QLabel(f"<h2>{APP_NAME}</h2>", dialog); title.setTextFormat(Qt.TextFormat.RichText); title.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(title)
    version = QLabel(f"Version {APP_VERSION}", dialog); version.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(version)
    tagline = QLabel(f"<b>{APP_TAGLINE}</b>", dialog); tagline.setTextFormat(Qt.TextFormat.RichText); tagline.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(tagline)
    description = QLabel("A focused, source-faithful Markdown editor with Source Only, Source + Preview and Preview Only layouts.", dialog); description.setWordWrap(True); description.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(description)
    details = QLabel(f"<a href='{GITHUB_URL}'>{GITHUB_URL}</a><br>Built on Python and PyQt6, carrying forward the proven Markdown-source foundations of Ricopad.<br><b>Configuration:</b> {html.escape(str(CONFIG_FILE))}<br><br>Copyright © 2026 Bruno Machado<br>[<a href='https://github.com/brunonlinespace/'>https://github.com/brunonlinespace/</a>]<br>Licensed under the GNU General Public License v3 or later.", dialog)
    details.setTextFormat(Qt.TextFormat.RichText); details.setAlignment(Qt.AlignmentFlag.AlignCenter); details.setOpenExternalLinks(True); details.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction); layout.addWidget(details)
    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, dialog); ok_button = buttons.button(QDialogButtonBox.StandardButton.Ok)
    if ok_button is not None: ok_button.setText("OK")
    buttons.accepted.connect(dialog.close); layout.addWidget(buttons); dialog.finished.connect(lambda _result: setattr(self, "about_dialog", None)); self.about_dialog = dialog; dialog.show()
