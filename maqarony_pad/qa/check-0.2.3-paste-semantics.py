#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.3 Item 30 Paste semantic-correction gate."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "markopad.py"
APP = APP_PATH.read_text(encoding="utf-8")
errors: list[str] = []


def req(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def sha(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def method_source(name: str) -> str:
    tree = ast.parse(APP)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MarkopadWindow")
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(APP, node) or ""

req('APP_VERSION = "0.2.3"' in APP, "0.2.3 identity missing")
req(
    'self.paste_action = self._action("Paste", self.paste, QKeySequence.StandardKey.Paste)' in APP,
    "Paste is not the smart StandardKey.Paste command",
)
req(
    'self.paste_plain_action = self._action("Paste as Plain Text", lambda: self.editor.paste(), "Ctrl+Shift+V")' in APP,
    "Paste as Plain Text Ctrl+Shift+V command missing",
)
req('Paste as Markdown' not in APP, "obsolete visible Paste as Markdown wording remains")
req('paste_markdown_action' not in APP, "obsolete paste_markdown_action remains")

smart = method_source("paste")
for fragment in (
    'mime.hasHtml()', 'doc = QTextDocument()', 'doc.setHtml(html)',
    'text = doc.toMarkdown()', 'text = doc.toPlainText()', 'data:[^\\n)]*',
    'self.editor.insert_guarded_text(text)',
):
    req(fragment in smart, f"smart Paste conversion contract missing: {fragment}")
req('self.editor.paste()' not in smart, "normal Paste still routes to literal editor Paste")

# Menu and Tabbed command surface must expose the same corrected pair.
req('edit.addAction(self.cut_action); edit.addAction(self.copy_action); edit.addAction(self.paste_action); edit.addAction(self.paste_plain_action)' in APP,
    "Edit AppMenu Paste pair not corrected")
tabbed = method_source("_create_tabbed_toolbar")
req('[self.cut_action, self.copy_action, self.paste_action, self.paste_plain_action, self.delete_action, self.select_all_action]' in tabbed,
    "Tabbed Home Paste pair not corrected")

icons = method_source("_refresh_action_icons")
req('"paste_action":"paste"' in icons, "Paste icon mapping changed/missing")
req('"paste_plain_action":"paste-plain"' in icons, "Paste as Plain Text icon mapping missing")
req('paste-markdown' not in icons, "paste-markdown icon is still wired")

# Classic persisted IDs deliberately preserve pre-0.2.3 semantics without a fragile one-shot migration:
# old paste_markdown (smart) now points to smart Paste; old paste (literal) points to Plain Text.
catalog = method_source("_classic_toolbar_catalog")
req('("Edit", "paste_markdown", "Paste", self.paste_action)' in catalog,
    "Classic legacy smart-Paste ID no longer preserves semantic intent")
req('("Edit", "paste", "Paste as Plain Text", self.paste_plain_action)' in catalog,
    "Classic legacy literal-Paste ID no longer preserves semantic intent")

# All three canonical icon assets remain byte-for-byte present; paste-markdown is unwired only.
asset_hashes = {
    "assets/toolbar-icons/light/paste.png": "a1d4e4a3feb57fe943fcc756e1c5ba2316d9d6c1b8444cdc6622750948bd2504",
    "assets/toolbar-icons/light/paste-plain.png": "483a48c75b4e0bdada4d5f6e274acaf15264f4d4ceb569852f0ea26e51497df4",
    "assets/toolbar-icons/light/paste-markdown.png": "d1359fbd60bc8247bb78af00a0f013d953f93862e8320ffd21b8994bdef64b3e",
    "assets/toolbar-icons/dark/paste.png": "824604b2dd8eeaaa9a6575967cba4f0a3d960ae25409f6a2289ff9f610146cec",
    "assets/toolbar-icons/dark/paste-plain.png": "a0fa3cd350f5f8e509fc76d3f1dad4610d21f96215de5d9d8855e2866933e171",
    "assets/toolbar-icons/dark/paste-markdown.png": "c0af62f91e93091d3b0e3b14fb56bf5ce94733d3d734903dcdb09a97628e2932",
}
for relative, digest in asset_hashes.items():
    req((ROOT / relative).is_file(), f"canonical Paste asset missing: {relative}")
    if (ROOT / relative).is_file():
        req(sha(relative) == digest, f"canonical Paste asset changed: {relative}")

# Protect all lower-level editor/file/persistence engines: only command semantics/routing change.
protected = {
    "source_editor.py": "0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py": "e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py": "b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
    "settings_io.py": "9ddc28b52955e0a2d65def935693a29c49766d52318b2a2082bb5f9f31468159",
    "legacy_ricopad.py": "2984a424345666509420bd8d9825394e6d8b6b70620d1eb3c50e519be71cdc40",
}
for relative, digest in protected.items():
    req(sha(relative) == digest, f"out-of-scope protected file changed: {relative}")

if errors:
    print("Markopad 0.2.3 check failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)
print("PASS: Markopad 0.2.3 Item 30 Paste semantic-correction contract")
