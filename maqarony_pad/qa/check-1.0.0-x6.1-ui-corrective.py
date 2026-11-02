#!/usr/bin/env python3
from pathlib import Path
import sys
from source_contract import contract_text
ROOT = Path(__file__).resolve().parents[1]
s = contract_text(ROOT)
errs=[]
def req(c,m):
    if not c: errs.append(m)
req('APP_VERSION = "1.0.0-x6.1"' in s, '1.0.0-x6.1 identity missing')
req('shortcuts_button.clicked.connect(self.show_shortcuts)' in s, 'Quick Tour Keyboard Shortcuts button is not routed to show_shortcuts')
req('show_keyboard_shortcuts_dialog' not in s, 'invalid Ricopad-only Quick Tour callback remains')
req('<br><b>Configuration:</b> {html.escape(str(CONFIG_FILE))}' in s, 'About does not use Configuration label')
req('<br><b>Preferences:</b> {html.escape(str(CONFIG_FILE))}' not in s, 'About still uses Preferences label')
# Preserve the established Quick Tour contract.
for frag in (
    'self.quick_start_action = self._action("Quick Tour…", self.show_quick_tour, "Shift+F1")',
    'self.quick_start_action.setToolTip("Quick Tour… (Shift+F1)")',
    'QCheckBox("Don\'t show Quick Tour on startup again",wizard)',
): req(frag in s, f'Quick Tour contract regressed: {frag}')
# AppMenu More Actions authority.
menu = s[s.index('more = self.file_menu.addMenu("More Actions")'):s.index('self.file_menu.addSeparator()\n        self.file_menu.addAction(self.print_action)')]
menu_order = [
    'more.addAction(self.duplicate_file_action)',
    'more.addAction(self.rename_file_action)',
    'more.addAction(self.delete_file_action)',
    'more.addAction(self.external_editor_action)',
    'more.addAction(self.open_folder_action)',
    'more.addAction(self.properties_action)',
]
req(all(x in menu for x in menu_order), 'More Actions AppMenu inventory changed')
req([menu.index(x) for x in menu_order] == sorted(menu.index(x) for x in menu_order), 'More Actions AppMenu order changed')
# Modern File toolbar must mirror that semantic order for More Actions buttons.
expected='[self.duplicate_file_action, self.rename_file_action, self.delete_file_action, self.external_editor_action, self.open_folder_action, self.properties_action],'
req(expected in s, 'Modern File toolbar More Actions order does not match AppMenu')
if errs:
    print('MaqaronyPad 1.0.0-x6.1 check failed:')
    [print('-', e) for e in errs]
    sys.exit(1)
print('PASS: MaqaronyPad 1.0.0-x6.1 corrective/UI-ordering contract')
