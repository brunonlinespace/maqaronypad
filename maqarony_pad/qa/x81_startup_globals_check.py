#!/usr/bin/env python3
"""x8.1: verify moved globals resolve at definition/call time without Qt imports."""
from __future__ import annotations
import ast, builtins, hashlib, json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
HOST=contract_text(ROOT)
MOV=(ROOT/'widgets/editor_commands_appearance.py').read_text(encoding='utf-8')
H=ast.parse(HOST); M=ast.parse(MOV)
# Unconditional top-level Name loads in binding RHS must have been defined/imported earlier.
bound=set(dir(builtins))
for n in H.body:
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
        bound.add(n.name)
    elif isinstance(n,ast.Import):
        for a in n.names: bound.add(a.asname or a.name.split('.')[0])
    elif isinstance(n,ast.ImportFrom):
        for a in n.names: bound.add(a.asname or a.name)
    elif isinstance(n,(ast.Assign,ast.AnnAssign)):
        val=n.value
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='_editor_commands_appearance' for t in n.targets):
            assert '_editor_commands_appearance' in bound, f'Binding before module import: line {n.lineno}'
            for v in ast.walk(val):
                if isinstance(v,ast.Name) and isinstance(v.ctx,ast.Load):
                    assert v.id in bound, f'Missing binding {v.id}: line {n.lineno}'
        targets=n.targets if isinstance(n,ast.Assign) else [n.target]
        for t in targets:
            if isinstance(t,ast.Name): bound.add(t.id)
expected={'APP_NAME','asset_path','dialog_title','save_json_settings','apply_theme'}
assigned={t.attr for n in H.body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='_editor_commands_appearance'}
assert assigned==expected,(assigned,expected)
assert {a.name for n in M.body if isinstance(n,ast.ImportFrom) and n.module=='datetime' for a in n.names}=={'datetime'}, 'Date/Time command import missing'
cmds=next(n for n in M.body if isinstance(n,ast.ClassDef) and n.name=='EditorCommandsAppearanceMixin')
actions=next(n for n in cmds.body if isinstance(n,ast.FunctionDef) and n.name=='_create_actions')
assert any(isinstance(n,ast.Name) and n.id=='datetime' for n in ast.walk(actions)), 'Date/Time callback unexpectedly changed'
# Scope gate: no implementation text may change from the frozen x8 extraction.
F=json.loads((ROOT/'qa/x8-method-fingerprints.json').read_text())
def methods(path,classname):
    s=contract_text(ROOT) if path.name=='app.py' else path.read_text(); lines=s.splitlines(keepends=True)
    cls=next(n for n in ast.parse(s).body if isinstance(n,ast.ClassDef) and n.name==classname)
    return {n.name:hashlib.sha256(''.join(lines[min([n.lineno]+[d.lineno for d in n.decorator_list])-1:n.end_lineno]).encode()).hexdigest() for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert methods(ROOT/'widgets/editor_commands_appearance.py','EditorCommandsAppearanceMixin')==F['relocated']
assert methods(ROOT/'app.py','MaqaronyPadWindow') | methods(ROOT/'widgets/mwpyn/editor_lifecycle.py','EditorLifecycleMixin')=={k:v for k,v in F['fingerprints'].items() if k not in F['relocated']}
print('PASS x8.1: startup bindings ordered; datetime present; original method definitions exact')
