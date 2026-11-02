# Architecture — Markopad 0.2.10

Markopad has one authoritative document representation: Markdown source text in `MarkopadSourceEditor`.

```text
.md file
   ↓
document_io.py
   ↓
MarkopadSourceEditor  ← Markdown commands
   ↓
editor_preview.py (read-only rendering)
```

Saving writes the source editor text through the bounded atomic I/O layer. Preview is downstream only and never reconstructs or writes Markdown.

Primary modules:

- `markopad.py` — application/window/actions/Tabbed/Classic orchestration
- `editor_source.py` — Markdown editing, syntax highlighting, line numbers and source transformations
- `document_io.py` — bounded stable reads, encoding/BOM/newline handling, path/target-aware exact-content snapshots, race-safe atomic writes and no-clobber rename/create helpers
- `editor_preview.py` — read-only Qt Markdown rendering and resource policy
- `legacy_ricopad.py` — narrow one-way legacy envelope recogniser/stripper

There is no RTF parser/serializer and no general rich-document Markdown codec.

Lifecycle hardening introduced in 0.1.2 watches only the active document and relevant parent directory. In 0.1.6, when the document was opened through a symbolic link, Markopad additionally retains/watches that opened path entry for change detection and safe Save validation while preserving the historical resolved document path for ordinary UI, Rename and Delete behavior. The editor owns explicit normal/changed/missing backing state; this is standalone document protection, not workspace scanning.

## AppMenu and shortcut inventory

The File / Edit / Markdown / Insert / View / Settings / Help AppMenu is a persistent application surface in both Tabbed and Classic modes and explicitly participates in Qt's native/global-menu integration. The Keyboard Shortcuts dialog recursively inventories assigned QAction shortcuts from this live menu tree; only shortcuts without an AppMenu QAction are appended as explicit exceptions. This avoids a second manually maintained menu-backed shortcut inventory.

## Alternative toolbar presentation

The AppMenu remains the canonical command/order model. Classic flattens applicable menu inventory into a customizable one-row toolbar. App Drag-and-Drop remains a synthetic state-synchronised binary toolbar toggle, while Editor Toolbar is the canonical AppMenu submenu action reused as a flyout on both Modern (internal `tabbed`) and Classic. `Ctrl+Alt+Shift+T` is an independent shortcut-only mode switch. The two dirty-document policies remain menu-backed flyouts.

## x4.0 editor module convergence

The canonical Markdown source and read-only preview are `editor_source.py` and `editor_preview.py`. The previous `source_editor.py` and `preview.py` remain import-only compatibility shims. Original source-editor search/view methods are owned by `editor_search_view.py`, while the standalone window’s Find/Replace/view methods are owned by `window_search_view.py`. No dialog extraction or editor-folder reorganisation is included.
