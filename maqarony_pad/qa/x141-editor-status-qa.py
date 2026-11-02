#!/usr/bin/env python3
"""Qt-free corrective x14.1 editor-status contract and preservation gate."""
import ast, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'app.py').read_text()
record=json.loads((ROOT/'qa/x141-method-preservation.json').read_text())
assert 'APP_VERSION = "1.0.0-x14.1"' in src
nodes=[n for n in ast.walk(ast.parse(src)) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
by={}
for n in nodes:
 name=n.name
 k=name if name not in by else name+'#'+str(sum(t==name or t.startswith(name+'#') for t in by))
 by[k]=hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest()
for k,v in record['unchanged_method_hashes'].items():assert by[k]==v,('modified unrelated method',k)
for old in ('operation_mode_label','document_status_label','view_status_label','format_status_label'):
 assert 'self.'+old not in src, old
assert src.count('bar.addWidget(bar.message_label, 1)')==1
assert src.count('bar.addPermanentWidget(self.status_indicators_label)')==1
assert 'status_indicators_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)' in src
assert 'status_indicators_label.setMinimumWidth(0)' in src
assert 'self.statusBar().showMessage(' in src
cls=next(n for n in ast.parse(src).body if isinstance(n,ast.ClassDef) and n.name=='MaqaronyPadWindow')
method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='update_status')
ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),'<pad-status>','exec'),ns)
class Label:
 def setText(self,t): self.text=t
 def setToolTip(self,t): self.tooltip=t
class Cursor:
 def blockNumber(self):return 19
 def positionInBlock(self):return 17
class Doc:
 def blockCount(self):return 109
class Editor:
 def textCursor(self):return Cursor()
 def toPlainText(self):return 'x'*4842
 def document(self):return Doc()
 def overwriteMode(self):return False
class Owner:
 editor=Editor();file_newline='\r\n';file_encoding='utf-8';view_mode='split';zoom_percent=100
 status_indicators_label=Label()
o=Owner();ns['update_status'](o)
assert o.status_indicators_label.text=='Insert · Ln 20/109 Col 18 Chars 4,842 · UTF-8 CRLF · Split 100%',o.status_indicators_label.text
assert o.status_indicators_label.tooltip==o.status_indicators_label.text
o.editor.overwriteMode=lambda:True;o.view_mode='preview';o.zoom_percent=300
ns['update_status'](o)
assert o.status_indicators_label.text.startswith('Overwrite · Ln 20/109')
assert o.status_indicators_label.text.endswith('· Preview 300%')
# The standalone status remains QMainWindow-owned; no stylesheet, palette, geometry or size-grip edits.
print('PASS x14.1 two-label status, exact indicator string, formatting and protected editor methods')
