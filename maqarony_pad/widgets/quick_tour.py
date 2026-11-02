#!/usr/bin/env python3
"""Existing MaqaronyPad quick tour presentation methods, relocated unchanged."""
from __future__ import annotations
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QCheckBox, QLabel, QPushButton, QVBoxLayout, QWizard, QWizardPage


def show_quick_tour(self) -> None:
    if self.tutorial_dialog is not None:
        self.tutorial_dialog.show(); self.tutorial_dialog.raise_(); self.tutorial_dialog.activateWindow(); return
    wizard=QWizard(self); wizard.setWindowTitle("Quick Tour — MaqaronyPad"); wizard.setWindowIcon(self.windowIcon()); wizard.setModal(False); wizard.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose,True)
    wizard.setOption(QWizard.WizardOption.NoBackButtonOnStartPage,True)
    startup_checkbox=QCheckBox("Don't show Quick Tour on startup again",wizard); startup_checkbox.setChecked(bool(self.tutorial_seen))
    def set_tour_startup_disabled(checked):
        self.tutorial_seen=bool(checked); self.persist_preferences()
    startup_checkbox.toggled.connect(set_tour_startup_disabled)
    wizard.setButton(QWizard.WizardButton.CustomButton1,startup_checkbox)
    wizard.setOption(QWizard.WizardOption.HaveCustomButton1,True)
    wizard.setButtonLayout([QWizard.WizardButton.CustomButton1,QWizard.WizardButton.Stretch,QWizard.WizardButton.BackButton,QWizard.WizardButton.NextButton,QWizard.WizardButton.FinishButton,QWizard.WizardButton.CancelButton])
    def add_page(title,body,button=None):
        page=QWizardPage(wizard); page.setTitle(title); layout=QVBoxLayout(page)
        label=QLabel(body,page); label.setWordWrap(True); label.setTextFormat(Qt.TextFormat.RichText); layout.addWidget(label)
        if button is not None: layout.addWidget(button,0,Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1); wizard.addPage(page)
    add_page("Welcome to MaqaronyPad","<p>MaqaronyPad is a focused editor for ordinary Markdown files. The Modern toolbar has six tabs: <b>File, Home, Insert, View, Settings and Help</b>, with Home open by default.</p><p>Hover a command for its name or shortcut. Use <b>Ctrl+Tab</b> and <b>Ctrl+Shift+Tab</b> to move between toolbar tabs. Double-click a tab title to collapse Modern toolbar controls; click a tab title once to reveal them again.</p>")
    add_page("Create, open and save","<p><b>File</b> contains New, Open, Save, Save As, Duplicate, Rename, Delete, Print, Export PDF and related file commands. MaqaronyPad edits Markdown directly, so there is no private document format.</p><p>Drag a Markdown file onto the editor to follow your configured active-window/new-window behavior.</p>")
    add_page("Write and format Markdown","<p><b>Home</b> provides Undo/Redo, selection and line commands, Bold, Italic, Strikethrough, Code, headings, lists, quotes and indentation.</p><p><b>Insert</b> contains images, links, tables, dates/times, horizontal rules and symbols. Formatting commands write portable Markdown syntax into Source.</p>")
    add_page("Find and navigate","<p><b>Ctrl+F</b> opens the Find/Replace panel and focuses Find; <b>Ctrl+H</b> focuses Replace. <b>Esc</b> closes the panel. Use <b>F3</b> for the next result and <b>Shift+F3</b> for the previous result.</p><p>Locked Mode protects Source from accidental changes while navigation, copying and search remain available. Help → Keyboard Shortcuts provides the live command inventory with fuzzy shortcut matching.</p>")
    add_page("View and reading comfort","<p><b>View</b> controls Full Screen, Show Status, Source Only, Source + Preview, Preview Only, Locked Mode, Editor Layout, Editor Toolbar, zoom and editor miscellany.</p><p>App Theme controls the application chrome; Dark Editor controls the Source/Preview canvas independently.</p>")
    add_page("Make it yours!","<p>Choose <b>Modern</b> or <b>Classic</b> from View → Editor Toolbar. Classic uses the same shared command registry in one configurable horizontal bar.</p><p>Use <b>Customise Classic Bar…</b> to choose its commands. Double-click the Source/Preview splitter to restore the default 3:2 layout.</p>")
    shortcuts_button=QPushButton("Open Keyboard Shortcuts…",wizard); shortcuts_button.setAutoDefault(False); shortcuts_button.clicked.connect(self.show_shortcuts)
    add_page("Markdown interoperability and help","<p>MaqaronyPad saves standards-based Markdown source directly. Preview is read-only and exists to render the current Markdown; it is never the stored document format.</p><p>Use <b>F1</b> for bundled documentation. Help also provides this Quick Tour, Keyboard Shortcuts, GitHub, Raise an Issue and About.</p>",shortcuts_button)
    def tutorial_finished(_result):
        self.tutorial_dialog=None
        QTimer.singleShot(0,self._focus_current_view)
    wizard.finished.connect(tutorial_finished); self.tutorial_dialog=wizard; wizard.show(); wizard.raise_(); wizard.activateWindow()
