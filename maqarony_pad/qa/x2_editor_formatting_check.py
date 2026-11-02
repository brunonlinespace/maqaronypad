#!/usr/bin/env python3
"""Exact-original-source x2 editor formatting extraction gate.

All source-editor methods, not only those extracted, are checked against the
original unmodified x1 baseline, using text-level definition SHA-256 hashes.
"""
from pathlib import Path
import ast, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
ENG=ROOT/"widgets/mwpyn/editor_source.py"
MOD=ENG.parent/"editor_formatting.py"
DATA=json.loads((ROOT/"qa/x2-method-fingerprints.json").read_text())
def methods(path, name):
    source=path.read_text(encoding="utf-8")
    # x12.6 permits only the approved source-editor cursor-centering correction.
    if path.name == "editor_source.py":
        source=source.replace("self.setCenterOnScroll(False)", "self.setCenterOnScroll(True)")
    lines=source.splitlines(keepends=True)
    nodes=ast.parse(source).body
    classes=[node for node in nodes if isinstance(node,ast.ClassDef) and node.name==name]
    assert len(classes)==1,(path,name,"missing/duplicate class")
    result={}
    for node in classes[0].body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            begin=min((d.lineno for d in node.decorator_list), default=node.lineno)
            assert node.name not in result,(path,node.name,"duplicate")
            text="".join(lines[begin-1:node.end_lineno])
            result[node.name]=hashlib.sha256(text.encode()).hexdigest()
    return result
host=methods(ENG,"MarkopadSourceEditor")
mixin=methods(MOD,"EditorFormattingMixin")
view=methods(ENG.parent/"editor_search_view.py","EditorSearchViewMixin")
insertion=methods(ENG.parent/"editor_insertion.py","EditorInsertionMixin")
extracted=set(DATA["moved_methods"])
assert set(mixin)==extracted, ("extracted inventory",set(mixin)^extracted)
assert not ((set(host)&set(mixin)) | (set(host)&set(insertion)) | (set(mixin)&set(insertion)) | (set(view)&set(host)) | (set(view)&set(mixin)) | (set(view)&set(insertion))), "method shadowing in editor inheritance"
assert len(host)+len(mixin)+len(insertion)+len(view)==DATA["original_count"]
assert host|mixin|insertion|view==DATA["all_method_sha256"], "original method source changed or missing"
src=ENG.read_text()
assert "class MarkopadSourceEditor(EditorSearchViewMixin, EditorInsertionMixin, EditorFormattingMixin, QPlainTextEdit):" in src
assert "editor_formatting import EditorFormattingMixin" in src
assert "class EditorFormattingMixin:" in MOD.read_text()
# The extracted helpers intentionally use these original module globals.
assert "import re" in MOD.read_text()
assert "from PyQt6.QtGui import QTextCursor" in MOD.read_text()
print(f"PASS: x2.0 formatting methods {len(mixin)}/{len(extracted)} and original editor methods {len(host)+len(mixin)+len(insertion)+len(view)}/{DATA['original_count']} text-identical")
