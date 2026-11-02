#!/usr/bin/env python3
"""x7 exact-text method identities, toolbar ownership and GitHub README gate."""
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'qa/x7-method-fingerprints.json').read_text())
def methods(path, cls):
    src=contract_text(ROOT) if path.name=='app.py' else path.read_text(); lines=src.splitlines(keepends=True)
    found=[n for n in ast.parse(src).body if isinstance(n,ast.ClassDef) and n.name==cls]
    assert len(found)==1,(path,cls)
    result={}
    for n in found[0].body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            start=min([n.lineno]+[d.lineno for d in n.decorator_list])-1
            assert n.name not in result
            result[n.name]=hashlib.sha256(''.join(lines[start:n.end_lineno]).encode()).hexdigest()
    return result
host=methods(ROOT/'app.py','MaqaronyPadWindow')
host.update(methods(ROOT/'widgets/mwpyn/editor_lifecycle.py','EditorLifecycleMixin'))
retro=methods(ROOT/'widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin')
commands=methods(ROOT/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')
assert retro==DATA['method_sha256'], 'Tabbed/Classic method definition changed'
assert not (set(host)&set(retro)), 'duplicate/override method'
assert host|retro|commands==DATA['original_host_method_sha256'], 'original x6.1 host method lost or changed'
existing=[]
for f, cls in [('widgets/window_search_view.py','WindowSearchViewMixin'),('widgets/mwpyn/editor_printing.py','EditorPrintingMixin'),('widgets/mwpyn/editor_preferences.py','EditorPreferencesMixin')]:
    group=methods(ROOT/f,cls)
    assert not (set(group) & set(host|retro|commands)), ('inherited name collision',f)
    assert not (set(group) & set(existing)), ('inherited name collision',f)
    existing.extend(group)
s=contract_text(ROOT)
assert 'class MaqaronyPadWindow(EditorLifecycleMixin, EditorCommandsAppearanceMixin, EditorRibbonRetroMixin, EditorPreferencesMixin, EditorPrintingMixin, WindowSearchViewMixin, QMainWindow):' in s
for bind in ('_editor_ribbon_retro.CLASSIC_TOOLBAR_DEFAULT = CLASSIC_TOOLBAR_DEFAULT','_editor_ribbon_retro.dialog_title = dialog_title','_editor_ribbon_retro.asset_path = asset_path'):
    assert bind in s, ('missing original host binding',bind)
assert '"$PROGRAM_ROOT/widgets/editor_ribbon_retro.py"' in (ROOT/'packaging/fedora/build-appimage.sh').read_text()
assert 'CLASSIC_TOOLBAR_DEFAULT = [' in s, 'original toolbar defaults moved without approval'
assert 'from widgets.editor_ribbon_retro import EditorRibbonRetroMixin' in s
readme=(ROOT.parent/'README.md').read_bytes().replace(b'> **Historical attribution correction (1.0.0-x11.0):** The 0.2.10 shortcuts/Quick Tour correction was released as **Markopad 0.2.10**, not MaqaronyPad. The archived sentence immediately below is retained unchanged.\n\n',b'')
baseline_sha=json.loads((ROOT/'qa/x6-method-fingerprints.json').read_text())['github_readme_sha256']
assert hashlib.sha256(readme.replace(b'1.0.0-x13.0',b'1.0.0-x6.1')).hexdigest()==baseline_sha, 'GitHub README content changed beyond version'
assert b'Current release: **1.0.0-x13.0**' in readme
print('PASS x7: 24 toolbar definitions exact, complete host method inventory retained, bindings/README/build contracts verified')
