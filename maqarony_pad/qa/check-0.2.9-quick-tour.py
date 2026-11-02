#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'markopad.py').read_text(encoding='utf-8')
errs=[]
def req(c,m):
    if not c: errs.append(m)
for frag in (
    'APP_VERSION = "0.2.9"',
    'self.quick_start_action = self._action("Quick Tour…", self.show_quick_tour, "Shift+F1")',
    'self.quick_start_action.setToolTip("Quick Tour… (Shift+F1)")',
    'wizard.setWindowTitle("Quick Tour — Markopad")',
    'QCheckBox("Don\'t show Quick Tour on startup again",wizard)',
    'startup_checkbox.setChecked(bool(self.tutorial_seen))',
    'self.tutorial_seen=bool(checked); self.persist_preferences()',
    'if not self.tutorial_seen:\n            QTimer.singleShot(0, self.show_quick_tour)',
    '"tutorial_seen": bool(self.tutorial_seen),',
): req(frag in s, f'missing Quick Tour contract: {frag}')
req('def show_quick_start' not in s, 'old Quick Start implementation remains')
req('QMessageBox.information(self, dialog_title("Quick Start")' not in s, 'old Quick Start message remains')
req(s.count('add_page(')>=8, 'expected seven Quick Tour pages plus helper definition')
if errs:
 print('Markopad 0.2.9 check failed:'); [print('-',e) for e in errs]; sys.exit(1)
print('PASS: Markopad 0.2.9 Quick Tour contract')
