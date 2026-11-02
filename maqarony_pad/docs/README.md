# MaqaronyPad 1.0.0-x17.1 — Editor Toolbar icon wiring

Editor Toolbar uses `layout-ribbon.png`; Modern uses `toolbar-tabbed.png`; Classic uses `toolbar-classic.png`. The actions and checked-state behavior are unchanged.

---

# MaqaronyPad 1.0.0-x17.0 — Unicode source character statistics

The Chars status indicator counts extended Unicode grapheme clusters in literal Markdown source, including punctuation/markup and spaces, and one logical newline between text blocks. The editor/preview and file-size safety limits are unchanged.

---

# MaqaronyPad documentation

MaqaronyPad 1.0.0-x14.4 is a focused, source-faithful Markdown editor. The Markdown text is always the document; Preview is a read-only rendering surface.

Use the Markdown menu and toolbar commands for headings, bold, italic, strikethrough, Quote Block, bullet/number/task lists, indentation, inline code and fenced Code Block. Insert provides Markdown-native links, image references, tables, horizontal rules, Date and Time, Date Only, Time Only and the 40-symbol curated dialog. Ctrl+/ toggles Markdown-compatible HTML comments; Insert toggles Insert/Overwrite mode.

Find/Replace uses the bottom MaqaronyPad panel with gold matches, a real selected active result, X/Y counter, F3/Shift+F3 navigation and safe bounded replacement.

View is aligned with the Marko family: Full Screen, Show Status; Word Wrap, Line Numbers and Dark Editor; Locked Mode; Editor Layout and Editor Toolbar; then Editor Zoom and Editor Miscellaneous. App Theme, App Drag-and-Drop and the remembered dirty-file policies live under Settings. Viewing configuration persists between sessions. Fresh/default application chrome is Light and the Source/Preview canvas independently defaults to Light, matching current Marko Plus; stored explicit choices continue to override those defaults.

Toolbar offers **Tabbed** and **Classic**. Both use icon-only 52×52 command buttons with 36×36 icons from the canonical Marko Plus command family. MaqaronyPad carries the full paired light/dark family while exposing only commands that belong to the standalone editor. Classic follows AppMenu order, may be customised while active, may be completely empty, uses the Editor Toolbar submenu as a flyout, retains the compact App Drag-and-Drop toggle, and keeps the two dirty-document policy flyouts.

The AppMenu remains available in both toolbar modes and explicitly uses Qt's native/global-menu contract. Keyboard Shortcuts uses that live File/Edit/Markdown/Insert/View/Settings/Help menu tree as its authoritative menu-backed shortcut inventory, with only menu-less shortcuts appended explicitly.

Lifecycle hardening watches only the active file and parent directory, preserving changed or missing backing files without workspace scanning.

Privacy is deliberate: MaqaronyPad has no Open Recent feature and does not keep a recent-file list.

Key documents:

- `CURRENT_ARCHITECTURE.md` — current x11 module map and historical-source distinctions
- `ARCHITECTURE.md` — source-authoritative model (historical Markopad 0.2.10 architecture record)
- `TOOLBAR_LAYOUTS.md` — Tabbed/Classic and Source/Preview layouts
- `FORMAT_SUPPORT.md` — Markdown-only file surface
- `FEATURE_MATRIX.md` — supported capabilities
- `SECURITY_REVIEW.md` — safety design
- `QA_TEST_PLAN.md` — release checks
