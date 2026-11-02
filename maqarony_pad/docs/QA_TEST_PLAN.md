# Markopad 0.2.10 QA test plan

## 0.2.10 corrective/UI-ordering checks

- Open **Quick Tour…**, click **Open Keyboard Shortcuts…**, and verify the existing Keyboard Shortcuts dialog opens without an exception.
- Open About and verify the settings path is labelled **Configuration**, not Preferences.
- Verify Modern → File presents the More Actions buttons in File → More Actions AppMenu order: Duplicate File, Rename, Delete File, Open in External Editor, Open Containing Folder, Properties.
- Verify the File → More Actions AppMenu order itself is unchanged.
- Verify Quick Tour persistence/ellipsis behavior from 0.2.9 remains unchanged.

## 0.2.8 New File editable-layout checks

- Choose Source Only, create a new document, and verify the new document opens Source Only.
- Choose Source + Preview, create a new document, and verify the new document opens Source + Preview.
- Choose Source Only or Source + Preview, then switch to Preview Only and create a new document; verify Preview Only does not replace the remembered editable choice.
- Restart and repeat to verify the remembered editable layout persists.
- Open an existing file while the ordinary view preference is Preview Only and verify ordinary Open remains allowed to use Preview Only.
- Verify all 0.2.7 Editor Toolbar/UI behavior remains unchanged.


## 0.2.7 Editor Toolbar correction checks

- `Ctrl+Alt+Shift+T` is an independent shortcut-only command that flips Modern↔Classic in either direction.
- There is no dedicated binary toolbar-toggle button.
- Editor Toolbar submenu label is **Modern (default)** / **Classic** / **Customise Classic Bar…**; internal toolbar mode remains `tabbed` / `classic`.
- Editor Toolbar uses `toolbar-classic`; its submenu entries remain text-only.
- Editor Layout uses `toolbar-tabbed`; Source Only / Source + Preview / Preview Only retain their existing icons.
- App Theme commands remain without keyboard shortcuts.
- The 0.2.4 active-surface routing, splitter reset and Find/Replace exclusion remain intact.

## 0.2.4 Item 32 Split/Preview interaction checks

- Copy follows the last active Source/Preview text surface in Source Only, Preview Only and Source + Preview.
- Select All follows the same active text surface.
- Preview focus in Split disables Cut, Paste, Paste as Plain Text, Delete, Undo/Redo, formatting, line operations and insertion commands that mutate Source.
- Returning focus to Source restores those commands according to Locked Mode/history state.
- Opening AppMenu/toolbar controls does not lose the remembered Source/Preview interaction surface.
- Double-clicking the Source/Preview divider restores the canonical 3:2 split and persists the reset.
- Find/Replace method implementations remain exactly unchanged from 0.2.3.
- Source editor, Preview renderer and document-I/O engines remain unchanged from 0.2.3.

## 0.2.2 Classic-toolbar alignment checks

- Classic catalogue groups are exactly File / Edit / Markdown / Insert / View / Settings / Help in AppMenu order.
- Normal submenu inventory is flattened; only the Duplicate and Open Externally dirty-document policies remain flyouts.
- Editor Toolbar is one flyout in both Modern View and Classic, using `toolbar-classic`; its submenu entries are text-only.
- App Drag-and-Drop is one compact Active Window↔New Window toggle in Classic.
- Light/Dark/System and Source/Split/Preview remain separate multi-choice actions.
- Exit is available as a Classic option.
- Default Classic selection includes Image Reference, Source Only, Source + Preview, Preview Only, and the single Editor Toolbar flyout.
- Existing old Classic drag/drop selections migrate to the single toggle.
- Saving zero selected Classic items remains valid.
- AppMenu method source remains unchanged from 0.2.1.
- Item 30 Paste actions/implementation remain unchanged.
- Protected editor/file/settings/Delete/Save As/status/Properties methods and modules retain 0.2.1 hashes.

## 0.1.9 icon-family convergence checks

- Light and dark command-icon directories each contain exactly the canonical 121 Marko Plus 0.4.4 PNG assets and match the retained authority hashes.
- Every mapped Markopad QAction resolves to an existing light and dark canonical asset.
- Current semantic mappings include Paste → `paste` and Paste as Plain Text → `paste-plain`; the canonical `paste-markdown` asset remains packaged but deliberately unwired. Quote Block → `quote-block`, Inline Code → `inline-code`, Code Block → `code-block`, Edit/Remove Link → their dedicated assets, and Heading → `heading-group` remain unchanged.
- App Theme System/Dark/Light actions use the canonical `system-theme`, `dark-mode` and `light-theme` assets.
- Tabbed and Classic inventory/build methods remain byte-for-byte/source-hash equivalent to 0.1.8.
- 0.1.7 shortcut/fuzzy search and 0.1.8 theme/default contracts remain intact.

## 0.1.8 theme/default parity checks

- Fresh/no-key application theme defaults to Light.
- Fresh/no-key editor canvas independently defaults to Light, even when application chrome is explicitly Dark/System for the current invocation.
- Light application palette matches current Marko Plus exactly for Window, Base, AlternateBase, tooltip, button, highlight, placeholder and link roles.
- Dark application palette remains unchanged from 0.1.7/current Plus.
- Existing explicit stored `theme` and `editor_canvas_light` values remain authoritative and are not migrated away.
- 0.1.7 shortcuts/fuzzy search, toolbar layouts, icon assets, editor/file modules, Delete preservation and preference persistence remain unchanged.


## 0.1.7 shortcut parity / fuzzy inventory checks

- New Window is Ctrl+Alt+Shift+N; Line Numbers is Ctrl+Alt+Shift+L; Dark Editor is Ctrl+Alt+Shift+E.
- Source Font is Ctrl+Shift+[ and Preview Font is Ctrl+Shift+].
- Save As and Task List have no registered shortcut, matching current Marko Plus for the same commands.
- Standalone Open, Tabbed/Classic switching and command-tab cycling retain their explicit Markopad-only shortcuts.
- Keyboard Shortcuts groups by File / Edit / Markdown / Insert / View / Settings / Help and derives rendered bindings from the live QActions.
- Fuzzy search matches aliases and reordered modifiers: e.g. `control shift n`, `shift+ctrl+n`, and `ctl n` can match a Ctrl+Alt+Shift+N binding.
- No duplicate explicit string shortcut is introduced.


## Toolbar/UI

- View → Editor Toolbar contains **Tabbed (default)**, **Classic**, separator, and **Customise Classic Bar…**; the same submenu action is exposed as a flyout on Tabbed and Classic.
- No “Interface”, “Ribbon”, “Retro”, or Button Labels control appears in current user-facing UI.
- Tabbed is one horizontal row per tab with simple vertical group separators. Resize narrow and confirm commands move behind the native right-side overflow control rather than producing an internal horizontal scrollbar.
- Tabbed tabs double-click to collapse and single-click while collapsed to reveal; state persists.
- Classic customisation persists selected controls and still offers individual Normal Paragraph / Heading 1–6 actions.
- Every toolbar command button is exactly 52×52 with a 36×36 icon and bordered button decoration.
- Both toolbars are icon-only.
- Light icon scheme is predominantly neutral dark with restrained teal accents; dark icon scheme is predominantly neutral light with restrained teal accents.
- Heading in Tabbed opens Normal Paragraph + Heading 1–6 dropdown; Code opens Inline Code + Code Block.
- Ctrl+1/Ctrl+2/Ctrl+3 select Source Only / Source + Preview / Preview Only; F5 inserts Date and Time.
- Ctrl+F opens/focuses Find and toggles the panel closed when Find already has focus; Ctrl+H does the same for Replace; Esc closes either state.
- F3 / Shift+F3 move Next / Previous with wraparound; the counter reports X/Y and all matches remain gold while the active hit is the real editor selection.
- Dark Editor is checked when the shared Source/Preview canvas is dark and unchecked when light.
- Source Font and Preview Font remain independent; Source Font weight/italic survives theme/zoom changes and Preview Font can optionally italicize block quotations.

## 0.0.2-r8.2 focused shortcut/menu checks

- Export PDF... is Ctrl+Shift+P.
- Indent is Ctrl+] and Outdent is Ctrl+[.
- File menu places Exit before Save and Exit.
- No other behavior changes.

## 0.0.2-r8.1 focused shortcut/Tabbed-toolbar checks

- Ctrl+Tab / Ctrl+Shift+Tab move to the next/previous Tabbed toolbar page while Tabbed is active.
- Tabbed Home order is Find → Go To Line... → Find and Replace.
- Horizontal Rule is Ctrl+Shift+H.
- App Drag-and-Drop choices have no Ctrl+Alt+1 / Ctrl+Alt+2 shortcuts.
- No other behavior changes.

## 0.0.2-r8 keybinding/menu regression checks

- Reviewed shortcuts from `keys_for_marko.md` are assigned exactly, including F2 Rename, F12 Locked Mode, Ctrl+1/2/3 layouts, Ctrl+Shift+0–6 paragraph/headings, Ctrl+L / Ctrl+Shift+L / Ctrl+T lists, and Shift+F1 Quick Start.
- GitHub Repository, Raise an Issue and About Markopad have no keybinding.
- Quote Block and Code Block retain the menu-only hints `>` and ```; Indent is now a registered Ctrl+] shortcut (and Outdent Ctrl+[) as of r8.2.
- Toolbar hover tooltips include the command's native rendered keybinding when one is assigned.
- Right-clicking Tabbed or Classic, including command buttons, offers Tabbed (default), Classic and Customise Classic Bar….
- Edit ends with Find → Go To Line... → Find and Replace.
- View follows the reviewed order and names: Full Screen, Show Status; Word Wrap, Line Numbers, Dark Editor; Locked Mode, Editor Layout, Editor Toolbar; Editor Zoom, Editor Miscellaneous. App Theme and App Drag-and-Drop are in Settings.

## Privacy and persistence

- There is no Open Recent action or recent-file list.
- Existing `recent_files`, `button_labels`, old `interface`, `retro_toolbar_items`, and `ribbon_collapsed` preferences are purged/migrated.
- Toolbar mode, layout, theme, editor canvas, splitter, drop behaviour, Classic selection and Tabbed collapse state persist.

## Markdown/fidelity

- Open/save without edits preserves representative UTF-8, BOM/no-BOM, CRLF/LF and final-newline cases.
- Save writes source text directly through the atomic-save path.
- Preview remains read-only and never writes to source.
- Remote/data preview resources remain blocked from implicit loading.
- 5M paste, 25M document and 10,000-match search bounds remain.

## Packaging

- `--version` returns exactly `Markopad 0.2.10`.
- Fedora AppImage builder remains non-privileged and runs system/dark/light GUI smoke probes on both AppDir/PyInstaller payload and extracted final AppImage.
- Windows portable builder probes exactly `Markopad 0.2.10`.

## 0.0.2-r1 focused regression checks

- Home is the selected default Tabbed page on a new window.
- About shows the slogan **Simple. Fast. Focused.**
- Historical 0.0.2-r1 executable-routing behavior remains removed; in 0.1.3 the file still delegates to the desktop/OS association, while dirty-state handling follows the new Save Changes and Open / Open Last Saved Version / Cancel lifecycle workflow.
- Customise Classic Bar… remains available regardless of whether Tabbed or Classic is active.

## 0.0.2-r7 Keyboard Shortcuts regression checks

- Help → Keyboard Shortcuts opens a retained modeless `Keyboard Shortcuts — Markopad` dialog; invoking it again raises the same instance.
- Dialog presentation mirrors Ricopad 0.7.2 r5.1: a 700×560 two-column `Command | Shortcut` table with visible headers, hidden row numbers, read-only cells and whole-row selection.
- Only commands with an assigned keybinding are listed; unbound commands are omitted rather than shown with placeholder dashes.
- Category dropdown starts at **All** and offers exactly File / Home / Insert / View / Help after All.
- Selecting a category shows only keybindings associated with that Markopad Tabbed toolbar tab.
- Typing in Search filters live by command name or rendered keybinding; clearing Search restores the selected category.
- Search + category filters compose correctly and a no-results message appears when nothing matches.
- The bottom action is the standard **OK** button used by the Ricopad dialog.

## 0.1.3 lifecycle regression checks

- Clean external content change shows the banner and does not silently reload.
- Dirty external content change preserves both versions until the user chooses Reload, Save Version As, Overwrite or Cancel.
- External deletion/rename-away produces missing state; Reload is unavailable; the live editor survives.
- Closing a clean-but-missing document requires an explicit preservation/close decision.
- Save/Overwrite refuses a second race after the user made the conflict decision.
- Save Version As rebinds preview/watcher to the new live path and leaves the changed original untouched.
- Rename refuses collisions and a source that changes before rename.
- Delete refuses a file that changes after confirmation and retains the editor after successful deletion.
- Dirty Duplicate Current includes unsaved edits; Duplicate Last Saved uses disk bytes.
- Dirty External Editor supports Save Changes and Open / Open Last Saved Version / Cancel.
- Ordinary Save As remains UTF-8/no-BOM; 64 MiB policy, shortcut policy and status layout remain unchanged.

## 0.1.3 family-alignment checks

- Open UTF-8/16/32 BOM Markdown and confirm exact encoding/BOM/newline preservation through Save As.
- Open an unmarked non-UTF-8 file and confirm Markopad asks for the source encoding rather than guessing.
- Confirm files/saves above 25 MiB are refused.
- Confirm unsupported explicit Save As suffixes are rejected and suffixless targets default to `.md`.
- Confirm F12 Locked Mode persists, blocks mutation, confirms unlock and adds the title suffix.
- Confirm F4 Properties uses grouped File / Document fields and lives under File → More Actions.
- Confirm the approved View, Markdown, Insert and Settings menu order.
- On Linux/Plasma, confirm the window associates with `markopad.desktop` rather than Python.

## 0.1.4 Undo/Redo availability checks

- Fresh/clean document with no undo history: Undo and Redo are disabled.
- After an edit: Undo becomes enabled when the document reports undo availability.
- After Undo: Redo follows the document redo availability.
- Locked Mode disables both regardless of stack history; unlocking restores the real stack-dependent state.
- Preview Only disables both regardless of stack history; Source Only / Source + Preview restore the real stack-dependent state.
- `source_editor.py`, `preview.py`, `document_io.py` and `legacy_ricopad.py` remain byte-for-byte identical to 0.1.3.
- Delete File still retains the live editor after successful on-disk deletion.
- The existing Undo/Redo QActions remain the sole Markopad command actions for these operations.

## 0.1.6 path/target-identity checks

- Normal regular-file atomic Save remains functional and does not report a symlink state.
- Opening/reading a symlink records the symlink path-entry identity and regular target identity separately.
- Save through an unchanged symlink preserves the symlink inode and updates only the regular-file target.
- Replacing/retargeting the symlink after the snapshot cancels Save without modifying either candidate target.
- Replacing the regular target behind an unchanged symlink cancels Save.
- Markopad keeps historical resolved-path Rename/Delete semantics and live-editor Delete preservation.
- 0.1.5 hardened settings persistence and 0.1.4 Undo/Redo contracts remain protected.

## 0.1.5 hardened-preferences checks

- Existing settings path, keys, defaults, migrations and Settings UI remain unchanged.
- Missing config loads as the normal empty/default state.
- Normal settings round-trip is exact.
- Malformed JSON, non-dictionary JSON, oversized config and config symlinks are rejected without preventing startup.
- Config directory/private temporary permissions are 0700/0600 on POSIX systems.
- Simulated atomic-replace failure preserves the previous config and cleans the temporary file.
- 0.1.4 Undo/Redo state behaviour remains present.
- Delete File continues to preserve the live editor after successful disk deletion.
- `source_editor.py`, `preview.py`, `document_io.py` and `legacy_ricopad.py` remain byte-for-byte identical to 0.1.4.
