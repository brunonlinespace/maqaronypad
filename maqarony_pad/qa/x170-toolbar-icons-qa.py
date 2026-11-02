#!/usr/bin/env python3
"""Canonical user-supplied toolbar icon inventory and wiring, edition-local gate."""
import hashlib,json
from pathlib import Path
PKG=Path(__file__).resolve().parents[1]
icons=PKG/'assets'/'toolbar-icons'
expected=json.loads((Path(__file__).resolve().parent/"x170-toolbar-inventory.json").read_text())
actual={p.relative_to(icons).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in icons.rglob('*') if p.is_file()}
assert len(expected)==288,(len(expected),len(actual))
assert actual==expected,('extra',sorted(actual.keys()-expected.keys()),'missing',sorted(expected.keys()-actual.keys()),'bytes',sorted(k for k in (actual.keys()&expected.keys()) if actual[k]!=expected[k])[:10])
source=(PKG/'widgets/editor_commands_appearance.py').read_text()
for fragment in (
    '"editor_layout_menu_action":"layout-markdown"',
    '"theme_light_action":"theme-light"',
    '"theme_dark_action":"theme-dark"',
    '"theme_system_action":"theme-system"',
    '"link_menu_action":"link-group"',
    'self.link_menu_action = links.menuAction()',
): assert fragment in source,fragment
assert '"editor_layout_menu_action":"toolbar-tabbed"' not in source
for old in ('"theme_light_action":"light-theme"','"theme_dark_action":"dark-mode"','"theme_system_action":"system-theme"'):
    assert old not in source, old
assert len([p for p in icons.glob('dark/*.png')])==144
assert len([p for p in icons.glob('light/*.png')])==144
print('PASS: canonical supplied 288-PNG icon pack, no leftovers, Editor Layout/theme/Link mapping')
