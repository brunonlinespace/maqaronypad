#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.4 Item 32 Split/Preview routing gate."""
from __future__ import annotations
import ast, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APP_PATH=ROOT/'markopad.py'
APP=APP_PATH.read_text(encoding='utf-8')
errors=[]
def req(cond,msg):
    if not cond: errors.append(msg)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def function_hashes(path,names):
    src=path.read_text(encoding='utf-8'); lines=src.splitlines(True); tree=ast.parse(src); found={}
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name in names:
            text=''.join(lines[node.lineno-1:node.end_lineno])
            found[node.name]=hashlib.sha256(text.encode()).hexdigest()
    return found

req('APP_VERSION = "0.2.4"' in APP,'0.2.4 identity missing')
req('self.copy_action = self._action("Copy", self._copy_active_text_surface' in APP,'Copy is not active-surface routed')
req('self.select_all_action = self._action("Select All", self._select_all_active_text_surface' in APP,'Select All is not active-surface routed')
for frag in (
    'def _preview_is_active_text_surface(self) -> bool:',
    'self.preview.copy()',
    'self.preview.selectAll()',
    'and not self._preview_is_active_text_surface()',
    'event.type() == QEvent.Type.FocusIn',
    'surface = "source"',
    'surface = "preview"',
    'obj is self.splitter.handle(1)',
    'def _reset_content_splitter(self) -> None:',
    'self.splitter.setSizes([3, 2])',
    'self.persist_preferences()',
): req(frag in APP,f'missing Item 32 contract: {frag}')
req(APP.count('and not self._preview_is_active_text_surface()') >= 2,'mutation and Undo/Redo guards must both respect Preview focus')
# Find/Replace was explicitly excluded: protect the 0.2.3 implementations exactly.
find_expected={
 'toggle_find_panel':'71f0e4ae264ae93f6bd9e841c9318acde9e38eb4f0226024ec999c35b9282176',
 'show_find_panel':'cd29299db2ff3d70bdac987e863a9025670c8915a9eb5cb2e18f190cb603d1d2',
 'hide_find_panel':'af4cbfe32a17880be4b828e2a35fa49d3b8863f0407762326b31e5c12faddc62',
 '_replace_flags':'bc00028a0e7c3a6026376d08aa36cc71d5a4eff26aa00857f4a440bfe8d5fe25',
 '_selection_matches_replace_query':'36f37fd8e9c7d395780c023c1242844d31669c82cef2c995734d2bcbf0a265e5',
 'find_next':'02dd0ed642eac78346b45b1838272af907fe1c13b4032230662041e8de4046b2',
 'find_previous':'7c5287263d9b261493dda25596ea6d02f00652252f13b3108f6a6f5851e58b4b',
 'replace_one':'9f57adfc86391f374b99ec3601fa75c2098b1915396c5730853971c39028d73d',
 'replace_all':'95006ab8891200aa5a78bf79ae13c31e102a9cd17c37ee14a192626c9128fd49',
}
actual=function_hashes(APP_PATH,set(find_expected))
for name,digest in find_expected.items(): req(actual.get(name)==digest,f'Find/Replace exclusion drifted: {name}')
# Item 32 must not rewrite editor/preview/file engines.
for rel,digest in {
 'source_editor.py':'0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327',
 'preview.py':'e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965',
 'document_io.py':'b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38',
}.items(): req(sha(ROOT/rel)==digest,f'protected implementation changed: {rel}')
if errors:
    print('Markopad 0.2.4 check failed:')
    for e in errors: print('-',e)
    sys.exit(1)
print('PASS: Markopad 0.2.4 Item 32 Split/Preview interaction contract')
