#!/usr/bin/env python3
"""x12.4: exact helper-source preservation, canonical import topology and behaviour."""
from __future__ import annotations
from pathlib import Path
import ast, hashlib, importlib.util, sys
ROOT=Path(__file__).resolve().parents[1]
EXPECTED={'_shortcut_tokens': '18d64d629800e751ff3277e3b28f0471d718e6408db038ce4083d2437137fe83', '_shortcut_query_matches': '681c30e67c2fd27b235087d9bc908420d878d9617750d684c577315ec59e0364'}
VERSION='1.0.0-x13.0'
MAQ=True
TARGET=ROOT/'app.py'
IMPORT='from widgets.keyboard_shortcuts import _shortcut_tokens, _shortcut_query_matches'
TOKEN='_shortcut_tokens'
MATCH='_shortcut_query_matches'
MODULE=ROOT/'widgets/keyboard_shortcuts.py'
assert MODULE.is_file() and not (ROOT/'shortcut_search.py').exists()
source=MODULE.read_text(encoding='utf-8')
assert source.startswith('#!/usr/bin/env python3\n')
tree=ast.parse(source)
expected=EXPECTED
methods={n.name:hashlib.sha256(ast.get_source_segment(source,n).encode()).hexdigest() for n in tree.body if isinstance(n,ast.FunctionDef)}
assert {key:methods[key] for key in expected}==expected, ('original helper definition changed', methods)
app=(ROOT/'app.py').read_text()
assert 'APP_VERSION = "'+VERSION+'"' in app
assert '_keyboard_shortcuts.show_shortcuts' in TARGET.read_text(), 'application no longer binds the canonical shortcut dialog'
assert not (ROOT/'app.py').read_text().count('def _shortcut_tokens('), 'duplicate MaqaronyPad helper'
# Import the pure helper module without PyQt or application globals.
spec=importlib.util.spec_from_file_location('x124_shortcut_search',MODULE)
obj=importlib.util.module_from_spec(spec)
spec.loader.exec_module(obj)
tokens=getattr(obj,TOKEN)('Ctrl+Alt+Shift+N')
match=getattr(obj,MATCH)
assert match('shift control n',tokens)
assert match('ctl n',tokens)
assert match('alt shift',tokens)
assert not match('meta q',tokens)
assert not match('',tokens)
assert all(p.read_bytes().startswith(b'#!/usr/bin/env python3') for p in ROOT.rglob('*.py'))
builder=(ROOT/'packaging/fedora/build-appimage.sh').read_text()
assert 'widgets/keyboard_shortcuts.py' in builder or 'collect_submodules' in builder or 'compileall -q "$SOURCE_ENTRY" "$PROGRAM_ROOT"' in builder
assert (ROOT/'widgets/window_search_view.py').exists() == MAQ
print('PASS x12.4: shortcut helpers are exact copies, canonical, importable and behaviour-preserving')
