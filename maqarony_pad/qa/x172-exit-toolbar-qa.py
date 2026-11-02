#!/usr/bin/env python3
"""x17.2: Exit final in Modern File and available by default in Classic."""
import ast
from pathlib import Path
R=Path(__file__).resolve().parents[1]
ui=(R/'widgets/editor_ribbon_retro.py').read_text()
app=(R/'app.py').read_text()
cmd=(R/'widgets/editor_commands_appearance.py').read_text()
for name,txt in [('editor_ribbon_retro',ui),('app',app),('editor_commands_appearance',cmd)]:ast.parse(txt,filename=name)
assert '[self.print_action, self.export_pdf_action],\n                [self.exit_action],' in ui
assert 'if index:\n                    self._tabbed_separator(toolbar)' in ui
assert '"new", "open", "save", "exit",' in app
assert '("File", "save_exit", "Save and Exit", self.save_exit_action),\n            ("File", "exit", "Exit", self.exit_action),' in ui
assert 'self.classic_toolbar_items = (' in app and 'self.settings.get("classic_toolbar_items"' in app
assert 'self.exit_action = self._action("Exit", self.close, QKeySequence.StandardKey.Quit)' in cmd
assert 'shortcut_text = action.shortcut().toString(QKeySequence.SequenceFormat.NativeText)' in cmd
assert 'action.setToolTip(f"{label} — {shortcut_text}" if shortcut_text else label)' in cmd
assert '"exit_action":"exit"' in cmd
for scheme in ('light','dark'):assert (R/f'assets/toolbar-icons/{scheme}/exit.png').is_file()
print('PASS x17.2: final Modern File Exit with separator; Classic default and order; existing shortcut tooltip')
