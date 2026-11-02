#!/usr/bin/env python3
"""Stage x3: exact source identity for all 57 original editor methods.

Includes the x2 inherited formatting methods, moved insertion/clipboard
methods and methods remaining in the original source-editor class.
"""
from pathlib import Path
import ast, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
ENG=ROOT/"widgets/mwpyn/editor_source.py"
F=ENG.parent/"editor_formatting.py"
I=ENG.parent/"editor_insertion.py"
DATA=json.loads((ROOT/"qa/x3-method-fingerprints.json").read_text())
def methods(path, name):
    source=path.read_text(encoding="utf-8")
    # x12.6 permits only the approved source-editor cursor-centering correction.
    if path.name == "editor_source.py":
        source=source.replace("self.setCenterOnScroll(False)", "self.setCenterOnScroll(True)")
    lines=source.splitlines(keepends=True)
    classes=[n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name==name]
    assert len(classes)==1,(path,name,"missing/duplicate class")
    result={}
    for n in classes[0].body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            start=min((d.lineno for d in n.decorator_list),default=n.lineno)
            assert n.name not in result,(path,n.name,"duplicate")
            result[n.name]=hashlib.sha256("".join(lines[start-1:n.end_lineno]).encode()).hexdigest()
    return result
host=methods(ENG,"MarkopadSourceEditor")
formatting=methods(F,"EditorFormattingMixin")
view=methods(ENG.parent/"editor_search_view.py","EditorSearchViewMixin")
insertion=methods(I,"EditorInsertionMixin")
assert set(insertion)==set(DATA["moved_methods"]), "wrong x3 extraction inventory"
assert not (set(host)&set(formatting) or set(host)&set(insertion) or set(formatting)&set(insertion) or set(view)&(set(host)|set(formatting)|set(insertion))), "MRO shadowing"
assert len(host)+len(formatting)+len(insertion)+len(view)==DATA["original_count"]
assert host|formatting|insertion|view==DATA["all_method_sha256"], "original editor definition changed or missing"
src=ENG.read_text()
assert "class MarkopadSourceEditor(EditorSearchViewMixin, EditorInsertionMixin, EditorFormattingMixin, QPlainTextEdit):" in src
assert "from widgets.mwpyn.editor_insertion import EditorInsertionMixin" in src
assert "class EditorInsertionMixin:" in I.read_text()
assert "import re" in I.read_text()
for symbol in ("QMimeData","Qt","QTimer","QInputMethodEvent","QKeyEvent","QTextCursor"):
    assert symbol in I.read_text(),(symbol,"missing extracted-method dependency")
assert "widgets/mwpyn/editor_source.py" in str(ENG) or "markopad_editor_source.py" in str(ENG)
print(f"PASS x3 exact text: {len(insertion)} moved and {len(host)+len(formatting)+len(insertion)+len(view)}/{DATA['original_count']} original editor methods")
