#!/usr/bin/env python3
"""x17.1: three-menu-action icon bindings, preserved x17.0 artwork and selection."""
import ast, hashlib, json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
src=(root/'widgets/editor_commands_appearance.py').read_text()
ui=(root/'widgets/editor_ribbon_retro.py').read_text()
assets=root/'assets/toolbar-icons'
record=json.loads((root/'qa/x170-toolbar-inventory.json').read_text())
actual={p.relative_to(assets).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.rglob('*.png')}
assert actual == record, 'Artwork changed or old assets introduced'
for theme in ('light','dark'):
    for name in ('layout-ribbon.png','toolbar-tabbed.png','toolbar-classic.png'):
        assert (assets/theme/name).is_file(), (theme,name)
assert '"editor_toolbar_menu_action":"layout-ribbon"' in src
assert '"tabbed_mode_action":"toolbar-tabbed", "classic_mode_action":"toolbar-classic"' in src
assert '"editor_toolbar_menu_action":"toolbar-classic"' not in src
assert 'self.customize_classic_action.setIcon(QIcon())' in src
assert 'for action in (self.tabbed_mode_action, self.classic_mode_action, self.customize_classic_action):' not in src
assert 'self.toolbar_menu = view.addMenu("Editor Toolbar")' in src
assert 'self.toolbar_menu.addAction(self.tabbed_mode_action); self.toolbar_menu.addAction(self.classic_mode_action)' in src
assert 'self.editor_toolbar_menu_action = self.toolbar_menu.menuAction()' in src
assert 'self.tabbed_mode_action = self._action("Modern (default)", lambda: self.set_toolbar_mode("tabbed"), checkable=True)' in src
assert 'self.classic_mode_action = self._action("Classic", lambda: self.set_toolbar_mode("classic"), checkable=True)' in src
assert 'toolbar_group = QActionGroup(self); toolbar_group.setExclusive(True)' in src
assert 'toolbar_group.addAction(self.tabbed_mode_action); toolbar_group.addAction(self.classic_mode_action)' in src
assert 'self.tabbed_mode_action.setChecked(tabbed); self.classic_mode_action.setChecked(not tabbed)' in ui
assert 'self.editor_toolbar_menu_action' in ui
# Guard against writing icon names to unrelated actions in toolbar rendering.
assert '"Toggle Editor Toolbar", self.toggle_toolbar_style, "Ctrl+Alt+Shift+T"' in src
assert 'self.set_toolbar_mode("classic" if self.toolbar_mode == "tabbed" else "tabbed")' in ui
print('PASS: MaqaronyPad x17.1 Editor Toolbar/Modern/Classic icon wiring; x17.0 artwork and mode contract preserved')
