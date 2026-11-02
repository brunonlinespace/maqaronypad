#!/usr/bin/env python3
"""x4 source-preservation release gate: all original editor and host methods,
source-view and Find/Replace extraction, renamed source and preview bytes.
"""
from __future__ import annotations
import ast, hashlib, json, pathlib
from source_contract import contract_text
ROOT=pathlib.Path(__file__).resolve().parents[1]
WIDGETS=ROOT
DATA=json.loads((ROOT/'qa/x4-method-fingerprints.json').read_text(encoding="utf-8"))
X3=json.loads((ROOT/'qa/x3-method-fingerprints.json').read_text(encoding="utf-8"))
def methods(path, name):
    source=contract_text(ROOT) if path.name=="app.py" else (contract_text(ROOT) if path.name=="app.py" else path.read_text(encoding="utf-8"))
    # x12.6 permits only the approved source-editor cursor-centering correction.
    if path.name == "editor_source.py":
        source=source.replace("self.setCenterOnScroll(False)", "self.setCenterOnScroll(True)")
    lines=source.splitlines(keepends=True)
    classes=[x for x in ast.parse(source).body if isinstance(x,ast.ClassDef) and x.name==name]
    assert len(classes)==1, (path,name)
    result={}
    for n in classes[0].body:
        if isinstance(n, (ast.FunctionDef,ast.AsyncFunctionDef)):
            begin=min((d.lineno for d in n.decorator_list),default=n.lineno)
            assert n.name not in result,(path,n.name)
            result[n.name]=hashlib.sha256("".join(lines[begin-1:n.end_lineno]).encode()).hexdigest()
    return result
src=WIDGETS/'widgets/mwpyn/editor_source.py'
view=WIDGETS/'widgets/mwpyn/editor_search_view.py'
fmt=WIDGETS/'widgets/mwpyn/editor_formatting.py'
ins=WIDGETS/'widgets/mwpyn/editor_insertion.py'
source_m=methods(src,'MarkopadSourceEditor')
view_m=methods(view,'EditorSearchViewMixin')
fmt_m=methods(fmt,'EditorFormattingMixin')
ins_m=methods(ins,'EditorInsertionMixin')
groups=[source_m,view_m,fmt_m,ins_m]
assert all(not (set(left) & set(right)) for i,left in enumerate(groups) for right in groups[i+1:]), 'duplicate inherited method'
assert set(view_m)==set(DATA['moved_source_methods']), 'x4 source extraction inventory drift'
assert set(source_m)|set(view_m)==set(DATA['source_editor_methods']), 'x4 source editor inventory drift'
assert source_m|view_m==DATA['source_editor_methods'], 'x4 source editor original definition modified'
assert {k:v for group in groups for k,v in group.items()}==X3['all_method_sha256'], 'x3 original method inventory changed'
original_class='class MarkopadSourceEditor(EditorSearchViewMixin, EditorInsertionMixin, EditorFormattingMixin, QPlainTextEdit):'
assert original_class in src.read_text(), 'canonical class inheritance drift'
assert 'EditorSearchViewMixin' in src.read_text() and 'EditorSearchViewMixin' in view.read_text()
HOST=ROOT/'app.py'
host_m=methods(HOST,'MaqaronyPadWindow')
host_m.update(methods(ROOT/'widgets/mwpyn/editor_lifecycle.py','EditorLifecycleMixin'))
host_view=methods(ROOT/'widgets/window_search_view.py','WindowSearchViewMixin')
host_printing=methods(ROOT/'widgets/mwpyn/editor_printing.py','EditorPrintingMixin')
host_preferences=methods(ROOT/'widgets/mwpyn/editor_preferences.py','EditorPreferencesMixin')
host_retro=methods(ROOT/'widgets/editor_ribbon_retro.py','EditorRibbonRetroMixin')
host_commands=methods(ROOT/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')
assert set(host_printing)=={'show_properties','_printable_document','print_document','export_pdf'}
assert not (set(host_m)&set(host_view)) and not ((set(host_m)|set(host_view))&set(host_printing)) and not ((set(host_m)|set(host_view)|set(host_printing))&set(host_preferences)), 'window/editor-page method override collision'
assert set(host_view)==set(DATA['moved_host_methods']), 'x4 host extraction inventory drift'
assert host_m|host_view|host_printing|host_preferences|host_retro|host_commands==DATA['host_methods'], 'original host implementation changed'
preview=WIDGETS/'widgets/mwpyn/editor_preview.py'
assert hashlib.sha256(preview.read_bytes()).hexdigest()==DATA['unchanged_preview_sha256'], 'preview content changed'
# x5 completes approved x4 filename convergence: obsolete compatibility aliases are absent.
assert not (WIDGETS/'source_editor.py').exists(), 'obsolete filename returned: source_editor.py'
assert not (WIDGETS/'preview.py').exists(), 'obsolete filename returned: preview.py'
# Search caps are intentionally retained at their original host import location;
# the extracted methods resolve matching values in their own module.
import ast as _ast

def global_assignments(path):
    parsed=_ast.parse((contract_text(ROOT) if path.name=="app.py" else path.read_text(encoding="utf-8")))
    result={}
    for node in parsed.body:
        if isinstance(node,_ast.Assign) and isinstance(node.value,_ast.Constant):
            for target in node.targets:
                if isinstance(target,_ast.Name): result[target.id]=node.value.value
    return result
caps=("MAX_SEARCH_MATCHES", "MAX_SEARCH_QUERY_CHARACTERS")
host_global=global_assignments(HOST)
view_global=global_assignments(ROOT/'widgets/window_search_view.py')
for cap in caps:
    assert host_global[cap] == view_global[cap], (cap, "search-limit drift across original host and extracted methods")
print(f"PASS x4: {len(source_m)+len(view_m)+len(fmt_m)+len(ins_m)} unchanged source methods; {len(host_m)+len(host_view)} unchanged host methods; {len(view_m)} + {len(host_view)} relocated; preview bytes exact")
