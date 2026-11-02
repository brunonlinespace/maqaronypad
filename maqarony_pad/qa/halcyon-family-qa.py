#!/usr/bin/env python3
"""Edition 1.0.0-x17.5 Halcyon artwork and selection contract."""
from pathlib import Path
import zipfile, hashlib
root=Path(__file__).resolve().parents[1]
outer=root.parent
scheme_set={'dark','light'}
assets=root/'assets'/'toolbar-icons-aero'
assert {p.name for p in assets.iterdir()} == scheme_set
for scheme in scheme_set:
    members=list((assets/scheme).glob('*.png'))
    assert len(members)==144,(scheme,len(members))
    assert (assets/scheme/'app-icons.png').is_file()
source=(root/'widgets/editor_commands_appearance.py').read_text()
assert '("halcyon", "Maqa Icons Halcyon")' in source
assert '"halcyon": "toolbar-icons-aero"' in source
assert 'for family in ("harmony", "humility", "heritage", "halcyon"):' in source
assert 'icon_halcyon_action = self.icon_family_actions["halcyon"]' in source
assert '"icon_halcyon_action"' not in source and "'icon_halcyon_action'" not in source, 'Halcyon should not have a mapped icon or toolbar button'
app=(root/'app.py').read_text()
assert '{"harmony", "humility", "heritage", "halcyon"}' in app
ribbon=(root/'widgets/editor_ribbon_retro.py').read_text()
assert 'icon_halcyon_action' not in ribbon
print('PASS Halcyon fourth AppMenu-only family and artwork inventory')
