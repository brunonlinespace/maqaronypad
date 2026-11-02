#!/usr/bin/env python3
"""x8 strict source identity, inheritance and README content gate."""
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
FROZEN=json.loads((ROOT/'qa/x8-method-fingerprints.json').read_text())
def methods(path,classname):
    s=contract_text(ROOT) if path.name=='app.py' else path.read_text(); lines=s.splitlines(keepends=True)
    classes=[n for n in ast.parse(s).body if isinstance(n,ast.ClassDef) and n.name==classname]
    assert len(classes)==1,(path,classname)
    out={}
    for n in classes[0].body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            start=min([n.lineno]+[d.lineno for d in n.decorator_list])-1
            assert n.name not in out
            out[n.name]=hashlib.sha256(''.join(lines[start:n.end_lineno]).encode()).hexdigest()
    return out

entry=FROZEN
host=methods(ROOT/'app.py','MaqaronyPadWindow')
host.update(methods(ROOT/'widgets/mwpyn/editor_lifecycle.py','EditorLifecycleMixin'))
moved=methods(ROOT/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')
assert moved==entry['relocated'], 'moved method definition changed'
assert not (set(host)&set(moved)), 'duplicate host/mixin method'
assert host|moved==entry['fingerprints'], 'original x7 method lost or modified'
others=[('widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin'),('widgets/mwpyn/editor_preferences.py','EditorPreferencesMixin'),('widgets/mwpyn/editor_printing.py','EditorPrintingMixin'),('widgets/window_search_view.py','WindowSearchViewMixin')]
all_groups=[host,moved]+[methods(ROOT/f,k) for f,k in others]
assert all(not (set(a)&set(b)) for i,a in enumerate(all_groups) for b in all_groups[i+1:]),'duplicate inherited method'
s=contract_text(ROOT)
assert 'class MaqaronyPadWindow(EditorLifecycleMixin, EditorCommandsAppearanceMixin, EditorRibbonRetroMixin, EditorPreferencesMixin, EditorPrintingMixin, WindowSearchViewMixin, QMainWindow):' in s
for name in ['APP_NAME','asset_path','dialog_title','save_json_settings','apply_theme']:
    assert f'_editor_commands_appearance.{name} = {name}' in s,name
assert '"$PROGRAM_ROOT/widgets/editor_commands_appearance.py"' in (ROOT/'packaging/fedora/build-appimage.sh').read_text()
README=(ROOT.parent/'README.md').read_bytes().replace(b'> **Historical attribution correction (1.0.0-x11.0):** The 0.2.10 shortcuts/Quick Tour correction was released as **Markopad 0.2.10**, not MaqaronyPad. The archived sentence immediately below is retained unchanged.\n\n',b'')
F6=json.loads((ROOT/'qa/x6-method-fingerprints.json').read_text())
assert hashlib.sha256(README.replace(b'1.0.0-x13.0',b'1.0.0-x6.1')).hexdigest()==F6['github_readme_sha256'], 'GitHub root README changed beyond version'
print('PASS x8: MaqaronyPad command/appearance definitions exact; no inherited method collisions; root README locked')
