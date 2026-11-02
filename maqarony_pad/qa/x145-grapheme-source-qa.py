#!/usr/bin/env python3
"""x14.5: scoped source/preservation, grapheme, caching, warning continuity."""
from __future__ import annotations
import ast, hashlib, importlib.util, json, sys, types
from pathlib import Path
from types import SimpleNamespace as NS

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
record=json.loads((ROOT/'qa/x145-predecessor.json').read_text(encoding='utf-8'))
assert (record['predecessor'],record['release']) == ('1.0.0-x14.4','1.0.0-x14.5')

# Protect all unchanged predecessor files, not merely current release hashes.
for rel,expected in record['unchanged_files'].items():
    p=PROJECT/rel
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==expected,rel
current_png={str(p.relative_to(PROJECT)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in PROJECT.rglob('*.png')}
assert len(current_png)==257 and current_png==record['png_files'],'PNG bytes/count changed'
assert not list(PROJECT.rglob('*.svg')),'Unexpected packaged SVGs'
assert '*.svg' in (ROOT/'app.py').read_text(),'External SVG content selection unintentionally removed'
assert 'APP_VERSION = "1.0.0-x14.5"' in (ROOT/'app.py').read_text()
assert 'count_markdown_characters(self.editor.document())' in (ROOT/'app.py').read_text()

# The only changed existing application method body is update_status;
# version self-test constants are checked through the new version probe.
tree=ast.parse((ROOT/'app.py').read_text(encoding='utf-8'))
current={}
for node in tree.body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
        current[node.name]=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
    elif isinstance(node,ast.ClassDef):
        for member in node.body:
            if isinstance(member,(ast.FunctionDef,ast.AsyncFunctionDef)):
                current[node.name+'.'+member.name]=hashlib.sha256(ast.dump(member,include_attributes=False).encode()).hexdigest()
assert len(current)==record['app_original_ast_count']
# The existing smoke_test contains the application version identity only;
# replacing the new literal with the predecessor value must restore its AST.
smoke=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='smoke_test')
class RebaseVersion(ast.NodeTransformer):
    def visit_Constant(self,node):
        if node.value=='1.0.0-x14.5':return ast.copy_location(ast.Constant(value='1.0.0-x14.4'),node)
        return node
smoke=RebaseVersion().visit(smoke)
assert hashlib.sha256(ast.dump(smoke,include_attributes=False).encode()).hexdigest()==record['app_smoke_test_original_ast']

for name,expected in record['app_unchanged_ast_methods'].items():
    assert current[name]==expected,('unexpected app method change',name)

# Segmenter protocol doubles. No extra runtime dependency: 'regex' is QA-only.
try: import regex
except ImportError: raise SystemExit('FAIL: Unicode grapheme QA needs regex test dependency')
class FakeBoundaryFinder:
    class BoundaryType: Grapheme=object()
    calls=[]
    def __init__(self,kind,text):
        assert kind is self.BoundaryType.Grapheme
        self.calls.append(text)
        self.boundaries=[m.end() for m in regex.finditer(r'\X',text)]
        self.index=0
    def toNextBoundary(self):
        if self.index>=len(self.boundaries): return -1
        pos=self.boundaries[self.index];self.index+=1
        return pos
class FakeBlockUserData: pass
qcore=types.ModuleType('PyQt6.QtCore');qcore.QTextBoundaryFinder=FakeBoundaryFinder
qgui=types.ModuleType('PyQt6.QtGui');qgui.QTextBlockUserData=FakeBlockUserData
old={name:sys.modules.get(name) for name in ('PyQt6','PyQt6.QtCore','PyQt6.QtGui')}
sys.modules.update({'PyQt6':types.ModuleType('PyQt6'),'PyQt6.QtCore':qcore,'PyQt6.QtGui':qgui})
try:
    spec=importlib.util.spec_from_file_location('maq_grapheme',ROOT/'widgets/mwpyn/character_count.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
finally:
    for k,v in old.items():
        if v is None:sys.modules.pop(k,None)
        else:sys.modules[k]=v

class TextBlock:
    def __init__(self,doc,index):self.doc=doc;self.index=index
    def isValid(self):return 0<=self.index<len(self.doc.entries)
    def revision(self):return self.doc.entries[self.index][1]
    def userData(self):return self.doc.entries[self.index][2]
    def setUserData(self,value):self.doc.entries[self.index][2]=value
    def text(self):return self.doc.entries[self.index][0]
    def next(self):return TextBlock(self.doc,self.index+1)
class Document:
    def __init__(self,parts):self.entries=[[v,1,None] for v in parts]
    def begin(self):return TextBlock(self,0)
    def blockCount(self):return len(self.entries)
    def change(self,index,new):
        self.entries[index][0]=new;self.entries[index][1]+=1

cases=[('',0),('ABC',3),('😀',1),('e\u0301',1),('👩‍👩‍👧‍👦',1),('🇵🇹',1),('👍🏽',1),('क्\u200dष',1),('**Hello**',9),('a b!',4),('# Título',8),('A\u2028B',3)]
for source,expected in cases:
    actual=module.count_markdown_characters(Document([source]))
    assert actual==expected,(source,actual,expected)
assert module.count_markdown_characters(Document(['']))==0
assert module.count_markdown_characters(Document(['','']))==1
assert module.count_markdown_characters(Document(['**Hi**','😀','']))==9  # 6 + newline + 1 + newline
assert module.count_markdown_characters(Document(['e\u0301','ABC']))==5  # 1+newline+3

multi=Document(['First','👩‍👩‍👧‍👦',''])
assert module.count_markdown_characters(multi)==8
initial=len(FakeBoundaryFinder.calls)
for _ in range(12): assert module.count_markdown_characters(multi)==8
assert len(FakeBoundaryFinder.calls)==initial,'Unchanged block was segmented repeatedly'
multi.change(1,'😀😀')
assert module.count_markdown_characters(multi)==9
assert FakeBoundaryFinder.calls[-1]=='😀😀'

# Independently exercise actual update_status/_on_text_changed methods via AST,
# without importing the GUI. The test counts each call to the segmenter.
def extracted(name):
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='MaqaronyPadWindow')
    method=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name==name)
    scope={'count_markdown_characters':module.count_markdown_characters}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),'<app method>', 'exec'),scope)
    return scope[name]
status=extracted('update_status')
text_change=extracted('_on_text_changed')
class Cursor:
    def blockNumber(self):return 1
    def positionInBlock(self):return 2
class Label:
    def __init__(self):self.text=''
    def setText(self,text):self.text=text
    def setToolTip(self,text):pass
class Editor:
    def __init__(self,doc):self.doc=doc;self.extractions=0
    def textCursor(self):return Cursor()
    def toPlainText(self):self.extractions+=1;raise AssertionError('Status must never copy entire text')
    def overwriteMode(self):return False
    def document(self):return self.doc
class Host:
    _loading=False
    _search_refresh_suspended=True
    file_newline='\n'
    file_encoding='utf-8'
    view_mode='split'
    zoom_percent=100
    def __init__(self):
        self.doc=Document(['**Hi**','😀',''])
        self.editor=Editor(self.doc)
        self.status_indicators_label=Label()
        self._cached_status_char_count=None
        self.renders=0
    def schedule_preview(self):self.renders+=1
    def update_status(self):status(self)
    def _update_ui_state(self):pass
host=Host()
status(host)
assert 'Chars 9' in host.status_indicators_label.text
count=len(FakeBoundaryFinder.calls)
for _ in range(30):status(host)
assert len(FakeBoundaryFinder.calls)==count,'Cursor-only status recalculated graphemes'
assert host.editor.extractions==0
host.doc.change(1,'🇵🇹👍🏽')
text_change(host)
assert 'Chars 10' in host.status_indicators_label.text
assert len(FakeBoundaryFinder.calls)==count+1,'Only changed text block should be re-segmented'
host._loading=True
host.doc.change(0,'')
text_change(host)
assert host._cached_status_char_count is None
status(host)
assert 'Chars 4' in host.status_indicators_label.text  # empty + newline + 2 emoji + newline
assert host.editor.extractions==0

# The previous warning correction remains literally unchanged in source and
# is exercised through the same 14.4 message owner pathways.
sys.path.insert(0,str(PROJECT))
from maqarony_pad.widgets.message_conventions import DEFAULT_MESSAGE_DURATION_MS
from maqarony_pad.widgets.message_conventions import is_critical_status,status_sentence
bar=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorMessageStatusBar')
functions={}
for name in ('showMessage','clearMessage'):
    method=next(m for m in bar.body if isinstance(m,ast.FunctionDef) and m.name==name)
    namespace={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])),f'<warning {name}>','exec'),namespace)
    functions[name]=namespace[name]
class Timer:
    def __init__(self):self.started=[]
    def start(self,n):self.started.append(n)
    def stop(self):pass
class WarningBar:
    def __init__(self):self.message_label=Label();self.message_label.setToolTip=lambda x:None;self.message_label.clear=lambda :setattr(self.message_label,'text','');self._message_timer=Timer()
    def showMessage(self,msg,timeout=4000,*,warning_id=None):return functions['showMessage'](self,msg,timeout,warning_id=warning_id)
    def clearMessage(self,*,warning_id=None):return functions['clearMessage'](self,warning_id=warning_id)
warning=WarningBar()
warning.showMessage('Backing file missing; the live document remains protected.',warning_id='backing_file')
assert warning._warning_id=='backing_file'
warning.showMessage('Routine feedback.')
assert warning._warning_id=='backing_file'
warning.showMessage('Could not save document.')
assert warning._critical_editor_message and warning._warning_id is None
warning.clearMessage(warning_id='backing_file')
assert warning.message_label.text=='Could not save document.'
warning.showMessage('Saved document.md.')
assert not warning._critical_editor_message and warning._message_timer.started==[DEFAULT_MESSAGE_DURATION_MS]

print('PASS: x14.5 Unicode graphemes, source semantics, block+host caching, warning regression, source scope, PNG/SVG checks')
print('NOTE: Unicode segmentation uses regex-based Qt interface double; live PyQt6 behavior not covered.')
