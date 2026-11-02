#!/usr/bin/env python3
"""Regression: the x6 preference module must be imported before its helper is bound."""
import ast
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"app.py"
s=p.read_text(encoding="utf-8")
t=ast.parse(s)
imports=[n.lineno for n in t.body if isinstance(n,ast.Import) and any(a.name=="widgets.mwpyn.editor_preferences" and a.asname=="_editor_preferences" for a in n.names)]
binds=[n.lineno for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Attribute) and isinstance(x.value,ast.Name) and x.value.id=="_editor_preferences" and x.attr=="save_json_settings" for x in n.targets)]
assert len(imports)==len(binds)==1 and imports[0]<binds[0], (imports,binds)
assert any(isinstance(n,ast.FunctionDef) and n.name=="save_json_settings" and n.lineno<binds[0] for n in t.body)
assert any(isinstance(n,ast.ImportFrom) and n.module=="widgets.mwpyn.editor_preferences" and any(a.name=="EditorPreferencesMixin" for a in n.names) and n.lineno<binds[0] for n in t.body)
print("PASS x6.1: preference import precedes helper binding; startup NameError prevented")
