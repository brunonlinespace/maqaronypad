#!/usr/bin/env python3
"""x14.4 Qt-free behavior and scoped-source regression gate."""
from __future__ import annotations
import ast
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
from maqarony_pad.widgets.message_conventions import (
    DEFAULT_MESSAGE_DURATION_MS, is_critical_status, status_sentence,
)

source = ROOT / 'app.py'
life = ROOT / 'widgets/mwpyn/editor_lifecycle.py'
assert 'APP_VERSION = "1.0.0-x14.4"' in source.read_text()
assert 'self.editor.textChanged.connect(self._on_text_changed)' in source.read_text()
assert 'self.editor.cursorPositionChanged.connect(self.update_status)' in source.read_text()

def extracted(path: Path, cls: str, name: str):
    tree = ast.parse(path.read_text())
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    method = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == name)
    ns = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method],type_ignores=[])), '<qa-x144>', 'exec'), ns)
    return ns[name]

show = extracted(source, 'EditorMessageStatusBar', 'showMessage')
clear = extracted(source, 'EditorMessageStatusBar', 'clearMessage')
set_backing = extracted(life, 'EditorLifecycleMixin', '_set_backing_state')
watch = extracted(life, 'EditorLifecycleMixin', 'handle_backing_path_event')
update_status = extracted(source, 'MaqaronyPadWindow', 'update_status')
text_changed = extracted(source, 'MaqaronyPadWindow', '_on_text_changed')

class Label:
    def __init__(self): self.text = ''; self.tooltip = ''
    def setText(self, text): self.text = text
    def setToolTip(self, text): self.tooltip = text
    def clear(self): self.text = ''
class Timer:
    def __init__(self): self.started = []; self.stopped = 0
    def start(self, value): self.started.append(value)
    def stop(self): self.stopped += 1
class StatusBar:
    def __init__(self):
        self.message_label = Label()
        self._message_timer = Timer()
    def showMessage(self, message, timeout=4000, *, warning_id=None):
        return show(self, message, timeout, warning_id=warning_id)
    def clearMessage(self, *, warning_id=None):
        return clear(self, warning_id=warning_id)

bar = StatusBar()
bar.showMessage('Backing file missing; the live MaqaronyPad document remains protected.', 6000, warning_id='backing_file')
assert bar._critical_editor_message and bar._warning_id == 'backing_file'
assert not bar._message_timer.started
bar.showMessage('Routine clipboard feedback.', 4000)
assert bar._warning_id == 'backing_file' and bar.message_label.text.startswith('Backing file')
bar.clearMessage(warning_id='something_else')
assert bar._warning_id == 'backing_file'
bar.clearMessage(warning_id='backing_file')
assert not bar._critical_editor_message and bar.message_label.text == ''
bar.showMessage('File changed outside MaqaronyPad.', warning_id='backing_file')
assert bar._warning_id == 'backing_file'
bar.showMessage('Could not save the active document.')
assert bar._critical_editor_message and bar._warning_id is None
bar.clearMessage(warning_id='backing_file')
assert bar.message_label.text == 'Could not save the active document.'
bar.showMessage('Saved example.md.')
assert not bar._critical_editor_message and bar._warning_id is None
assert bar._message_timer.started == [DEFAULT_MESSAGE_DURATION_MS]

class Banner:
    def __init__(self): self.visible = False
    def show(self): self.visible = True
    def hide(self): self.visible = False
class Button:
    def __init__(self): self.enabled = None
    def setEnabled(self, value): self.enabled = value
class BackingOwner:
    def __init__(self):
        self.bar = StatusBar()
        self.backing_state = 'normal'
        self.external_label = Label()
        self.external_banner = Banner()
        self.reload_external_button = Button()
        self.changed = 0
    def statusBar(self): return self.bar
    def _update_ui_state(self): self.changed += 1
    def _set_backing_state(self, state): set_backing(self, state)
    def _bind_document_watcher(self): pass

owner = BackingOwner()
owner.current_path = Path('/tmp/test.md')
initial = NS(digest='start',state=NS(device=1,inode=1,size=2,mtime_ns=1))
changed = NS(digest='changed',state=NS(device=1,inode=1,size=3,mtime_ns=2))
owner.disk_snapshot = initial
owner._current_disk_snapshot = lambda: changed
watch(owner)
assert owner.backing_state == 'changed' and owner.bar._warning_id == 'backing_file'
owner._current_disk_snapshot = lambda: None
watch(owner)
assert owner.backing_state == 'missing' and owner.bar._warning_id == 'backing_file'
owner.bar.showMessage('Could not load the requested file.')
owner._current_disk_snapshot = lambda: initial
watch(owner)
assert owner.backing_state == 'normal' and owner.bar.message_label.text == 'Could not load the requested file.'
owner.bar.clearMessage()
owner._current_disk_snapshot = lambda: None
watch(owner)
assert owner.bar._warning_id == 'backing_file'
owner._current_disk_snapshot = lambda: initial
watch(owner)
assert owner.bar.message_label.text == '' and owner.bar._warning_id is None
assert not owner.external_banner.visible

class Cursor:
    def blockNumber(self): return 2
    def positionInBlock(self): return 4
class Document:
    def blockCount(self): return 3
class Editor:
    def __init__(self):
        self.content = 'one\ntwo\n🎉é𐍈'
        self.extractions = 0
    def textCursor(self): return Cursor()
    def toPlainText(self): self.extractions += 1; return self.content
    def overwriteMode(self): return False
    def document(self): return Document()
editor = Editor()
class CounterOwner:
    _loading = False
    _search_refresh_suspended = True
    file_newline = '\n'
    file_encoding = 'utf-8'
    view_mode = 'split'
    zoom_percent = 100
    def __init__(self):
        self.editor = editor
        self._cached_status_char_count = None
        self.status_indicators_label = Label()
    def schedule_preview(self): pass
    def update_status(self): update_status(self)
    def _update_ui_state(self): pass
obj = CounterOwner()
update_status(obj)
assert 'Chars 11' in obj.status_indicators_label.text, obj.status_indicators_label.text
assert editor.extractions == 1
for _ in range(10): update_status(obj)
assert editor.extractions == 1, 'Cursor movement must not extract document again'
editor.content += 'a'
text_changed(obj)
update_status(obj)
assert 'Chars 12' in obj.status_indicators_label.text
assert editor.extractions == 2
obj._loading = True
editor.content = ''
text_changed(obj)
update_status(obj)
assert 'Chars 0' in obj.status_indicators_label.text and editor.extractions == 3
obj._loading = False
assert len('one\ntwo\n🎉é𐍈') == 11, 'Preserve Python code-point semantics'

# All non-approved production methods and complete files must remain identical.
record = json.loads((ROOT/'qa/x144-preservation.json').read_text())
assert record['predecessor'] == '1.0.0-x14.3' and record['release'] == '1.0.0-x14.4'
for rel, sha in record['untouched_production_files'].items():
    assert hashlib.sha256((ROOT.parent/rel).read_bytes()).hexdigest() == sha, rel
for rel, expected in record['untouched_methods'].items():
    tree = ast.parse((ROOT.parent/rel).read_text())
    current = {}
    for n in tree.body:
        if isinstance(n, ast.ClassDef):
            for m in n.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    current[n.name+'.'+m.name] = hashlib.sha256(ast.dump(m,include_attributes=False).encode()).hexdigest()
    for name, sha in expected.items(): assert current[name] == sha, (rel,name)
print('PASS: x14.4 warning identity, recovery isolation, Unicode counter caching and production preservation')
