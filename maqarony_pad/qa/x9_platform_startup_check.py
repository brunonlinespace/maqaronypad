#!/usr/bin/env python3
"""x9: exact source-text identity, startup-global bindings and README contract."""
from __future__ import annotations
import ast, hashlib, json
from pathlib import Path
from source_contract import contract_text
ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT/'app.py'
PLAT=ROOT/'editor_platform_startup.py'
BASE=json.loads((ROOT/'qa/x9-method-fingerprints.json').read_text())
source=PLAT.read_text(encoding='utf-8'); lines=source.splitlines(keepends=True)
found={}
for n in ast.parse(source).body:
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
        pos=min([n.lineno]+[d.lineno for d in n.decorator_list])-1
        found[n.name]=hashlib.sha256(''.join(lines[pos:n.end_lineno]).encode()).hexdigest()
assert found==BASE['relocated'], ('original top-level definition modified, removed, or added', found.keys())
host=HOST.read_text(); ht=ast.parse(host); pt=ast.parse(source)
assert not any(isinstance(n,ast.FunctionDef) and n.name in found for n in ht.body), 'old function implementation remains in host'
assert any(isinstance(n,ast.ImportFrom) and n.module=='editor_platform_startup' and set(a.name for a in n.names)==set(found) for n in ht.body), 'public helper reexports incomplete'
assert 'if __name__ == "__main__":\n    raise SystemExit(main())' in host
# Require all host-owned runtime references in relocated functions to have explicit bindings.
required={'APP_ID','APP_NAME','APP_VERSION','APP_ORG','ORGANIZATION_DOMAIN','DESKTOP_ID','MaqaronyPadWindow','apply_theme','load_json_settings','smoke_test'}
assigned={t.attr for n in ht.body if isinstance(n,ast.Assign) for t in n.targets if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='_editor_platform_startup'}
assert assigned==required,(assigned,required)
# At module load, no relocated module access may precede its import.
bound=set()
for n in ht.body:
    if isinstance(n,ast.Import):
        bound.update(a.asname or a.name.split('.')[0] for a in n.names)
    elif isinstance(n,ast.ImportFrom):
        bound.update(a.asname or a.name for a in n.names)
    elif isinstance(n,(ast.FunctionDef,ast.ClassDef)):
        bound.add(n.name)
    elif isinstance(n,ast.Assign):
        for t in n.targets:
            if isinstance(t,ast.Attribute) and isinstance(t.value,ast.Name) and t.value.id=='_editor_platform_startup':
                assert '_editor_platform_startup' in bound
                assert isinstance(n.value,ast.Name) and n.value.id in bound,(t.attr,ast.dump(n.value))
            elif isinstance(t,ast.Name): bound.add(t.id)
assert PLAT.parent == HOST.parent, 'resource-path helpers rely on original same-folder __file__ resolution'
assert 'def program_dir() -> Path:\n    return Path(__file__).resolve().parent' in source
assert 'def main(argv: list[str] | None = None) -> int:' in source
assert 'if args.maqaronypad_smoke_test: return smoke_test(theme)' in source
smokedef=next(n for n in ht.body if isinstance(n,ast.FunctionDef) and n.name=='smoke_test')
lines=host.splitlines(keepends=True)
smokesrc=''.join(lines[smokedef.lineno-1:smokedef.end_lineno])
assert hashlib.sha256(smokesrc.replace('1.0.0-x13.0','1.0.0-x8.1').encode()).hexdigest()==BASE['smoke_metadata_only_sha256'],'smoke harness changed beyond release version literal'
assert '--maqaronypad-smoke-test' in source
assert 'editor_platform_startup.py' in (ROOT/'packaging/fedora/build-appimage.sh').read_text()
# Do not relax README content baseline.
f6=json.loads((ROOT/'qa/x6-method-fingerprints.json').read_text())
readme=(ROOT.parent/'README.md').read_bytes().replace(b'> **Historical attribution correction (1.0.0-x11.0):** The 0.2.10 shortcuts/Quick Tour correction was released as **Markopad 0.2.10**, not MaqaronyPad. The archived sentence immediately below is retained unchanged.\n\n',b'')
assert hashlib.sha256(readme.replace(b'1.0.0-x13.0',b'1.0.0-x6.1')).hexdigest()==f6['github_readme_sha256'],'GitHub root README modified beyond version'
assert b'Current release: **1.0.0-x13.0**' in readme
assert (ROOT/'qa/x81_startup_globals_check.py').is_file()
print('PASS x9: seven original functions exact; smoke version-only, startup bindings safe, launcher/README/packaging intact')

# Execute the *real relocated module* against minimal Qt stand-ins. This catches
# missing module-global imports/bindings without claiming a live GUI test.
import contextlib, io, importlib.util, sys, types
qt=types.ModuleType('PyQt6'); gui=types.ModuleType('PyQt6.QtGui'); widgets=types.ModuleType('PyQt6.QtWidgets')
class FakeIcon:
    def __init__(self, *args): self.args=args
class FakeApp:
    @staticmethod
    def instance(): return None
    def __init__(self,*args): self.args=args
    def setApplicationName(self,*a): pass
    def setApplicationDisplayName(self,*a): pass
    def setApplicationVersion(self,*a): pass
    def setOrganizationName(self,*a): pass
    def setOrganizationDomain(self,*a): pass
    def setDesktopFileName(self,*a): pass
    def setWindowIcon(self,*a): pass
    def exec(self): return 17
class FakeEditor:
    MAX_DOCUMENT_CHARACTERS=25_000_000
    def load_text(self,v): self.text=v
    def toPlainText(self): return self.text
class FakePreview:
    def isReadOnly(self): return True
class FakeWindow:
    def __init__(self,*args,**kwargs): self.editor=FakeEditor(); self.preview=FakePreview()
    def refresh_preview_now(self): pass
    def close(self): pass
    def show(self): pass
qt.QtGui=gui;qt.QtWidgets=widgets;gui.QIcon=FakeIcon;widgets.QApplication=FakeApp
old={k:sys.modules.get(k) for k in ('PyQt6','PyQt6.QtGui','PyQt6.QtWidgets')}
try:
    sys.modules.update({'PyQt6':qt,'PyQt6.QtGui':gui,'PyQt6.QtWidgets':widgets})
    spec=importlib.util.spec_from_file_location('_maq_x9_platform_probe', PLAT)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.APP_ID='maqaronypad';module.APP_NAME='MaqaronyPad';module.APP_VERSION='1.0.0-x13.0'
    module.APP_ORG='brunonlinespace';module.ORGANIZATION_DOMAIN='github.com/brunonlinespace';module.DESKTOP_ID='maqaronypad'
    module.MaqaronyPadWindow=FakeWindow;module.apply_theme=lambda *a:None;module.load_json_settings=lambda: {'theme':'light'}
    assert module.program_dir()==ROOT
    assert module.project_root()==ROOT.parent
    assert module.asset_path('icons','maqaronypad.png').is_file()
    assert isinstance(module.application_icon(),FakeIcon)
    assert module.parse_args(['--version']).version
    assert module.host_process_environment().get('PATH') is not None
    output=io.StringIO()
    with contextlib.redirect_stdout(output): assert module.main(['--version'])==0
    assert output.getvalue().strip()=='MaqaronyPad 1.0.0-x13.0'
    smoke_ast=next(n for n in ast.parse(host).body if isinstance(n,ast.FunctionDef) and n.name=='smoke_test')
    exec(compile(ast.Module(body=[smoke_ast],type_ignores=[]),str(HOST),'exec'),module.__dict__)
    assert module.smoke_test('light')==0
    assert module.main(['--theme','dark'])==17
finally:
    for key,oldmod in old.items():
        if oldmod is None:sys.modules.pop(key,None)
        else:sys.modules[key]=oldmod
print('PASS x9: relocated startup functions execute with complete globals under Qt stand-ins (not live Qt)')
