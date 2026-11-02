#!/usr/bin/env python3
"""x17.3: Execute the real Quick Tour function with a Qt API simulator.

This is intentionally more than a source-grep check: all seven wizard pages must
construct without undefined Qt names, and the existing callbacks must still work.
The simulator lets this run when PyQt6 is absent from a build/audit machine.
"""
from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'widgets' / 'quick_tour.py'
APP = ROOT / 'app.py'
CODE = SOURCE.read_text(encoding='utf-8')
assert ast.parse(CODE)
assert 'APP_VERSION = "1.0.0-x17.3"' in APP.read_text(encoding='utf-8')
assert 'APP_VERSION == "1.0.0-x17.3"' in APP.read_text(encoding='utf-8'), 'AppImage GUI smoke version must match release'

# Names must be imported in their canonical Qt modules, not injected as globals.
imports = {
    node.module: {alias.name for alias in node.names}
    for node in ast.parse(CODE).body if isinstance(node, ast.ImportFrom)
}
assert {'Qt', 'QTimer'} <= imports['PyQt6.QtCore']
assert {'QCheckBox', 'QLabel', 'QPushButton', 'QVBoxLayout', 'QWizard', 'QWizardPage'} <= imports['PyQt6.QtWidgets']

qt = ModuleType('PyQt6')
core = ModuleType('PyQt6.QtCore')
widgets = ModuleType('PyQt6.QtWidgets')
qt.__path__ = []
core.Qt = MagicMock(name='Qt')
core.QTimer = MagicMock(name='QTimer')
for klass in ('QCheckBox', 'QLabel', 'QPushButton', 'QVBoxLayout', 'QWizard', 'QWizardPage'):
    setattr(widgets, klass, MagicMock(name=klass))
# Resolve imports via module symbols, as the real application does on startup.
saved = {key: sys.modules.get(key) for key in ('PyQt6', 'PyQt6.QtCore', 'PyQt6.QtWidgets')}
try:
    sys.modules.update({'PyQt6': qt, 'PyQt6.QtCore': core, 'PyQt6.QtWidgets': widgets})
    spec = importlib.util.spec_from_file_location('maqa_x173_tour_test', SOURCE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
finally:
    for key, original in saved.items():
        if original is None:
            sys.modules.pop(key, None)
        else:
            sys.modules[key] = original

class FakeWindow:
    tutorial_dialog = None
    tutorial_seen = False

    def __init__(self):
        self.persist_preferences = MagicMock(name='persist_preferences')
        self.show_shortcuts = MagicMock(name='show_shortcuts')
        self._focus_current_view = MagicMock(name='_focus_current_view')

    def windowIcon(self):
        return None

host = FakeWindow()
module.show_quick_tour(host)  # Regression: would raise NameError at QWizardPage in x17.2.
wizard = widgets.QWizard.return_value
assert host.tutorial_dialog is wizard
assert widgets.QWizardPage.call_count == 7, 'Quick Tour must construct all seven pages'
assert widgets.QLabel.call_count == 7, 'Quick Tour must populate all seven page labels'
assert wizard.addPage.call_count == 7
assert widgets.QPushButton.return_value.clicked.connect.call_args.args[0] == host.show_shortcuts
checkbox = widgets.QCheckBox.return_value
checkbox.toggled.connect.call_args.args[0](True)
assert host.tutorial_seen is True
host.persist_preferences.assert_called_once_with()

# Existing-dialog behavior: show/raise/focus, never construct duplicate wizard.
module.show_quick_tour(host)
assert widgets.QWizard.call_count == 1
assert wizard.show.call_count == 2

# Closing must clear the reference and restore editor focus on next Qt turn.
wizard.finished.connect.call_args.args[0](0)
assert host.tutorial_dialog is None
core.QTimer.singleShot.assert_called_once_with(0, host._focus_current_view)

print('PASS x17.3: Quick Tour constructs seven pages; startup option, shortcuts, re-show and close callbacks')
