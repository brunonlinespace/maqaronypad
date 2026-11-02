#!/usr/bin/env python3
"""1.0.0-x17.8: exercise frozen-module path and status callback without Qt.

The AppImage freezes app.py from within maqarony_pad/, so its import root is
that inner folder, not the Portable outer root. A lazy absolute import of
maqarony_pad.widgets raised ModuleNotFoundError inside QAction callbacks.
"""
from pathlib import Path
import ast
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
source = (root / "app.py").read_text(encoding="utf-8")
tree = ast.parse(source)
status_class = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "EditorMessageStatusBar")
method = next(n for n in status_class.body if isinstance(n, ast.FunctionDef) and n.name == "showMessage")
imports = [n.module for n in ast.walk(method) if isinstance(n, ast.ImportFrom)]
assert imports == ["widgets.message_conventions"], imports
assert "maqarony_pad.widgets.message_conventions" not in source
smoke = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "smoke_test")
smoke_text = ast.get_source_segment(source, smoke)
assert "action.trigger()" in smoke_text
for family in ("harmony", "humility", "heritage", "halcyon"):
    assert family in smoke_text
for theme in ("system", "dark", "light"):
    assert theme in smoke_text

# Actually execute the unchanged status-message method in a Python process
# whose import path contains only the inner package root (plus stdlib).
code = r"""
import ast, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root))
assert 'maqarony_pad' not in sys.modules
from widgets.message_conventions import status_sentence
assert status_sentence('Theme: Light') == 'Theme: Light.'
source = (root / 'app.py').read_text()
tree = ast.parse(source)
klass = next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='EditorMessageStatusBar')
method = next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name=='showMessage')
namespace={}
exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(root/'app.py'), 'exec'), namespace)
class Label:
    def __init__(self): self.text=''; self.tooltip=''
    def setText(self, value): self.text=value
    def setToolTip(self,value): self.tooltip=value
class Timer:
    def stop(self): pass
    def start(self, ms): assert ms==4000
class Status:
    def __init__(self): self.message_label=Label(); self._message_timer=Timer()
s=Status()
namespace['showMessage'](s, 'Theme: Light.', 2500)
assert s.message_label.text=='Theme: Light.'
namespace['showMessage'](s, 'Maqa Icons Halcyon.', 2500)
assert s.message_label.text=='Maqa Icons Halcyon.'
namespace['showMessage'](s, 'File changed outside MaqaronyPad.', 2500, warning_id='backing_file')
assert s._critical_editor_message and s._warning_id=='backing_file'
namespace['showMessage'](s, 'Saved test.md.', 2500)
assert not s._critical_editor_message and s.message_label.text=='Saved test.md.'
"""
result = subprocess.run([sys.executable, '-I', '-c', code, str(root)],capture_output=True, text=True)
assert result.returncode == 0, result.stderr
print('PASS x17.8 frozen path status callback, real seven-action smoke contract')
