# MaqaronyPad 1.0.0-x17.4 — Maqa icon families (2026-11-01)

Added selectable Maqa Icons Harmony (default), Humility, and Heritage. The App Icons submenu follows App Theme in Settings; three mutually exclusive Modern toolbar commands follow theme controls with a separator. Selection persists, refreshes command artwork and available workspace icons, and preserves underlying editor workflows. New family artwork comes directly from the supplied 144-per-theme packs.

---

# MaqaronyPad 1.0.0-x17.3 — Quick Tour crash hotfix (2026-10-31)

- Restore the four missing Qt imports (`QWizardPage`, `QVBoxLayout`, `QLabel`, `QTimer`) in the extracted Quick Tour module. The undefined `QWizardPage` raised a Python `NameError` inside the toolbar QAction callback, which PyQt6 translated into a fatal abort.
- Add an executable, Qt-independent Quick Tour construction regression test covering all seven pages, action handling and close cleanup. Preserve all existing tutorial text, dialogs, other commands and icon files unchanged.

---

# MaqaronyPad 1.0.0-x17.2 — Exit on Editor Toolbar (2026-10-31)

- Expose the existing **Exit QAction** last in the **Modern File** tab, preceded by a separator.
- Include Exit in the **default Classic toolbar selection**, ordered last among File commands. Preserve saved Classic customizations (including whether Exit was selected).
- Retain `exit.png` artwork, the existing Quit shortcut (`Ctrl+Q` on Linux) in its tooltip, and the existing close/unsaved-changes workflow.
- No changes to AppMenu ordering, icon artwork, Markdown functionality or file-handling behavior. Live PyQt6/KDE testing remains pending.

---

# MaqaronyPad 1.0.0-x17.1 — Editor Toolbar icon wiring (2026-10-31)

Targeted icon-only wiring from x17.0: **Editor Toolbar** AppMenu parent and shared toolbar flyout use `layout-ribbon.png`; the **Modern (default)** and **Classic** mutually exclusive submenu actions use `toolbar-tabbed.png` and `toolbar-classic.png`, respectively. The parent icon does not follow selection. No icon artwork, toolbar mode semantics, preferences, or Markdown/file behavior changed.

---

# MaqaronyPad 1.0.0-x17.0 — canonical toolbar icon pack (2026-10-31)

Icon-only release from 1.0.0-x14.5: replaced the toolbar-icons light/dark collections with the 144-per-theme supplied pack (no retained old assets). Editor Layout uses `layout-markdown.png`; the Light/Dark/System actions use `theme-light.png`/`theme-dark.png`/`theme-system.png`; the Insert > Link AppMenu group uses `link-group.png`. Editor and file workflows are otherwise unchanged.

---

# MaqaronyPad 1.0.0-x17.0 — Grapheme-aware source Chars

- Replace the previous Unicode-code-point `Chars` statistic with extended grapheme clusters for Markdown **source**.
- Count logical newlines once; cache per unchanged text block and between document edits. Preserve cursor-status layout and x14.4 backing-warning correction.
- Zero SVG assets, 257 PNGs preserved unchanged. External document SVG selection is not an SVG icon resource.

---

# MaqaronyPad 1.0.0-x14.4 — Targeted status corrections

- Backing-file recovery dismisses only a warning explicitly owned by the backing-file monitor; other unresolved critical warnings persist.
- Cache the existing Python-code-point character count and invalidate on every text edit, including programmatic loads. Cursor-only updates no longer copy the full document to count characters.
- Keep x14.3 editor message conventions, layout, ordinary messages, the deliberately removed Words count, editing/formatting and file safety unchanged.

---

# MaqaronyPad 1.0.0-x14.3 — Status-message coverage convergence

This edition adds the ten approved status-message events only, preserving existing source, editor UI and filesystem behavior.

Five logical fields: Insert/Overwrite; Line/Column/total Chars; Source/Split/Preview plus Zoom; Encoding/Newline; and independently visible Messages. Remove status Words. Preserve the existing Pad status-bar styling, numeric grouping, and all other editor behavior.

---

# MaqaronyPad 1.0.0-x13.0 — Exclusive-install permission preservation

Align the existing no-clobber fallback with MaqaronyDesk x16.2 by restoring staged-file permissions using guarded `os.fchmod`. No other production implementation changes; historical release records below remain unchanged.

---

# MaqaronyPad 1.0.0-x12.6 — Source editor scrolling corrective

Disable automatic centered overscrolling below the last source line, using Sheepy Pad 0.4.1 as the reference. No other editor or application logic changes. Previous release records remain below unchanged.

---

# MaqaronyPad 1.0.0-x12.5 — Canonical application module filename

The main application module is `app.py` (formerly `maqarony_pad.py`). The outer `main.py` portable launcher, Fedora AppImage and Windows build scripts now use that filename. The previous release record follows without changes.

---

# MaqaronyPad 1.0.0-x11.0 — Current documentation and metadata corrections

This is a documentation and release-metadata correction to 1.0.0-x10.0, not a new editor-extraction stage. The x10 document lifecycle extraction, Markdown editing, file I/O, previews, workspace-independent protections, shortcuts, toolbar artwork and application integration remain unchanged.

- Current in-app documentation identifies this release.
- Current architecture is described in `docs/CURRENT_ARCHITECTURE.md`, without rewriting the historical Markopad architecture account.
- The repository-root README contains a separate attribution correction for the original Markopad 0.2.10 release; its archived historical sentence is preserved unchanged.
- The current AppStream entry correctly describes these documentation corrections and records the x10 lifecycle extraction (the older x10 metadata entry remains unchanged as an historical artifact).
- Temporary-file prefixes remain `.maqarony_pad-`, the existing behavior since the first MaqaronyPad rebrand. No file I/O changes were made.

## Preserved development history (verbatim below)

# 1.0.0-x7.0 — Standalone Tabbed/Classic presentation extraction

The 24 original Tabbed and Classic toolbar presentation methods are relocated without rewriting their implementations into `editor_ribbon_retro.py`. MaqaronyPad maintains its original command catalogue, rendering and toolbar behaviour. x1–x6.1 extraction history and functionality remain unchanged. The public GitHub README is unchanged except the current release version references.

# 1.0.0-x7.0 — Preferences extraction and public README restoration

- Original preference-restoration and persistence methods moved into `editor_preferences.py`, without changing their definitions or configuration paths.
- The repository-root `README.md` was restored from the original MaqaronyPad 0.3.4 source; only current-version references were updated.
- Existing Markdown, preview, file-safety and presentation behaviour remains unchanged.

# 1.0.0-x3.0 — insertion and clipboard extraction

Stage x3 moves 16 existing methods into `editor_insertion.py` unchanged. x4 contains the approved source/preview filename alignment.

## 1.0.0-x2.0 — corrective x1 extraction from 0.3.4

- Based on the authoritative MaqaronyPad 0.3.4 source, retaining its standalone `MarkopadSourceEditor` and `MarkdownPreview` layout.
- Existing highlighter, line-number and colour-scheme helper definitions moved without modification to `editor_widgets.py`.
- Supersedes MaqaronyPad 1.0.0-x1.0 as the master for subsequent experiments; MepyNamu 1.0.0-x1.0 remains paired and unchanged.

<p align="center">
  <a href="https://github.com/brunonlinespace/maqaronypad">
    <img
      src="maqarony_pad/assets/icons/maqaronypad-about.png"
      alt="MaqaronyPad"
      width="256"
    >
  </a>
</p>

# MaqaronyPad

**Friendly. Fast. Focused.**

MaqaronyPad is a focused standalone Markdown editor built around an authoritative Markdown source editor and a read-only rendered preview. It reads and writes ordinary Markdown files directly, without introducing a private document format or workspace database.

Current release: **1.0.0-x7.0**

0.2.10 is a narrow corrective/UI-ordering release: Quick Tour's Keyboard Shortcuts button now opens MaqaronyPad's existing shortcuts dialog correctly, the About dialog uses **Configuration**, and the Modern File toolbar's More Actions buttons follow the File → More Actions AppMenu order.

Repository: <https://github.com/brunonlinespace/maqaronypad>

## What MaqaronyPad is

MaqaronyPad is designed for people who want a dedicated desktop Markdown editor with direct source editing, live preview, strong file-safety behavior, and conventional application menus and toolbars.

Markdown source is always authoritative. Preview is downstream and read-only; it never reconstructs or writes the stored document.

Supported Markdown filename extensions are `.md`, `.markdown`, `.mdown`, and `.mkd`.

MaqaronyPad deliberately does not expose a generic plain-text compatibility mode. Unsupported file types are rejected rather than silently opened under a different document model.

## Highlights

- Native **Markdown source editing and read-only preview**.
- Three persistent document layouts: **Source Only**, **Source + Preview**, and **Preview Only**.
- **Modern** six-tab toolbar plus a fully customisable **Classic** toolbar.
- Persistent native/global **AppMenu** available in both toolbar modes.
- Markdown headings, emphasis, lists, task lists, quotes, inline/fenced code, links, image references, tables, horizontal rules, symbols, and date/time insertion.
- Smart **Paste** that converts rich/HTML clipboard content to Markdown, plus **Paste as Plain Text**.
- Bottom **Find / Replace** panel with bounded search results, next/previous navigation, Replace and Replace All.
- **Go To Line**, line numbers, word wrap, Insert/Overwrite mode, source/preview zoom, and separate Source/Preview fonts.
- Persistent **Locked Mode** for protection against accidental edits.
- Safe Save, Save As, Duplicate, Rename, Delete, and external-editor workflows.
- Atomic Markdown saving, external-change detection, and protection when the active backing file is deleted or renamed away.
- Source/Preview-aware Copy and Select All behavior in Split mode, with source-mutating commands protected while Preview owns interaction focus.
- System, Dark, and Light application themes with independent editor-canvas control.
- Searchable **Keyboard Shortcuts**, persistent **Quick Tour**, bundled documentation, GitHub and issue links.
- Canonical Marko light/dark command-icon family with 122 assets per theme.

## Interface

### Modern toolbar

The **Modern** toolbar is the default command surface. Internally this remains the established `tabbed` toolbar mode.

Its six tabs are:

- **File** — New, Open, Save, file actions, Print, Export PDF, New Window, Exit, and related document commands.
- **Home** — clipboard, selection, headings, Markdown formatting, lists, comments, line operations, Find, and Go To Line.
- **Insert** — images, tables, links, horizontal rules, dates/times, symbols, and code-related insertion commands.
- **View** — document layout, Full Screen, status, zoom, editor controls, and the Editor Toolbar flyout.
- **Settings** — application theme, drag-and-drop behavior, editor canvas, and dirty-document policies.
- **Help** — documentation, Quick Tour, Keyboard Shortcuts, GitHub, issues, and About.

Hover over a toolbar command to see its name and assigned keyboard shortcut.

Use **Ctrl+Tab** and **Ctrl+Shift+Tab** to move between Modern toolbar tabs. Double-click a tab to collapse its controls; click a tab while collapsed to reveal them again. The collapsed state persists.

### Classic toolbar

Classic uses the same application actions in one traditional customisable toolbar.

Its catalogue follows AppMenu order. Every Classic item is removable, so the toolbar may be completely empty; the permanent AppMenu remains the recovery and control surface.

The **Editor Toolbar** flyout is available from both Modern and Classic and contains:

- **Modern (default)**
- **Classic**
- **Customise Classic Bar…**

`Ctrl+Alt+Shift+T` independently flips between Modern and Classic.

### AppMenu

The native application menu remains available in both toolbar modes and follows the canonical:

**File → Edit → Markdown → Insert → View → Settings → Help**

command model.

The Keyboard Shortcuts dialog inventories the live application actions from this menu structure, so assigned menu shortcuts remain visible without maintaining a separate duplicate list.

## Editing

MaqaronyPad has three document layouts:

- **Source Only** (`Ctrl+1`)
- **Source + Preview** (`Ctrl+2`)
- **Preview Only** (`Ctrl+3`)

The Source editor is the authoritative document representation. Preview renders the current Markdown through Qt and is always read-only.

The Source + Preview splitter uses a canonical 3:2 default. Double-clicking the divider restores that ratio and persists the reset.

When Preview owns interaction focus in Split mode, Copy and Select All target Preview while source-mutating commands remain unavailable. Returning to Source restores normal editing commands.

A newly created document never starts in Preview Only. MaqaronyPad remembers the user's most recently used editable layout—Source Only or Source + Preview—and uses that layout for new documents.

## Markdown behavior

MaqaronyPad edits ordinary Markdown directly.

Supported editing commands include:

- Bold, Italic, and Strikethrough
- Normal Paragraph and Heading 1–6
- Bullet, Numbered, and Task lists
- Quote Block
- Indent / Outdent
- Inline Code and fenced Code Block
- Insert / Edit / Remove Link
- Image Reference
- Table
- Horizontal Rule
- Date, Time, and Date and Time
- Symbol insertion
- Toggle Comment

Rendering uses Qt's built-in Markdown support. Markdown syntax unsupported by the renderer remains ordinary source text and can still be saved faithfully.

## File safety and external changes

MaqaronyPad treats file safety as part of the normal standalone document lifecycle.

Reads use stable exact-content snapshots. Saves re-check the expected file identity before bounded atomic replacement, and Save As preserves the document's encoding, BOM, and newline style where applicable.

The active document and relevant parent path are monitored for external changes without scanning unrelated folders. If the backing file changes externally, MaqaronyPad offers explicit resolution rather than silently overwriting the external change.

If an open backing file is deleted or renamed away, the live editor remains available and protected rather than discarding the user's document state.

Rename and Delete re-check filesystem identity before destructive operations. Symbolic-link opens retain path/target identity checks so an unchanged link can save safely while retargeting or replacement races are rejected.

Dirty **Duplicate File** and **Open in External Editor** workflows can use either the current live document or the last saved disk version according to the configured policy.

## Locked Mode

**Locked Mode** (`F12`) is a persistent protection state.

It prevents document mutation while preserving navigation, search, selection, copying, and read-only Preview access. The window title identifies Locked Mode while it is active.

## Appearance

Choose **System**, **Dark**, or **Light** for the application shell. App Theme choices intentionally have no keyboard shortcuts.

The editor canvas can be controlled independently with **Dark Editor**.

Both Modern and Classic use the same packaged light/dark command-icon family. Command buttons use the established 52×52 geometry with 36×36 icons.

## Useful keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+N` | New |
| `Ctrl+Alt+Shift+N` | New Window |
| `Ctrl+O` | Open… |
| `Ctrl+S` | Save |
| `Ctrl+Shift+Q` | Save and Exit |
| `Ctrl+Shift+D` | Duplicate File |
| `F2` | Rename… |
| `Ctrl+Shift+O` | Open Containing Folder |
| `Ctrl+Shift+E` | Open in External Editor |
| `F4` | Properties |
| `Ctrl+P` | Print… |
| `Ctrl+Shift+P` | Export PDF… |
| `Ctrl+F` | Find |
| `Ctrl+H` | Find and Replace |
| `F3` / `Shift+F3` | Next / Previous Find result |
| `Esc` | Close Find/Replace panel |
| `Ctrl+G` | Go To Line… |
| `Ctrl+B` | Bold |
| `Ctrl+I` | Italic |
| `Ctrl+/` | Toggle Comment |
| `Ctrl+D` | Duplicate Line / Selection |
| `Ctrl+Shift+K` | Delete Line |
| `Ctrl+Shift+V` | Paste as Plain Text |
| `Ctrl+1` | Source Only |
| `Ctrl+2` | Source + Preview |
| `Ctrl+3` | Preview Only |
| `Ctrl+Alt+Shift+T` | Toggle Modern / Classic toolbar |
| `Ctrl+Alt+Shift+W` | Word Wrap |
| `Ctrl+Alt+Shift+L` | Line Numbers |
| `Ctrl+Alt+Shift+S` | Show / Hide Status |
| `Ctrl+Alt+Shift+E` | Dark Editor |
| `F11` | Full Screen |
| `F12` | Locked Mode |
| `F1` | Documentation |
| `Shift+F1` | Quick Tour… |
| `Ctrl+Shift+/` | Keyboard Shortcuts |

The complete live shortcut inventory is available from **Help → Keyboard Shortcuts**.

## Running from source

MaqaronyPad requires Python 3 and PyQt6 within the supported PyQt6 6.x series.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r maqarony_pad/requirements.txt
python main.py
```

Other useful launch forms:

```bash
python main.py --version
python main.py document.md
python main.py --theme dark
```

## Building the AppImage

The Fedora AppImage builder is included in the source tree:

```bash
./maqarony_pad/packaging/fedora/build-appimage.sh
```

It is intentionally non-privileged: it does not install host packages or invoke privilege-elevation helpers. Missing host prerequisites are reported instead.

Expected outputs include:

```text
maqarony_pad/dist/MaqaronyPad-1.0.0-x2.0-x86_64.AppImage
maqarony_pad/dist/MaqaronyPad-1.0.0-x2.0-x86_64.AppImage.sha256
maqarony_pad/dist/MaqaronyPad-1.0.0-x2.0-x86_64.build-info.txt
maqarony_pad/dist/MaqaronyPad-1.0.0-x2.0-x86_64.build-python-lock.txt
```

A finished AppImage can additionally be exercised with:

```bash
./maqarony_pad/packaging/fedora/test-appimage.sh
```

## Validation

Run the authoritative dependency-light source-release gate with:

```bash
bash maqarony_pad/qa/static-qa.sh
```

The release checks cover application identity, Markdown behavior, editor/UI contracts, file safety, settings persistence, packaged assets, packaging metadata, and source-manifest integrity. GUI smoke tests are additionally run by the AppImage builder when PyQt6 is available in its isolated build environment.

## Configuration

MaqaronyPad stores application configuration at:

```text
~/.config/brunonlinespace/maqaronypad/maqaronypad.json
```

The configuration is persisted through a bounded private atomic-write path. MaqaronyPad deliberately stores **no recent-file history**.

Documents remain ordinary Markdown files and are never embedded into the configuration.

## Scope

MaqaronyPad is a **standalone Markdown editor**.

It deliberately keeps Markdown source as the durable document format and does not add workspaces, document databases, or a private rich-document representation. Preview is a read-only rendering surface over the source rather than a second editable document model.

## License

MaqaronyPad is licensed under the **GNU General Public License v3.0 or later**.

See `maqarony_pad/LICENSE` for the complete license text.

## Links

- MaqaronyPad: <https://github.com/brunonlinespace/maqaronypad>
- Issues: <https://github.com/brunonlinespace/maqaronypad/issues>
- GitHub profile: <https://github.com/brunonlinespace/>

Copyright © 2026 Bruno Machado.
