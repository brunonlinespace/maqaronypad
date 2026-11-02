#!/usr/bin/env python3
"""x14.0: status group parity and preservation of all unrelated methods."""
from pathlib import Path
import ast,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/'app.py').read_text()
assert 'class EditorMessageStatusBar(QStatusBar)' in APP
assert 'self.status_left' not in APP and 'self.status_right' not in APP
assert 'Words {words:' not in APP
for key in ('operation_mode_label','document_status_label','view_status_label','format_status_label','message_label'):
 assert key in APP
for fragment in ('Chars {total_chars:,}', 'Ln {line}/{self.editor.document().blockCount()} Col {col}',
                 'f"{view} {self.zoom_percent}%"','f"{self.file_encoding.upper()} {newline}"',
                 'self.editor.overwrite_mode_changed.connect(self._on_editor_overwrite_mode_changed)',
                 'bar.addWidget(bar.message_label, 1)', 'QSizePolicy.Policy.Ignored', 'self._message_timer.start(int(timeout))'):
 assert fragment in APP,fragment
order=['bar.addWidget(self.operation_mode_label)','bar.addWidget(self.document_status_label, 3)', 'bar.addWidget(self.view_status_label)','bar.addWidget(self.format_status_label)','bar.addWidget(bar.message_label, 1)']
assert list(map(APP.index,order)) == sorted(map(APP.index,order))
# Exercise the exact method without importing Qt: minimal fake document/editor/labels.
tree=ast.parse(APP)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MaqaronyPadWindow')
m=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='update_status')
fn=ast.FunctionDef(name='update_status',args=m.args,body=m.body,decorator_list=[],returns=m.returns,type_comment=None)
ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<pad-status>','exec'),ns)
class Label:
 def setText(self,t):self.text=t
 def setToolTip(self,t):self.tooltip=t
class Cursor:
 def blockNumber(self):return 6
 def positionInBlock(self):return 17
class Document:
 def blockCount(self):return 109
class Editor:
 def textCursor(self):return Cursor()
 def toPlainText(self):return 'a'*1240
 def document(self):return Document()
 def overwriteMode(self):return True
class Owner:
 editor=Editor();operation_mode_label=Label();document_status_label=Label();view_status_label=Label();format_status_label=Label()
 file_newline='\r\n';file_encoding='utf-8';view_mode='split';zoom_percent=110
owner=Owner();ns['update_status'](owner)
assert owner.operation_mode_label.text=='Overwrite'
assert owner.document_status_label.text=='Ln 7/109 Col 18 Chars 1,240'
assert owner.view_status_label.text=='Split 110%'
assert owner.format_status_label.text=='UTF-8 CRLF'
record=json.loads((ROOT/'qa/x140-method-preservation.json').read_text())['unchanged_methods']
for key,oldhashes in record.items():
 f,name=key.split('::');src=ast.parse((ROOT/f).read_text());hashes=[hashlib.sha256(ast.dump(n,include_attributes=False).encode()).hexdigest() for n in ast.walk(src) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
 assert hashes==oldhashes,('unexpected method change',key)
print('PASS x14.0 status grouping, numbers, view/format, standalone messages, preserved methods')
