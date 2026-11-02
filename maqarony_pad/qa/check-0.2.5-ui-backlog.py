#!/usr/bin/env python3
"""Dependency-light Markopad 0.2.5 approved UI-backlog gate."""
from __future__ import annotations
import ast, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "markopad.py"
APP = APP_PATH.read_text(encoding="utf-8")
errors: list[str] = []

def req(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)

def tree_hash(root: Path, *, exclude: set[str] | None = None) -> str:
    exclude = exclude or set()
    h = hashlib.sha256()
    for p in sorted(root.glob("*.png")):
        if p.name in exclude:
            continue
        h.update(p.name.encode("utf-8") + b"\0" + p.read_bytes())
    return h.hexdigest()

def function_hashes(path: Path, names: set[str]) -> dict[str, str]:
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines(True)
    tree = ast.parse(src)
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            text = "".join(lines[node.lineno - 1:node.end_lineno])
            found[node.name] = hashlib.sha256(text.encode()).hexdigest()
    return found

req('APP_VERSION = "0.2.5"' in APP, "0.2.5 identity missing")

# Approved shortcut/name contract.
for frag in (
    'self.theme_light_action = self._action("Light", lambda: self.set_theme("light"), "Ctrl+Alt+Shift+1", checkable=True)',
    'self.theme_dark_action = self._action("Dark", lambda: self.set_theme("dark"), "Ctrl+Alt+Shift+2", checkable=True)',
    'self.theme_system_action = self._action("System", lambda: self.set_theme("system"), "Ctrl+Alt+Shift+3", checkable=True)',
    'self.tabbed_mode_action = self._action("Tabbed (default)", lambda: self.set_toolbar_mode("tabbed"), checkable=True)',
    'self.classic_mode_action = self._action("Classic", lambda: self.set_toolbar_mode("classic"), checkable=True)',
    'self.toolbar_style_toggle_action = self._action("Editor Toolbar", self.toggle_toolbar_style, "Ctrl+Alt+Shift+T", checkable=True)',
    'self.addAction(self.toolbar_style_toggle_action)',
    '("Editor Toolbar", self.toolbar_style_toggle_action)',
):
    req(frag in APP, f"missing 0.2.5 shortcut/name contract: {frag}")
req('self._action("Tabbed (default)", lambda: self.set_toolbar_mode("tabbed"), "Ctrl+Alt+Shift+1"' not in APP,
    "old direct Tabbed shortcut remains")
req('self._action("Classic", lambda: self.set_toolbar_mode("classic"), "Ctrl+Alt+Shift+2"' not in APP,
    "old direct Classic shortcut remains")
req('self.toolbar_style_toggle_action = self._action("Toolbar Style"' not in APP,
    "old Toolbar Style label remains on compact toggle")

# Heading AppMenu icon and Toggle Comment surfaces.
for frag in (
    'self.heading_menu_action = headings.menuAction()',
    '"heading_menu_action":"heading-group"',
    '"comment_action":"comment-toggle"',
    '[self.undo_action, self.redo_action, self.duplicate_line_action, self.delete_line_action, self.comment_action, self.find_action, self.goto_action, self.replace_action]',
    '("Edit", "comment", "Toggle Comment", self.comment_action)',
):
    req(frag in APP, f"missing UI backlog wiring: {frag}")

# Classic default must not expand just because Comment is now available.
module = ast.parse(APP)
default_assign = next(
    n for n in module.body
    if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "CLASSIC_TOOLBAR_DEFAULT" for t in n.targets)
)
defaults = ast.literal_eval(default_assign.value)
req(defaults == [
    "new", "open", "save",
    "undo", "redo", "find",
    "bold", "italic", "inline_code",
    "image", "link",
    "source", "split", "preview", "toolbar_style", "customize_classic",
], f"Classic default changed unexpectedly: {defaults}")

# Canonical icon family is the old 121 assets plus the approved Comment pair.
ICON_ROOT = ROOT / "assets" / "toolbar-icons"
old_tree = {
    "light": "460c0c1d6b625a43fa76efb84178b4baf2c5faef2727c6f12e226101fd863dd9",
    "dark": "32700ede0da30ebe1f2f67e090c29d50751c9bf42978f22235abc8ed637dc700",
}
comment_hash = {
    "light": "8672a84b6898bff8c4184f04e8059d1578f542d7cd7f11a039d43c7debeac963",
    "dark": "1c769b67fd7a4dca3c09b69b7f63aa88b97de1ba620b85b810ff3b00ae16a169",
}
for scheme in ("light", "dark"):
    files = sorted((ICON_ROOT / scheme).glob("*.png"))
    req(len(files) == 122, f"{scheme} icon family must contain 122 assets")
    req(tree_hash(ICON_ROOT / scheme, exclude={"comment-toggle.png"}) == old_tree[scheme],
        f"existing {scheme} icon family changed")
    comment = ICON_ROOT / scheme / "comment-toggle.png"
    req(comment.is_file(), f"missing {scheme}/comment-toggle.png")
    if comment.is_file():
        req(hashlib.sha256(comment.read_bytes()).hexdigest() == comment_hash[scheme],
            f"wrong {scheme} Comment Toggle asset")

# Retain completed Item 32 and its explicit Find/Replace exclusion.
for frag in (
    'self.copy_action = self._action("Copy", self._copy_active_text_surface',
    'self.select_all_action = self._action("Select All", self._select_all_active_text_surface',
    'def _preview_is_active_text_surface(self) -> bool:',
    'self.preview.copy()', 'self.preview.selectAll()',
    'obj is self.splitter.handle(1)',
    'def _reset_content_splitter(self) -> None:',
    'self.splitter.setSizes([3, 2])',
):
    req(frag in APP, f"Item 32 contract regressed: {frag}")
find_expected = {
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
actual = function_hashes(APP_PATH, set(find_expected))
for name, digest in find_expected.items():
    req(actual.get(name) == digest, f"Find/Replace exclusion drifted: {name}")
for rel, digest in {
    "source_editor.py":"0264f2515d499c3a877742e08877535323b825021fe7c1c15d0f95a9c2f2e327",
    "preview.py":"e9fa111f4119402e7f4396c9b39d5ec5fdf19627e45e907be036cbd555bb8965",
    "document_io.py":"b2f8d439af424ac296c297d0d9d781062b55dbd955c72ae5cbc1862788cefe38",
}.items():
    req(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest,
        f"protected implementation changed: {rel}")

if errors:
    print("Markopad 0.2.5 check failed:")
    for e in errors:
        print("-", e)
    sys.exit(1)
print("PASS: Markopad 0.2.5 approved UI-backlog contract")
