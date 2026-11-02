#!/usr/bin/env python3
"""x12.2 bounded Python source-header convergence: no code, layout, mode changes."""
from pathlib import Path
import hashlib, ast, stat
ROOT = Path(__file__).resolve().parents[1]
OUTER = ROOT.parent
HEAD = b"#!/usr/bin/env python3\n"
VERSION = '1.0.0-x13.0'
PRIOR = '1.0.0-x12.1'
EXPECTED = {'widgets/editor_commands_appearance.py': 'b8727ad8425af02c30d79b5c706d93f1fd738a2a7d437f2329b57b580e0b3eae', 'widgets/mwpyn/editor_preferences.py': '5fe3cbd7d0b6c70a7bdc7e503560191f397fdc7675ecc9dade6a3f1f34512704', 'widgets/mwpyn/editor_printing.py': 'c48153977eab599aa811a893fc6cd9aa1d1d0dad7945c13e639f63d84ac5b14b', 'widgets/mwpyn/editor_search_view.py': '373ddffcbb831bde1744ba260fa4eed38ef78868689244aeaf16a5235a2f2d33', 'widgets/window_search_view.py': '21b84c9be0d22070b00132da3a168cdae5481c7f39a857bb2decf9063ffe96a7'}
assert len(EXPECTED) == 5
for name, digest in EXPECTED.items():
    path=ROOT/name
    content=path.read_bytes()
    assert content.startswith(HEAD), f"missing canonical shebang: {name}"
    # The x12.3 widget-tree pass alters import targets, not the original
    # implementation. Normalise only the relocated import for the frozen x12.2 hash.
    historical=content[len(HEAD):].replace(b'from widgets.mwpyn.editor_widgets import ',b'from editor_widgets import ')
    assert hashlib.sha256(historical).hexdigest()==digest, f"non-shebang or non-import change: {name}"
    assert not (path.stat().st_mode & stat.S_IXUSR), f"import-only file became executable: {name}"
for path in [OUTER/"main.py", *ROOT.rglob("*.py")]:
    content=path.read_bytes()
    assert content.startswith(b"#!/usr/bin/env python3"), f"Python shebang missing: {path}"
    compile(content, str(path), "exec")
assert (OUTER/"main.py").stat().st_mode & stat.S_IXUSR, "root launcher lost executable permission"
assert hashlib.sha256((OUTER/"README.md").read_bytes().replace(VERSION.encode(), PRIOR.encode())).hexdigest() == '8ea816191e2e0bd095ff3c00776388eb06347e7b4d6b1c3717b5b099529536aa', "public README changed beyond version"
# Retain x12.5 source record intact beneath the x12.6 release preface.
inner=(ROOT/"README.md").read_bytes()
inner=inner[inner.index(b'# MaqaronyPad 1.0.0-x12.5'):]
assert hashlib.sha256(inner.replace(b'1.0.0-x12.5', PRIOR.encode())).hexdigest() == 'd178a274f04be59a7d002240d3e3f3d018b15ddb46b39df4682e202357efc0c4', "historical internal README changed"
assert (ROOT/"app.py").is_file(), "app.py not retained"
assert (ROOT/"widgets"/"__init__.py").is_file() and (ROOT/"widgets"/"mwpyn"/"__init__.py").is_file(), "x12.3 widget package missing"
print("PASS: x12.2 Python shebangs, content preservation, permissions, and README protection")
