#!/usr/bin/env python3
"""MaqaronyPad 1.0.0-x14.3: message conventions, delivery and predecessor-preservation gate."""
from __future__ import annotations
import ast,hashlib,json,sys
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent))
CONTRACT=json.loads((ROOT/'qa/x143-preservation.json').read_text())
assert CONTRACT['predecessor']=='1.0.0-x14.2'
assert CONTRACT['release']=='1.0.0-x14.3'
for rel,sha in CONTRACT['untouched_production_files'].items():
    assert hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest()==sha,rel
for rel,allowed in CONTRACT['unchanged_methods'].items():
    tree=ast.parse((ROOT.parent/rel).read_text())
    current={}
    for node in tree.body:
        if isinstance(node,ast.ClassDef):
            for method in node.body:
                if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    current[node.name+'.'+method.name]=hashlib.sha256(ast.dump(method,include_attributes=False).encode()).hexdigest()
    for name,expected in allowed.items():
        assert current[name]==expected,(rel,name)

def extract(source,owner,name):
    tree=ast.parse((ROOT/source).read_text())
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==owner)
    fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name==name)
    namespace={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'<msg-test>','exec'),namespace)
    return namespace[name]

class Label:
    def __init__(self): self.text=None;self.tooltip=None
    def setText(self,text):self.text=text
    def setToolTip(self,text):self.tooltip=text
    def clear(self):self.text=''
class Timer:
    def __init__(self):self.started=[];self.stopped=0
    def start(self,ms):self.started.append(ms)
    def stop(self):self.stopped+=1

status=extract('app.py','EditorMessageStatusBar','showMessage')
clear=extract('app.py','EditorMessageStatusBar','clearMessage')
obj=SimpleNamespace(message_label=Label(),_message_timer=Timer())
status(obj,'Saved example.md',1000)
assert obj.message_label.text=='Saved example.md.'
assert obj._message_timer.started==[4000]
status(obj,'File changed outside MaqaronyPad.',1000)
assert obj.message_label.text=='File changed outside MaqaronyPad.'
assert obj._critical_editor_message and obj._message_timer.started==[4000]
status(obj,'A routine message.',4000)
assert obj.message_label.text=='File changed outside MaqaronyPad.'
status(obj,'Saved example.md.',0)
assert obj.message_label.text=='Saved example.md.' and not obj._critical_editor_message
clear(obj)
assert obj.message_label.text=='' and obj._critical_editor_message is False
life=(ROOT/'widgets/mwpyn/editor_lifecycle.py').read_text()
for needle in ('Saved {self.current_path.name}.','Duplicated as {destination.name}.','Renamed {old_path.name} to {target.name}.','Deleted {self.current_path.name}; the open document is retained.', 'Saved MaqaronyPad version as {target.name};'):
    assert needle in life,needle
assert life.count('self.statusBar().showMessage(message, 5000)')==1, 'One preservation-specific confirmation'
assert 'self.statusBar().showMessage(f"Saved as {target.name}", 3000)' in life

from maqarony_pad.widgets.message_conventions import status_sentence,is_critical_status,DEFAULT_MESSAGE_DURATION_MS
assert DEFAULT_MESSAGE_DURATION_MS==4000
assert status_sentence('Renamed old to new')=='Renamed old to new.'
assert status_sentence('The linked file could not be found.')=='The linked file could not be found.'
assert not is_critical_status('Saved example.md.')
assert is_critical_status('Backing file missing; the live document remains protected.')
print('PASS: MaqaronyPad 1.0.0-x14.3 message conventions and predecessor scope')
