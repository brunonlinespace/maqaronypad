#!/usr/bin/env python3
"""x6 strict method-copy parity, architecture and GitHub root README content gate."""
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
PKG=ROOT.name
BASE=ROOT.parent
QA=Path(__file__).parent
FROZEN=json.loads((QA/'x6-method-fingerprints.json').read_text())

def methods(file, name):
    s=(contract_text(ROOT) if file.name=='app.py' else file.read_text(encoding='utf-8')); lines=s.splitlines(keepends=True)
    cs=[x for x in ast.parse(s).body if isinstance(x,ast.ClassDef) and x.name==name]
    assert len(cs)==1,(file,name)
    out={}
    for n in cs[0].body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            start=min([n.lineno,*[d.lineno for d in n.decorator_list]])-1
            assert n.name not in out
            out[n.name]=hashlib.sha256(''.join(lines[start:n.end_lineno]).encode()).hexdigest()
    return out

host=methods(BASE/FROZEN['source'].replace('maqarony_pad.py','app.py'),FROZEN['host_class'])
host.update(methods(ROOT/'widgets/mwpyn/editor_lifecycle.py','EditorLifecycleMixin'))
mixin=methods(ROOT/'widgets/mwpyn'/Path(FROZEN['mixin']).name,FROZEN['mixin_class'])
retro=methods(ROOT/'widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin')
commands=methods(ROOT/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')
assert mixin==FROZEN['method_sha256'], 'extracted preference method source differs from x5'
assert not set(host)&set(mixin), 'a preference method has multiple implementations'
assert host|mixin|retro|commands==FROZEN['x5_host_methods'], 'original editor host method missing or changed'
readme=(BASE/'README.md').read_bytes().replace(b'> **Historical attribution correction (1.0.0-x11.0):** The 0.2.10 shortcuts/Quick Tour correction was released as **Markopad 0.2.10**, not MaqaronyPad. The archived sentence immediately below is retained unchanged.\n\n',b'')
prior_readme=readme.replace(b'1.0.0-x13.0', b'1.0.0-x6.1')
assert hashlib.sha256(prior_readme).hexdigest()==FROZEN['github_readme_sha256'], 'unapproved alteration in GitHub root README beyond version replacement' 
assert b'Current release: **1.0.0-x13.0**' in readme
if PKG=='maqarony_pad':
    main=contract_text(ROOT)
    assert 'class MaqaronyPadWindow(EditorLifecycleMixin, EditorCommandsAppearanceMixin, EditorRibbonRetroMixin, EditorPreferencesMixin, EditorPrintingMixin, WindowSearchViewMixin, QMainWindow):' in main
    assert '_editor_preferences.save_json_settings = save_json_settings' in main
    assert 'from widgets.mwpyn.editor_preferences import EditorPreferencesMixin' in main
    assert '"$PROGRAM_ROOT/widgets/mwpyn/editor_preferences.py"' in (ROOT/'packaging/fedora/build-appimage.sh').read_text()
else:
    main=(ROOT/'widgets/editor_page.py').read_text()
    assert 'class EditorPage(EditorPagePreferencesMixin, EditorPagePrintingMixin, EditorPageSearchViewMixin, QWidget):' in main
    assert 'from mepynamu.widgets.editor_page_preferences import EditorPagePreferencesMixin' in main
print('PASS x6: original preference implementations exact; README restored/locked; mixin bindings verified')
