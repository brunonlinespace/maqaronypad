#!/usr/bin/env python3
"""Qt-free x14.2 feedback/delivery tests and x14.1 production preservation gate."""
from __future__ import annotations
import ast
import hashlib
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
assert 'APP_VERSION = "1.0.0-x14.2"' in (ROOT/'app.py').read_text()
record=json.loads((ROOT/'qa/x142-preservation.json').read_text())

def methods(path):
    tree=ast.parse(path.read_text())
    found={}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    found[f'{node.name}.{child.name}']=hashlib.sha256(ast.dump(child,include_attributes=False).encode()).hexdigest()
        elif isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            found[node.name]=hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest()
    return found
for rel,expected in record['untouched_production_files'].items():
    assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected,rel
for rel,expected in record['unchanged_methods'].items():
    seen=methods(ROOT/rel)
    for name,digest in expected.items():assert seen[name]==digest,(rel,name)

def method(rel,cls,name,globals_dict=None):
    tree=ast.parse((ROOT/rel).read_text())
    owner=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==cls)
    fn=next(x for x in owner.body if isinstance(x,ast.FunctionDef) and x.name==name)
    ns=dict(globals_dict or {})
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),'<x142-test>','exec'),ns)
    return ns[name]

class Bar:
    def __init__(self):self.messages=[]
    def showMessage(self,msg,timeout=0):self.messages.append((msg,timeout))
class FakeOwner(NS):
    def statusBar(self):return self.bar

L='widgets/mwpyn/editor_lifecycle.py'
class QFileDialog:
    response=''
    @staticmethod
    def getSaveFileName(*args):return QFileDialog.response,''
class QMessageBox:
    @staticmethod
    def warning(*args):raise AssertionError('unexpected warning')
shared={'Path':Path,'QFileDialog':QFileDialog,'QMessageBox':QMessageBox,'SUPPORTED_EXTENSIONS':{'.md','.markdown','.mdown','.mkd'},'dialog_title':lambda t:t}

with tempfile.TemporaryDirectory() as work:
    directory=Path(work)
    source=directory/'source.md';source.write_text('# Example\n')
    target=directory/'copy.md'
    save_as=method(L,'EditorLifecycleMixin','save_as',shared)
    editor=FakeOwner(current_path=source,bar=Bar(),_save_as_target=lambda path:True)
    QFileDialog.response=str(target)
    assert save_as(editor) is True
    assert editor.bar.messages==[('Saved as copy.md',3000)]
    editor.bar.messages.clear();editor._save_as_target=lambda path:False
    assert save_as(editor) is False and not editor.bar.messages
    QFileDialog.response=''
    assert save_as(editor) is False and not editor.bar.messages
    QFileDialog.response=str(source)
    editor._save_as_target=lambda path:True
    assert save_as(editor) is True and not editor.bar.messages, 'nested Save must not duplicate'

    save_version=method(L,'EditorLifecycleMixin','save_version_as',shared)
    QFileDialog.response=str(target)
    for state,expected in (
        ('normal','Saved as copy.md'),
        ('changed','Saved MaqaronyPad version as copy.md; external disk copy preserved.'),
        ('missing','Saved MaqaronyPad version as copy.md; the original path remains missing.'),
    ):
        editor.bar.messages.clear();editor.backing_state=state
        assert save_version(editor) is True
        assert editor.bar.messages==[(expected,5000)],state
    editor._save_as_target=lambda path:False;editor.bar.messages.clear()
    assert save_version(editor) is False and not editor.bar.messages
    QFileDialog.response=''
    assert save_version(editor) is False and not editor.bar.messages

    # Watcher events: warn only when the transition becomes newly visible.
    watcher=method(L,'EditorLifecycleMixin','handle_backing_path_event')
    initial=NS(digest='a',state=NS(device=1,inode=2,size=1,mtime_ns=1))
    outside=NS(digest='b',state=NS(device=1,inode=2,size=1,mtime_ns=2))
    observed=[outside]
    editor=FakeOwner(bar=Bar(),current_path=source,disk_snapshot=initial,
        backing_state='normal',_current_disk_snapshot=lambda:observed[0],
        _bind_document_watcher=lambda:None,
        _set_backing_state=lambda state:None)
    editor._set_backing_state=lambda state:setattr(editor,'backing_state',state)
    watcher(editor);watcher(editor)
    assert editor.bar.messages==[('File changed outside MaqaronyPad.',5000)]
    observed[0]=None;watcher(editor);watcher(editor)
    assert editor.bar.messages[-1]==('Backing file missing; the live MaqaronyPad document remains protected.',6000)
    assert len(editor.bar.messages)==2
    observed[0]=initial;watcher(editor)
    assert editor.backing_state=='normal' and len(editor.bar.messages)==2

    # Link warnings are local and do not intercept working local links.
    QDesktopServices=NS(openUrl=lambda url:opened.append(url))
    QUrl=NS(fromLocalFile=lambda path:path)
    click=method('widgets/mwpyn/editor_preview.py','MarkdownPreview','_on_anchor_clicked',{'QDesktopServices':QDesktopServices,'QUrl':QUrl,'Path':Path})
    opened=[];missing=[]
    preview=NS(_document_dir=directory,missing_link_requested=NS(emit=lambda:missing.append(True)),external_link_requested=NS(emit=lambda url:None))
    def url(text,*,local=False):
        return NS(scheme=lambda:'file' if local else '',isRelative=lambda:not local,
                  toString=lambda:text,isLocalFile=lambda:local,toLocalFile=lambda:text)
    click(preview,url('absent.md'))
    assert missing==[True] and not opened
    (directory/'present.md').write_text('hello')
    click(preview,url('present.md'))
    assert len(opened)==1 and len(missing)==1
    click(preview,url(str(directory/'missing.md'),local=True))
    assert len(missing)==2

    # PDF completion must be newly produced, nonempty and have a PDF signature.
    pdf=method('widgets/mwpyn/editor_printing.py','EditorPrintingMixin','export_pdf',{})
    output=directory/'document.pdf'
    QFileDialog.response=str(output)
    class Printer:
        class PrinterMode:HighResolution=1
        class OutputFormat:PdfFormat=2
        def __init__(self,*args):self.path=None
        def setOutputFormat(self,value):pass
        def setOutputFileName(self,path):self.path=path
    pdf.__globals__.update({'Path':Path,'QFileDialog':QFileDialog,'QPrinter':Printer,'dialog_title':lambda s:s})
    contents=[b'%PDF-1.7\nmock']
    owner=FakeOwner(current_path=source,bar=Bar(),_printable_document=lambda:NS(print=lambda printer:output.write_bytes(contents[0]) if contents[0] is not None else None))
    pdf(owner)
    assert owner.bar.messages==[(f'Exported PDF to {output}',4000)]
    owner.bar.messages.clear();contents[0]=None
    pdf(owner)
    assert not owner.bar.messages,'stale existing PDF must not trigger success'
    QFileDialog.response='';pdf(owner);assert not owner.bar.messages

    # External opener/folder confirmation conditional on host accepted launch.
    launches=[]
    class Desktop:
        success=True
        @classmethod
        def openUrl(cls,path):launches.append(path);return cls.success
    folder=method(L,'EditorLifecycleMixin','open_containing_folder',{'Path':Path,'QUrl':NS(fromLocalFile=lambda x:x),'QDesktopServices':Desktop})
    folder_owner=FakeOwner(current_path=source,bar=Bar())
    folder(folder_owner)
    assert folder_owner.bar.messages==[('Opened the folder containing source.md.',3000)]
    folder_owner.bar.messages.clear();Desktop.success=False;folder(folder_owner)
    assert not folder_owner.bar.messages
    Desktop.success=True
    external=method(L,'EditorLifecycleMixin','open_external_editor',{'Path':Path,'QUrl':NS(fromLocalFile=lambda x:x),'QDesktopServices':Desktop,'QMessageBox':NS(warning=lambda *a:None),'dialog_title':lambda x:x})
    external_owner=FakeOwner(current_path=source,bar=Bar(),editor=NS(document=lambda:NS(isModified=lambda:False)),_file_policy=lambda *a:'ask')
    external(external_owner)
    assert external_owner.bar.messages==[('Opened source.md in an external editor.',3000)]
    external_owner.bar.messages.clear();Desktop.success=False;external(external_owner)
    assert not external_owner.bar.messages

# Signals and destination wiring; no extra widget or status layout changes.
preview=(ROOT/'widgets/mwpyn/editor_preview.py').read_text()
app=(ROOT/'app.py').read_text()
appearance=(ROOT/'widgets/editor_commands_appearance.py').read_text()
life=(ROOT/L).read_text()
assert 'missing_link_requested = pyqtSignal()' in preview
assert 'self.preview.missing_link_requested.connect(' in app
assert 'self.statusBar().showMessage("The linked file could not be found.", 4000)' in app
assert 'self.statusBar().showMessage(f"Loaded {self.current_path.name}", 3000)' in life
assert '"Editor canvas switched to a dark background."' in appearance
assert '"Editor canvas switched to a light background."' in appearance
assert 'self.statusBar().showMessage(f"Theme: {theme.capitalize()}.", 2500)' in appearance
assert app.count('bar.addWidget(bar.message_label, 1)')==1
assert app.count('bar.addPermanentWidget(self.status_indicators_label)')==1
assert 'status_indicators_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)' in app
assert all('self.'+old not in app for old in ('operation_mode_label','document_status_label','view_status_label','format_status_label'))
print('PASS x14.2 ten-message coverage, guarded outcomes, local delivery, unchanged x14.1 methods/layout')
