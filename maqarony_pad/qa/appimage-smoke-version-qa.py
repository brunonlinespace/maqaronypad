#!/usr/bin/env python3
"""Regression for x1.0.1 smoke failure: stale version literal caused exit 3.

Exercise the REAL smoke_test function (AST-extracted without PyQt6), including
all theme/icon transitions. Deliberately mismatch the app's runtime version,
then inject the historical hard-coded version assertion to prove rejection.
"""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "app.py").read_text(encoding="utf-8")
TREE = ast.parse(TEXT)
VERSION = next(n.value.value for n in TREE.body if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "APP_VERSION" for t in n.targets)
    and isinstance(n.value, ast.Constant))
MANIFEST = json.loads((ROOT.parent / "suite-pythoine-component.json").read_text(encoding="utf-8"))
assert VERSION == MANIFEST["version"], (VERSION, MANIFEST["version"])
smoke = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == "smoke_test")
version_checks = [n for n in ast.walk(smoke) if isinstance(n, ast.Compare)
    and len(n.ops)==1 and isinstance(n.ops[0], ast.Eq)
    and isinstance(n.left, ast.Call) and isinstance(n.left.func, ast.Attribute)
    and n.left.func.attr=="applicationVersion"]
assert len(version_checks)==1, "Smoke must inspect the actual application's runtime version"
assert len(version_checks[0].comparators)==1 and isinstance(version_checks[0].comparators[0],ast.Name) and version_checks[0].comparators[0].id=='APP_VERSION'
assert not any(isinstance(n,ast.Constant) and isinstance(n.value,str) and re.fullmatch(r'\d+\.\d+\.\d+(?:-x[\d.]+)?',n.value)
               for n in ast.walk(smoke)), "Hard-coded release literal inside smoke_test"

class FakeApplication:
    declared_version = VERSION
    @classmethod
    def instance(cls): return cls()
    def applicationVersion(self): return self.declared_version

class FakeAction:
    def __init__(self, cb): self.cb=cb; self.checked=False
    def trigger(self): self.cb(); self.checked=True
    def isChecked(self): return self.checked
    def icon(self): return FakeIcon()
class FakeIcon:
    def isNull(self): return False
class FakeText:
    MAX_DOCUMENT_CHARACTERS=25_000_000
    def load_text(self,txt): self.txt=txt
    def toPlainText(self): return self.txt
class FakePreview:
    def isReadOnly(self): return True
class FakeLabel:
    def __init__(self): self.value=''
    def text(self): return self.value
class FakeStatus:
    def __init__(self): self.message_label=FakeLabel()
class FakeWindow:
    def __init__(self,theme_override):
        self.theme=theme_override
        self.editor=FakeText()
        self.preview=FakePreview()
        self._status=FakeStatus()
        self.new_action=FakeAction(lambda:None)
        self.icon_family='harmony'
        self.icon_family_actions={family:FakeAction(lambda f=family:self.set_family(f)) for family in ('harmony','humility','heritage','halcyon')}
        for theme in ('system','dark','light'):
            setattr(self,f'theme_{theme}_action',FakeAction(lambda t=theme:self.set_theme(t)))
    def statusBar(self): return self._status
    def refresh_preview_now(self): pass
    def set_theme(self,theme):
        if theme!=self.theme:
            self._status.message_label.value=f'Theme: {theme.capitalize()}.'
        self.theme=theme
    def set_family(self,family):
        self.icon_family=family
        self._status.message_label.value=f'Maqa Icons {family.title()}.'
    def close(self): pass

# Compile the exact production smoke-test function without importing Qt.
ns={'QApplication':FakeApplication,'apply_theme':lambda *a:None,
    'MaqaronyPadWindow':FakeWindow,'APP_NAME':'MaqaronyPad','APP_VERSION':VERSION}
exec(compile(ast.fix_missing_locations(ast.Module(body=[smoke],type_ignores=[])),str(ROOT/'app.py'),'exec'),ns)
for theme in ('system','dark','light'):
    assert ns['smoke_test'](theme)==0, theme
FakeApplication.declared_version='0.0.0'
assert ns['smoke_test']('system')==3, "Smoke failed to reject runtime-version mismatch"
FakeApplication.declared_version=VERSION
# Historical failure is precisely a stale constant in the predicate.
import copy
wrong=copy.deepcopy(smoke)
needle=next(n for n in ast.walk(wrong) if isinstance(n,ast.Compare)
    and isinstance(n.left,ast.Call) and isinstance(n.left.func,ast.Attribute)
    and n.left.func.attr=='applicationVersion')
needle.comparators=[ast.Constant(value='1.0.0')]
wrong_ns=dict(ns)
exec(compile(ast.fix_missing_locations(ast.Module(body=[wrong],type_ignores=[])),str(ROOT/'app.py'),'exec'),wrong_ns)
assert wrong_ns['smoke_test']('system')==3, "Historical hard-coded version defect was not reproduced"
print('PASS 1.0.2 real smoke-test logic: 3 themes, 4 icon families, version mismatch and stale-literal rejection')
