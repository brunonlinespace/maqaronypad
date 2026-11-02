#!/usr/bin/env python3
"""x12 canonical app-module relocation: pinned source text, launch and history contract."""
from __future__ import annotations
import ast, hashlib, json, re, stat
from pathlib import Path
OLD_FILE='maqarony_pad.py'
VERSION='1.0.0-x13.0'
PREVIOUS='1.0.0-x11.0'
HISTORY_MARKER=b'# MaqaronyPad 1.0.0-x11.0'
INTERNAL_MARKER=b'# MaqaronyPad 1.0.0-x11.0'
ROOT=Path(__file__).resolve().parents[1]
OUTER=ROOT.parent
GOLD=json.loads((ROOT/'qa/x12-filename-fingerprints.json').read_text())
assert (ROOT/'app.py').is_file()
assert not (ROOT/OLD_FILE).exists(), 'obsolete application module still present'
source=(ROOT/'app.py').read_text(encoding='utf-8')
lines=source.splitlines(keepends=True)
methods={}
def text_of(n):
    pos=min([n.lineno]+[d.lineno for d in n.decorator_list])-1
    return ''.join(lines[pos:n.end_lineno])
for node in ast.parse(source).body:
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
        method_text=text_of(node)
        if node.name=='smoke_test':
            # Embedded version assertion is the sole authorised release-identity edit.
            assert 'APP_VERSION == "'+VERSION+'"' in method_text
            method_text=method_text.replace('APP_VERSION == "'+VERSION+'"','APP_VERSION == "1.0.0-x12.0"')
        methods['function:'+node.name]=hashlib.sha256(method_text.encode()).hexdigest()
    elif isinstance(node,ast.ClassDef):
        for method in node.body:
            if isinstance(method,(ast.FunctionDef,ast.AsyncFunctionDef)):
                methods['method:'+node.name+'.'+method.name]=hashlib.sha256(text_of(method).encode()).hexdigest()
# x12.4/x12.5: the original top-level functions remain in the consolidated keyboard-shortcuts module.
shortcut_source=(ROOT/'widgets/keyboard_shortcuts.py').read_text(encoding='utf-8')
shortcut_lines=shortcut_source.splitlines(keepends=True)
for helper in ast.parse(shortcut_source).body:
    if isinstance(helper,(ast.FunctionDef,ast.AsyncFunctionDef)) and helper.name in ('_shortcut_tokens','_shortcut_query_matches'):
        first=min([helper.lineno]+[d.lineno for d in helper.decorator_list])-1
        text=''.join(shortcut_lines[first:helper.end_lineno])
        methods['function:'+helper.name]=hashlib.sha256(text.encode()).hexdigest()
# x12.5: recover the original four class-method fingerprints from their
# new module functions. Restore only their historical class indentation.
for module, method in (('about_dialog', 'show_about'), ('quick_tour', 'show_quick_tour'),
                       ('keyboard_shortcuts', '_shortcut_catalog'), ('keyboard_shortcuts', 'show_shortcuts')):
    file_source=(ROOT/'widgets'/f'{module}.py').read_text(encoding='utf-8')
    functions=[n for n in ast.parse(file_source).body if isinstance(n,ast.FunctionDef) and n.name==method]
    assert len(functions)==1, ('missing relocated method', method)
    definition=ast.get_source_segment(file_source,functions[0]) + '\n'
    old_text='\n'.join('    '+line if line else line for line in definition.split('\n'))
    methods['method:MaqaronyPadWindow.'+method]=hashlib.sha256(old_text.encode()).hexdigest()
assert methods==GOLD['methods'], 'original method source text changed after module relocation'
launcher=(OUTER/'main.py').read_text(encoding='utf-8')
assert 'entry_point = program_dir / "app.py"' in launcher
assert 'runpy.run_path(str(entry_point), run_name="__main__")' in launcher
assert 'APP_VERSION = "'+VERSION+'"' in source
assert bool((OUTER/'main.py').stat().st_mode & 0o111), 'main.py must be executable'
for relative in ('packaging/fedora/build-appimage.sh','packaging/windows/build-windows-portable.ps1'):
    script=(ROOT/relative).read_text(encoding='utf-8')
    assert 'app.py' in script and OLD_FILE not in script, relative
readme=(OUTER/'README.md').read_bytes().replace(VERSION.encode(),PREVIOUS.encode())
assert hashlib.sha256(readme).hexdigest()==GOLD['previous_root_readme_sha256'], 'GitHub root README changed beyond current version'
notes=(ROOT/'docs/RELEASE_NOTES.md').read_bytes()
changes=(ROOT/'docs/CHANGELOG.md').read_bytes()
# SHA256 of the predecessor's entire history, which must remain an unmodified suffix.
for data,key in ((notes,'previous_release_notes_sha256'),(changes,'previous_changelog_sha256')):
    marker=data.index(HISTORY_MARKER)
    assert hashlib.sha256(data[marker:]).hexdigest()==GOLD[key], 'historical release records changed'
internal=(ROOT/'README.md').read_bytes()
assert hashlib.sha256(internal[internal.index(INTERNAL_MARKER):]).hexdigest()==GOLD['previous_internal_readme_sha256'], 'internal README history modified'
print('PASS x12: canonical app.py, executable launcher, unchanged method source, preserved public README and history')
