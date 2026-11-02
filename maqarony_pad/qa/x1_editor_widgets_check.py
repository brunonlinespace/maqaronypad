#!/usr/bin/env python3
"""1.0.0-x1.1 source-identity gate anchored to MaqaronyPad 0.3.4."""
from pathlib import Path
import ast,hashlib,json,re
BASE=Path(__file__).resolve().parents[1]
expected=json.loads((BASE/'qa/x1-method-fingerprints.json').read_text())
engine=(BASE/'widgets/mwpyn/editor_source.py').read_text()
widgets=(BASE/'widgets/mwpyn/editor_widgets.py').read_text()
def defs(source):
    lines=source.splitlines(keepends=True)
    return {n.name:''.join(lines[min((d.lineno for d in n.decorator_list),default=n.lineno)-1:n.end_lineno]) for n in ast.parse(source).body if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef))}
wd, ed=defs(widgets),defs(engine)
for name in ('HighlightRule','MarkdownHighlighter','LineNumberArea','_scheme'):
    assert name in wd and name not in ed,(name,'definition location')
    assert hashlib.sha256(wd[name].encode()).hexdigest()==expected[name],name
assert 'MarkopadSourceEditor' in ed  # The entire original method inventory is checked by x2_editor_formatting_check.py
match=re.search(r'MARKDOWN_COLOR_SCHEMES = \{.*?\n\}\n',widgets,re.S)
assert match and hashlib.sha256(match.group(0).encode()).hexdigest()==expected['color_schemes']
for name in ('HighlightRule','MarkdownHighlighter','LineNumberArea','_scheme','MARKDOWN_COLOR_SCHEMES'):
    assert name in engine.split('from widgets.mwpyn.editor_widgets import',1)[1],('missing re-export',name)
assert 'from widgets.mwpyn.editor_widgets import' in engine
assert not (BASE/'mwpyn').exists(), '0.3.4 folder layout must be preserved'
print('PASS: x1.1 extracted widget and original 0.3.4 editor definitions preserved')
