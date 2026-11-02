#!/usr/bin/env python3
"""x10 exact original method-copy and inherited lifecycle source safety contract."""
from __future__ import annotations
import ast,hashlib,json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
BASE=json.loads((Path(__file__).parent/'x10-method-fingerprints.json').read_text())
def methods(path,klass):
    text=contract_text(ROOT) if path.name=='app.py' else (contract_text(ROOT) if path.name=='app.py' else path.read_text(encoding='utf-8'));lines=text.splitlines(keepends=True)
    cs=[x for x in ast.parse(text).body if isinstance(x,ast.ClassDef) and x.name==klass]
    assert len(cs)==1,(path,klass)
    result={}
    for n in cs[0].body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            start=min([n.lineno]+[d.lineno for d in n.decorator_list])-1
            assert n.name not in result
            result[n.name]=hashlib.sha256(''.join(lines[start:n.end_lineno]).encode()).hexdigest()
    return result
host=methods(ROOT/('app.py' if BASE['host']=='maqarony_pad.py' else BASE['host']),BASE['host_class'])
life=methods(ROOT/'widgets/mwpyn'/Path(BASE['mixin']).name,BASE['mixin_class'])
assert life==BASE['moved_sha256'],('lifecycle implementation drift',life)
assert host|life==BASE['all_sha256'],'missing or modified original host methods'
assert not set(host)&set(life),'lifecycle MRO override collision'
assert set(life)==set(BASE['moved_names']),'moved inventory mismatch'

others=[('widgets/window_search_view.py','WindowSearchViewMixin'),('widgets/mwpyn/editor_printing.py','EditorPrintingMixin'),('widgets/mwpyn/editor_preferences.py','EditorPreferencesMixin'),('widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin'),('widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')]
s=contract_text(ROOT)
assert 'class MaqaronyPadWindow(EditorLifecycleMixin, EditorCommandsAppearanceMixin, EditorRibbonRetroMixin, EditorPreferencesMixin, EditorPrintingMixin, WindowSearchViewMixin, QMainWindow):' in s
assert 'import widgets.mwpyn.editor_lifecycle as _editor_lifecycle' in s
assert 'from widgets.mwpyn.editor_lifecycle import EditorLifecycleMixin' in s
for x in ('dialog_title','save_json_settings'):
    assert f'_editor_lifecycle.{x} = {x}' in s
assert '"$PROGRAM_ROOT/widgets/mwpyn/editor_lifecycle.py"' in (ROOT/'packaging/fedora/build-appimage.sh').read_text()
# Preserve dependency evaluation order: a past experimental release failed on an
# application-module attribute assignment before the referenced module existed.
compiled=ast.parse(s)
seen=set()
for node in compiled.body:
    if isinstance(node,(ast.FunctionDef,ast.ClassDef)):seen.add(node.name)
    elif isinstance(node,ast.Import):seen.update(alias.asname or alias.name.split('.')[0] for alias in node.names)
    elif isinstance(node,ast.ImportFrom):seen.update(alias.asname or alias.name for alias in node.names)
    elif isinstance(node,ast.Assign):
        for target in node.targets:
            if isinstance(target,ast.Attribute) and isinstance(target.value,ast.Name) and target.value.id=='_editor_lifecycle':
                assert '_editor_lifecycle' in seen, 'lifecycle module bound before import'
                assert isinstance(node.value,ast.Name) and node.value.id in seen,(target.attr,'helper bound before definition')
            elif isinstance(target,ast.Name):seen.add(target.id)


seen=set(host)|set(life)
for name,klass in others:
    group=methods(ROOT/name,klass)
    assert not (seen&set(group)),(name,'inherited method collision')
    seen|=set(group)
assert 'def load_from_disk' in (ROOT/'widgets/mwpyn'/Path(BASE['mixin']).name).read_text() if BASE['host_class']=='EditorPage' else 'def rename_file' in (ROOT/'widgets/mwpyn'/Path(BASE['mixin']).name).read_text()
README=(ROOT.parent/'README.md').read_bytes()
assert b'Current release: **1.0.0-x13.0**' in README
prior=ROOT.parent.parent/(('MaqaronyPad-1.0.0-x9.0-source' if BASE['host_class']=='MaqaronyPadWindow' else 'MepyNamu-1.0.0-x8.0-source'))/'README.md'
if prior.is_file():
    original=prior.read_bytes()
    baseline=BASE['baseline'].encode()
    assert README.replace(b'> **Historical attribution correction (1.0.0-x11.0):** The 0.2.10 shortcuts/Quick Tour correction was released as **Markopad 0.2.10**, not MaqaronyPad. The archived sentence immediately below is retained unchanged.\n\n',b'')==original.replace(baseline,b'1.0.0-x13.0'), 'GitHub README drift outside version and recorded erratum'
print('PASS x10: exact lifecycle definition identity, complete host inventory, no MRO override, approved README version')
