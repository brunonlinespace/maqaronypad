#!/usr/bin/env python3
"""x5 release gate: frozen x4 definitions, printing/Properties extraction, filename convergence."""
from __future__ import annotations
import ast,hashlib,json,pathlib
from source_contract import contract_text
ROOT=pathlib.Path(__file__).resolve().parents[1]
FROZEN=json.loads((ROOT/'qa/x5-method-fingerprints.json').read_text())
X4=json.loads((ROOT/'qa/x4-method-fingerprints.json').read_text())

def methods(path,klass):
    src=(contract_text(ROOT) if path.name=='app.py' else path.read_text(encoding='utf-8')); lines=src.splitlines(keepends=True)
    nodes=[n for n in ast.parse(src).body if isinstance(n,ast.ClassDef) and n.name==klass]
    assert len(nodes)==1, (path,klass)
    found={}
    for n in nodes[0].body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            begin=min([n.lineno,*[d.lineno for d in n.decorator_list]])-1
            assert n.name not in found,n.name
            found[n.name]=hashlib.sha256(''.join(lines[begin:n.end_lineno]).encode()).hexdigest()
    return found
for entry in FROZEN['methods']:
    host=methods(ROOT.parent/entry['source'].replace('maqarony_pad.py','app.py'),entry['host_class'])
    if entry['host_class']=='MaqaronyPadWindow':host.update(methods(ROOT/'widgets/mwpyn/editor_lifecycle.py','EditorLifecycleMixin'))
    moved=methods(ROOT/'widgets/mwpyn'/pathlib.Path(entry['mixin_path']).name,entry['mixin_class'])
    prefs=methods(ROOT/'widgets/mwpyn/editor_preferences.py','EditorPreferencesMixin')
    retro=methods(ROOT/'widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin')
    commands=methods(ROOT/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')
    assert set(moved)==set(entry['extracted_methods']), (entry['host_class'],'moved method inventory')
    assert not set(host)&set(moved), (entry['host_class'],'duplicate method names')
    assert host|moved|prefs|retro|commands==entry['original_methods'],(entry['host_class'],'original method source modified or missing')
# Original frozen x4 host/editor-page method sets remain complete despite their new inherited printing mixins.
original=X4['host_methods']
host=methods(ROOT/'app.py','MaqaronyPadWindow')
host.update(methods(ROOT/'widgets/mwpyn/editor_lifecycle.py','EditorLifecycleMixin'))
view=methods(ROOT/'widgets/window_search_view.py','WindowSearchViewMixin')
printing=methods(ROOT/'widgets/mwpyn/editor_printing.py','EditorPrintingMixin')
prefs=methods(ROOT/'widgets/mwpyn/editor_preferences.py','EditorPreferencesMixin')
retro=methods(ROOT/'widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin')
commands=methods(ROOT/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')
assert host|view|printing|prefs|retro|commands==original

# The formerly published aliases must be entirely absent, not merely empty or compatible.
for old in FROZEN['deleted_old_module_shims']:
    assert not (ROOT/pathlib.Path('.')/old).exists(), old
assert (ROOT/pathlib.Path('.')/'widgets/mwpyn/editor_source.py').is_file()
assert (ROOT/pathlib.Path('.')/'widgets/mwpyn/editor_preview.py').is_file()
# The release must point at canonical imports, never resurrecting old shims.
for file in ['app.py']:
    content=(ROOT/file).read_text()
    for banned in ('from source_editor import','from preview import'):
        assert banned not in content,(file,banned)
# Reuse the unchanged dialog-title helper from original host; do not duplicate/reimplement it.
src=contract_text(ROOT)
assert '_editor_printing.dialog_title = dialog_title' in src
assert 'class MaqaronyPadWindow(EditorLifecycleMixin, EditorCommandsAppearanceMixin, EditorRibbonRetroMixin, EditorPreferencesMixin, EditorPrintingMixin, WindowSearchViewMixin, QMainWindow):' in src

print('PASS x5: exact printing/Properties method identities; no obsolete module aliases; canonical imports retained')
