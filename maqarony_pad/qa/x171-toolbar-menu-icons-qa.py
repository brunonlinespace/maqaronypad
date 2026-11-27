#!/usr/bin/env python3
"""Toolbar menu/icon wiring: preserve artwork and enforce the scoped 1.1.7 mode contract."""
import hashlib, json
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
assert '"tabbed_mode_action":"toolbar-tabbed", "classic_mode_action":"toolbar-classic", "customize_classic_action":"toolbar-classic"' in src
assert 'self.tabbed_mode_action = self._action("Modern (default)", lambda: self.set_toolbar_mode("tabbed"), checkable=True)' in src
assert 'self.classic_mode_action = self._action("Classic", lambda: self.set_toolbar_mode("classic"), checkable=True)' in src
assert 'self.appmenu_only_mode_action = self._action("Disabled (AppMenu only)", lambda: self.set_toolbar_mode("appmenu_only"), checkable=True)' in src
assert 'self.customize_classic_action = self._action("Classic Settings...", self.show_classic_toolbar_dialog)' in src
assert 'toolbar_group = QActionGroup(self); toolbar_group.setExclusive(True)' in src
assert 'toolbar_group.addAction(self.tabbed_mode_action); toolbar_group.addAction(self.classic_mode_action); toolbar_group.addAction(self.appmenu_only_mode_action)' in src
assert 'self.toolbar_menu = view.addMenu("Editor Toolbar")' in src
assert 'self.toolbar_menu.addAction(self.tabbed_mode_action)' in src
assert 'self.toolbar_menu.addAction(self.classic_mode_action)' in src
assert 'self.toolbar_menu.addAction(self.customize_classic_action)' in src
assert 'self.toolbar_menu.addAction(self.appmenu_only_mode_action)' in src
assert 'self.editor_toolbar_menu_action = self.toolbar_menu.menuAction()' in src
assert 'self.classic_toolbar.addAction(self.customize_classic_action)' in ui
assert 'self.tabbed_mode_action.setChecked(tabbed)' in ui
assert 'self.classic_mode_action.setChecked(classic)' in ui
assert 'self.appmenu_only_mode_action.setChecked(appmenu_only)' in ui
assert 'self.menuBar().setVisible(classic or appmenu_only)' in ui
print('PASS: toolbar artwork preserved; Modern/Classic/Disabled and persistent Classic Settings contract enforced')
