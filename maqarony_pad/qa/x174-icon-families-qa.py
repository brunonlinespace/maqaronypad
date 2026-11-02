#!/usr/bin/env python3
"""Current Maqa icon-family release gate: source, artworks and UI wiring."""
import ast,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
asset_root=ROOT/'assets'
expected=json.loads((Path(__file__).parent/'maqa-icon-family-inventory.json').read_text())
actual={p.relative_to(asset_root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('toolbar-icons','toolbar-icons-classic','toolbar-icons-original') for p in (asset_root/folder).rglob('*.png')}
assert len(expected)==864 and actual==expected, (len(expected),len(actual),sorted(expected.keys()-actual.keys())[:10],sorted(actual.keys()-expected.keys())[:10])
for folder in ('toolbar-icons','toolbar-icons-classic','toolbar-icons-original'):
    dark={p.name for p in (asset_root/folder/'dark').glob('*.png')}
    light={p.name for p in (asset_root/folder/'light').glob('*.png')}
    assert len(light)==len(dark)==144 and light==dark
common=(ROOT/'widgets/editor_commands_appearance.py').read_text()
assert 'Maqa Icons Harmony' in common and 'Maqa Icons Humility' in common and 'Maqa Icons Heritage' in common
assert 'icon_group = QActionGroup(self); icon_group.setExclusive(True)' in common
assert 'icon_menu = settings.addMenu("App Icons")' in common
assert 'self.app_icons_menu_action = icon_menu.menuAction()' in common
assert '"app_icons_menu_action":"app-icons"' in common
for icon in ('icons-new','icons-classic','icons-legacy'):
    assert f'"{icon}"' in common
assert '"harmony": "toolbar-icons", "humility": "toolbar-icons-classic"' in common
assert '"heritage": "toolbar-icons-original"' in common
assert 'self._refresh_action_icons()' in common
ast.parse(common)
app=(ROOT/'app.py').read_text()
retro=(ROOT/'widgets/editor_ribbon_retro.py').read_text()
prefs=(ROOT/'widgets/mwpyn/editor_preferences.py').read_text()
assert 'self.icon_family = str(self.settings.get("icon_family", "harmony"))' in app
assert '"icon_family": self.icon_family' in prefs
assert 'self.persist_preferences()' in common
assert '[self.icon_harmony_action, self.icon_humility_action, self.icon_heritage_action]' in retro
assert 'self._icon_family_directory(), self._effective_scheme()' in retro
assert 'asset_path(self._icon_family_directory(), scheme,' in common
for src in (app,retro,prefs): ast.parse(src)
print("PASS: 864 source-exact PNGs, three exclusive selectors, persistent families, live icons")
