## MaqaronyPad 1.0.2 — AppImage smoke-test version correction (2026-11-01)

- Correct a confirmed regression introduced during 1.0.1 issuance: the application's `APP_VERSION` became `1.0.1`, but `smoke_test()` still checked `APP_VERSION == "1.0.0"`. This caused the AppDir system-theme GUI smoke test to exit 3 after successful freezing and metadata validation.
- Make the real smoke test compare `QApplication.applicationVersion()` against the current `APP_VERSION`, instead of a hard-coded version literal; this retains a useful runtime identity check without a future stale constant.
- Add a mandatory dependency-light QA script that executes the production smoke-test function with simulated QAction transitions for all three themes and all four icon families, and proves that both a mismatched runtime version and the historical stale-literal defect fail.
- No Markdown editor functionality, icon artwork, data storage, format support, or layout changes. GitHub README current version only.

## MaqaronyPad 1.0.1 — AppStream final-release ordering correction (2026-11-01)

- Correct Fedora AppImage failure after promotion to 1.0.0: AppStream rejected final 1.0.0 followed by development editions 1.0.0-x17.10, etc. (`releases-not-in-order`).
- Limit public AppStream release entries to final 1.0.1, 1.0.0, and previously published 0.3.4, strictly newest first. Preserve every experimental source edition and description in this changelog and release notes.
- Invoke AppStream's own validator during Fedora builder source preflight where available, instead of only at AppDir assembly; strengthen the dependency-free validator and regression with old failure and bad-order mutations.
- No Markdown editor, file handling, themes, icon art, or runtime functionality changes. Protected root README differs only in current version.

## MaqaronyPad 1.0.0 — Final release (2026-11-01)

- Promote the resolved 1.0.0-x17.10 source to final 1.0.0; preserve its Markdown-only repeat-build QA fix and all earlier approved corrections.
- Synchronize current application, Suite manifest, Fedora AppImage, Windows portable version identity, README version field and version-dependent QA.
- Preserve historical release records, editor runtime behavior, themes, icon artwork and file safety.

## MaqaronyPad 1.0.0-x17.10 — Repeat-build QA scope correction (2026-11-01)

- Replace the recursive Markdown-only grep over the entire project with a scoped check over production Python source and desktop/AppStream/component metadata.
- Exclude generated build/venv, PyInstaller bundles, AppDir, dist, historical docs and QA scripts from file-format capability detection; keep actual application RTF capability detection strict.
- Add positive regression for old build artifacts and negative regressions for production Python and desktop MIME violations. No runtime/editor, icons or README changes outside current version.

## MaqaronyPad 1.0.0-x17.9 — AppStream build preflight correction (2026-11-01)

- Correct the Fedora AppImage builder failure from x17.8: the AppStream release list omitted the exact current version, causing a late `AssertionError` after PyInstaller.
- Add the missing x17.8 historical AppStream record and the x17.9 current record, preserving older history.
- Validate real Desktop Entry and AppStream metadata during builder preflight, before environment setup and freezing, and again after AppDir assembly; execute both with a mandatory QA regression, including negative metadata tests.
- No changes to editing, theme/icon command behavior, artwork or other production runtime files; GitHub README current-version field only.

## MaqaronyPad 1.0.0-x17.8 — Frozen status-message import and settings-action validation (2026-11-01)

- Fix the lazy status-message helper import for the actual PyInstaller import root.
- Make existing AppDir and final AppImage smoke tests trigger Light, Dark, System and all four icon families and verify status messages and icons.
- Add import-root regression QA; preserve all unrelated runtime and icon assets.

## MaqaronyPad 1.0.0-x17.7 — GitHub README and Halcyon dark import icon correction (2026-11-01)

- Adopt the four GitHub README texts explicitly supplied in `updated-readme-2.zip` as the new protected authorities; only designated current-version field(s) differ in the issued release.
- Correct `impport-file.png` to `import-file.png` in the dark Halcyon family without changing any image bytes. Preserve all other icon assets and application functions.
- Enforce independent protected-README checking and exact Halcyon light/dark filename parity in the source-release gate.

---

## MaqaronyPad 1.0.0-x17.6 — Correct GitHub README authority (2026-11-01)

- Restore the repository-root GitHub README byte-for-byte from the user-supplied 1.0.0-x14.4 authoritative file, changing only the designated `Current release` value to `1.0.0-x17.6`.
- Remove the unauthorized x14.5 release section inherited from the incorrect baseline. Replace the pinned README authority and checksum with the user-supplied original; keep the mandatory version-only release gate.
- Preserve the x14.5 historical account in the existing changelog and release-history documentation, not in the protected GitHub README.
- No changes to Markdown editing, icon families, toolbar commands, configuration, or file-handling operations.

---

## MaqaronyPad 1.0.0-x17.5 — Halcyon icons and protected GitHub README (2026-11-01)

- Add the fourth App Icons choice **Maqa Icons Halcyon**, with artwork from `toolbar-icons-aero`; AppMenu only (no selector icon or toolbar command). Persist choice and refresh all existing light/dark icon consumers.
- Restore the authoritative GitHub README; its **current version** field(s) are the only permissible modifications. Preserve recovered historical differences under `docs/history/` and enforce an independent immutable README gate.
- Existing icon families, commands and editor/file behavior remain unchanged.

---

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

# MaqaronyPad 1.0.0-x17.0 — Unicode source Chars (2026-10-24)

- Use Qt grapheme boundaries and per-`QTextBlock` revision caching for the Markdown-source Chars indicator. Count whitespace, markup and logical paragraph breaks.
- Keep host-level total caching so cursor-only updates are inexpensive. Do not change file-size limits or text editing.
- Preserve x14.4 warning correction and all PNG icon assets; no SVG assets existed in x14.4.
- Add x14.5 scoped QA with Unicode and cache regression coverage.

---

# MaqaronyPad 1.0.0-x14.4 — Status correction (2026-10-24)

- Tag backing-file change/missing alerts with an explicit warning identifier. Returning to the normal backing state clears only that alert, preserving unrelated persistent critical warnings.
- Preserve the previous `len(editor.toPlainText())` character-count semantics (including Unicode) with cache invalidation on `textChanged`; cursor-only status refresh no longer extracts the whole text.
- Retain the existing status-bar labels/layout, four-second message conventions, wording, status information, format handling and all file operations.
- Add focused Qt-free QA for warning ownership, clearing, Unicode counts and the scoped production diff. Previous historical release QA remains version-specific and unchanged.

---

# MaqaronyPad 1.0.0-x14.3 — Message conventions (2026-10-24)

- Standardized status messages to four seconds, with unresolved critical warnings persistent until resolution or acknowledgement.
- Save, Save As and Save Version As include the filename; duplicate, delete and rename follow the approved action wording.
- Complete-sentence punctuation and suppression of duplicate completion messages; no changes to editor logic or status-bar layout.

---

# MaqaronyPad 1.0.0-x14.2 — Status-message coverage convergence (2026-10-24)

- Ten agreed status-feedback additions, using MaqaronyDesk x18.3 or RiqatonyPad x13.1 as the authority: successful Open, Save As, Save Version As, PDF export, missing local link, Dark Editor canvas switch, application theme switch, external editor launch, containing-folder launch, and external backing-file transition.
- Status messages appear in the existing left editor message field. Existing notification text, status indicator fields, layout and editor/file operations remain unchanged. PDF success requires a fresh nonempty PDF output; watcher alerts occur only on changes of backing state.
- No wording-convergence changes, new dialogs, new actions, workspace features or layout changes. Static x14.2 delivery/preservation regression added; live Fedora Qt GUI validation remains pending.

# MaqaronyPad 1.0.0-x14.1 — Editor status-bar correction (2026-10-23)

- Use exactly two visible editor status labels: independent messages at left; a permanent, right-aligned consolidated indicator at right.
- Editing · document line/column/total characters · encoding/newline · viewing/zoom. Only middle dots between groups; existing thousands separators remain.
- Preserve all Pad styling, status-message timeouts, numerical calculations, file/editor behavior and geometry settings. No workspace changes.

# MaqaronyPad 1.0.0-x14.0 — Editor status-bar convergence (2026-10-23)

- Arrange editor status into the five approved functional fields, with independent messages and no status-bar word count.
- Preserve numerical formatting, native Pad styling, geometry safeguards, and all non-status-bar behavior.

# MaqaronyPad 1.0.0-x13.0 — Permission preservation (2026-10-23)

- Match MaqaronyDesk x16.2: after the exclusive-open fallback creates its destination, call `os.fchmod(descriptor, source_mode)` when available to restore the staged file permissions even under restrictive umasks.
- Preserve no-clobber handling, temporary-file lifecycle, data transfer, fsync, and all other editor behavior.
- Update only current release identity, app metadata, source manifest, and scope-specific QA.

# MaqaronyPad 1.0.0-x12.6 — End-of-document scrolling (2026-10-22)

- Disable automatic cursor-centred overscrolling in the Markdown source editor using `setCenterOnScroll(False)`, following Sheepy Pad 0.4.1.
- Preserve Go To Line, ordinary cursor visibility, word wrapping, line-number gutter and preview behavior. No other production behavior changed.
- Update version identity, AppStream, source manifest and static QA. Live Qt behavior requires Fedora KDE confirmation.

# MaqaronyPad 1.0.0-x12.5

Behaviour-preserving presentation extraction: relocate existing About, Quick Tour and Keyboard Shortcuts application methods into `widgets/about_dialog.py`, `widgets/quick_tour.py` and `widgets/keyboard_shortcuts.py`; consolidate the existing shortcut-search helper without changing its implementations. No dialog classes or unrelated changes.

# MaqaronyPad 1.0.0-x12.4 — Keyboard-shortcut helper convergence (2026-10-18)

- Relocated existing keyboard-shortcut query helpers to `widgets/shortcut_search.py`, preserving original implementations and user behaviour.
- Moved the original private helper functions from `app.py`, retained their names and behaviour, and updated their import paths.
- Kept document Find/Replace and editing code unchanged; updated version metadata, manifests and QA.
- No public README content edits beyond current-version references.

---

# MaqaronyPad 1.0.0-x12.3 — Widget-tree reorganisation (2026-10-18)

- Converged standalone Pad widget organisation under `widgets/` and `widgets/mwpyn/`.
- Kept original editing algorithms and class method definitions unchanged; updated imports, resource lookup, build references and source regression checks.
- No new features, dialogs, application constants, services or compatibility shims.

---

# MaqaronyPad 1.0.0-x12.2 — Python shebang consistency (2026-10-18)

- Added the standard Python 3 shebang to five existing import-only Python modules; their previous contents and all methods remain unchanged.
- Preserved executable permissions and source paths; no widget-directory relocation or editor behavior changes.
- Updated release metadata, QA and source integrity manifest. Public README changed only for the current version.

---

# MaqaronyPad 1.0.0-x12.1 — Packaging layout and source-provenance cleanup

- Removed redundant `OFFICIAL_SOURCE.md`; source integrity continues through `SOURCE_MANIFEST.sha256` and release QA.
- Moved unchanged Windows packaging assets from `windows/` to `packaging/windows/` and updated the builder’s program-root calculation.
- Updated packaging references and release checks without altering editor methods, application behaviour, or public documentation beyond current-version references.
- Windows build requires verification on Windows; no runtime feature change.

---

# MaqaronyPad 1.0.0-x12.0 — Application module filename convergence

- Renamed the standalone application module from `maqarony_pad.py` to `app.py`, keeping its existing implementation unchanged except for the current release version.
- Updated the portable launcher, Fedora AppImage/Windows staging, source identity QA and manifest to use the single canonical `app.py` (no compatibility copy).
- Root GitHub README changed only where the current version is referenced. Historical release entries below are preserved byte-for-byte.
- The executable root `main.py` was already executable and remains unchanged.

---

# MaqaronyPad 1.0.0-x11.0 — Documentation and metadata correction

- Correct the current in-app documentation release label and add a current architecture guide, without modifying the historical Markopad 0.2.10 architecture record.
- Add a separate historical-attribution correction notice for the original Markopad 0.2.10 README sentence; retain that archived sentence verbatim.
- Prepend an accurate AppStream release entry; clarify that x10 extracted 29 file-lifecycle methods. Previous AppStream release elements remain untouched.
- Document the existing `.maqarony_pad-` temporary-file prefix as an intentional preserved implementation detail. No document I/O or editor algorithm changes.
- Protect preceding release notes, changelog sections and source fingerprint fixtures without changing their original bytes.
- No new functions, feature changes, editor restructuring or packaging-mechanics changes. Live GUI and Fedora AppImage build remain unverified here.

---

# MaqaronyPad 1.0.0-x10.0 — Document I/O and file-lifecycle extraction

- Derived directly from `1.0.0-x9.0`. Moved 29 existing main-window file-lifecycle methods verbatim to `editor_lifecycle.py` using `EditorLifecycleMixin`.
- Original `document_io.py`, document watcher responsibilities, external file preservation, Save/Save As, Rename, Duplicate and Delete semantics remain unchanged.
- Updated required packaging references, exact source-identity QA and original source-location checks. GitHub root README updated only for the release version.
- No new features, dialog migration, application-constants extraction, folder reorganisation, shared runtime, or algorithm changes.
- Live PyQt6 GUI, AppImage and Windows builds not run in this environment.

---

# MaqaronyPad 1.0.0-x9.0 — Platform, resources and startup support extraction

- Derived strictly from the corrected 1.0.0-x8.1 baseline; MepyNamu remains unchanged.
- Relocated eight existing top-level platform/resource/startup function definitions verbatim to `editor_platform_startup.py`; retained original public names and the executable entry point in `maqarony_pad.py`.
- Kept the program directory semantics by placing the new module beside the original; bound original application constants and window references only after their definitions to avoid startup import errors.
- Updated packaging inventories and source QA without changing application behavior, dialogs, file-safety or editor methods.
- Repository-root GitHub README changed exclusively in its current version reference; all previous release history retained.
- PyQt6 live runtime and actual AppImage/Windows build tests remain unverified here.

---

# MaqaronyPad 1.0.0-x8.1 — Corrective startup and Date/Time import fix

- Derived exclusively from issued 1.0.0-x8.0; x8.0 source is not modified or reissued.
- Bind the extracted command/appearance module's existing globals only after its import and after `apply_theme` is defined; fixes startup `NameError`.
- Restore the `datetime` import required by the unchanged Date, Time and Date and Time command callbacks in the relocated module.
- Preserve all existing editor and command method definitions, file safety, toolbar/menus, Qt ownership and application behaviour.
- Add a dependency-light import-order and global-symbol regression gate; preserve original release history.
- GitHub root README modified exclusively for current-version references.

---

# MaqaronyPad 1.0.0-x8.0 — Commands, icons and appearance extraction

- Based directly on MaqaronyPad 1.0.0-x7.0; MepyNamu was not used as a source.
- Moved 16 existing command/menu, icon and appearance methods to `editor_commands_appearance.py` with their definitions unchanged.
- Preserved the original Tabbed/Classic presentation, command catalogue, shortcut choices, appearance preferences, file safety, source/preview logic and dialog implementations.
- Retained previous x1–x7 exact-text identity checks, added x8 method-inventory/MRO/global-binding QA, and updated AppImage staging.
- Public GitHub root README remains unchanged except its current version references; no new features or unrelated changes.

---

# MaqaronyPad 1.0.0-x7.0 — Tabbed/Classic presentation extraction

- Derived strictly from the corrected `1.0.0-x6.1` source; MepyNamu is unchanged.
- Relocated 24 existing Tabbed/Classic toolbar construction, cataloguing, customisation, sizing, collapse, and AppImage overflow methods to `editor_ribbon_retro.py` without changing their method-definition text.
- Retained the host-owned command catalogue defaults and resource/dialog helpers, binding their original references to the extracted module without altering their values or behaviour.
- Preserved the existing Tabbed and Classic command inventory, icon geometry, toolbar preferences, shortcuts, dialog implementation and UI contract.
- Added x7 method-text identity and integration checks; kept earlier x1–x6.1 extraction and safety gates.
- GitHub root README changed exclusively through `1.0.0-x6.1` → `1.0.0-x7.0` version references. No dialog-class extraction, application-constants extraction, shared runtime or editor-folder reorganisation.
- Source QA completed; live PyQt6 and packaged GUI runtime tests remain unverified.

---

# MaqaronyPad 1.0.0-x6.1 — Corrective release

- Fixed a launch-time `NameError` caused by binding the extracted preference helper before importing its module; no preference method bodies changed.
- Direct continuation of 1.0.0-x6.0, retaining all x1–x6 editor extraction work, the restored GitHub root README, and existing file-safety contracts.
- Version/packaging metadata and regression checks synchronized; no new features, dialog extraction, or unrelated changes.

---

# MaqaronyPad 1.0.0-x6.0 — Preferences and New Document Defaults stage

- Branched directly from the issued 1.0.0-x5.0 source without changes to unrelated application or editor behaviour.
- Relocated 2 existing editor preference method(s), with unchanged source text; retained each application's current configuration service and paths. No independent new-document-defaults method existed to extract in the inspected sources.
- Restored the public repository-root README directly from the original 0.3.4 source, changing only necessary current-version references. Experimental release notes remain in internal documentation only.
- Added x6 source-identity, README-integrity and packaging regression checks; prior x1–x5 identity and file-safety checks retained.
- No dialog extraction, app-constants extraction, editor-folder reorganisation, shared library or new functionality.

---

# MaqaronyPad 1.0.0-x5.0 — Printing, PDF and Document Information

- Branches directly from **1.0.0-x4.0**, maintaining its complete source and configuration lineage.
- Original printing/PDF and Properties method bodies relocated text-identically into dedicated x5 mixins, keeping MaqaronyPad's application-specific editor/workspace ownership.
- Completes the approved x4 filename convergence by removing obsolete import-only source-editor and preview module shims; canonical `editor_source.py` and `editor_preview.py` stay unchanged.
- Retains original dialog layout/text, commands, shortcuts, source-versus-preview behaviour, security and file-lifecycle semantics; no dialog migration, app-constants migration or editor-folder restructuring.
- New x5 source-fingerprint gate added to the retained full release QA. Runtime Qt and AppImage/Windows builds are not validated in this source-only environment.

---

# MaqaronyPad 1.0.0-x4.0 — Search and view extraction with editor filename convergence

- Derived exclusively from 1.0.0-x3.0 (corrected 0.3.4 source lineage).
- Relocated original unchanged source-editor search/decorations/view methods into `editor_search_view.py`.
- Relocated original unchanged MaqaronyPad window Find/Replace/view methods into `window_search_view.py`.
- Canonical modules are `editor_source.py` and `editor_preview.py`; old names remain as thin import compatibility shims.
- No dialog migration, constants extraction, editor-folder migration, runtime shared foundation, or new features.
- Original method bodies and preview source bytes verified against x3.0.

---

# MaqaronyPad 1.0.0-x3.0 — insertion and clipboard extraction

- Relocated 16 unchanged Markdown editor methods into `editor_insertion.py`; no behavioural changes.
- x1–x3 method identity and all available source safety gates retained.

---

# MaqaronyPad 1.0.0-x2.0 — editor-widget extraction from 0.3.4

- Corrective branch from the previously omitted **MaqaronyPad 0.3.4** baseline. This supersedes `1.0.0-x1.0` as the source master for later MaqaronyPad extraction stages; MepyNamu `1.0.0-x1.0` is unchanged.
- Relocated the unmodified `HighlightRule`, `MarkdownHighlighter`, `LineNumberArea`, `_scheme` and `MARKDOWN_COLOR_SCHEMES` definitions from `source_editor.py` to `editor_widgets.py`.
- Preserved the 0.3.4 `MarkopadSourceEditor` class and `MarkdownPreview` in their original modules. The earlier `mwpyn/` namespace is **not** restored.
- Kept source-editor import compatibility, Markdown source authority, existing UI/menus, preview, preferences and file lifecycle unchanged.
- Extended Fedora AppImage input validation, version identifiers, and source-integrity/release QA for the extracted helper module. Retained all older release-specific QA scripts and release notes intact.
- No dialog migration, `app_constants.py` creation or editor-folder reorganisation.

## 0.3.4 — Original module layout restored

- Returned the editor and preview to the original `source_editor.py` and `preview.py` modules with their original classes.
- Removed the experimental `mwpyn` namespace without changing Markdown editing/rendering logic.
- Kept the MaqaronyPad identity, current KDE and AppImage fixes, application/command icons and historical release records intact.

## 0.2.10 — Quick Tour corrective and More Actions ordering

- Fixed Quick Tour's Keyboard Shortcuts button to use Markopad's existing shortcuts dialog callback.
- Changed About-dialog **Preferences** to **Configuration**.
- Reordered Modern File-toolbar More Actions buttons to match File → More Actions AppMenu exactly.
- No unrelated behavior changes.

## 0.2.9 — Quick Tour convergence

- Replaced Quick Start with a Ricopad-style seven-page **Quick Tour…** wizard adapted for Markopad.
- Added persistent **Don't show Quick Tour on startup again** footer behavior and first-run startup presentation.
- Added ellipsis to both the Help/AppMenu entry and toolbar tooltip.
- No unrelated behavior changes.

## 0.2.8

- Added a persisted last-editable document layout (`source` or `split`).
- New Document now opens in that remembered editable layout rather than Preview Only.
- Preview Only remains valid for ordinary viewing and does not overwrite the remembered editable choice.
- Existing document-open behavior and all unrelated UI/editor/file behavior remain unchanged.

## 0.2.7

- Restored `Ctrl+Alt+Shift+T` as an independent shortcut-only Modern↔Classic toolbar switch; the removed binary toolbar button remains removed.
- Renamed the user-facing Editor Toolbar submenu entry **Tabbed (default)** to **Modern (default)** without changing the internal `tabbed` mode/state.
- Rewired **Editor Toolbar** to `toolbar-classic`.
- Rewired **Editor Layout** to `toolbar-tabbed`; its child-command icons remain unchanged.
- Preserved shortcut-free App Theme commands, the 0.2.6 flyout/customisation structure, Item 32 routing and all editor/Preview/file-lifecycle behavior.
- No icon asset changes and no audit-item work.

## 0.2.6

- Replaced the synthetic Tabbed↔Classic **Editor Toolbar** toggle with the existing **Editor Toolbar** submenu action as a flyout on both Tabbed and Classic toolbars.
- The Editor Toolbar flyout uses `toolbar-tabbed`; its Tabbed, Classic and Customise Classic Bar… submenu entries are text-only.
- Removed the standalone **Customise Classic Bar…** toolbar button; it remains available inside Editor Toolbar and from the toolbar context menu.
- **Editor Layout** now uses `toolbar-classic`; Source Only / Source + Preview / Preview Only retain their existing icons.
- Removed Light/Dark/System App Theme keyboard shortcuts without changing the theme commands themselves.
- No audit-item, editor/Preview engine, file-lifecycle, status-bar, Find/Replace, formatting-semantic or icon-asset changes.

## 0.2.5

- UI backlog release: added the approved Toggle Comment light/dark icon pair and wired a Home toolbar button plus Classic customization entry.
- AppMenu Heading now uses the same `heading-group` icon as the Tabbed flyout.
- Added direct Light/Dark/System theme shortcuts on `Ctrl+Alt+Shift+1/2/3`.
- Rebound Tabbed↔Classic switching to one `Ctrl+Alt+Shift+T` **Editor Toolbar** toggle and renamed the compact control accordingly.
- Preserved 0.2.4 Split/Preview routing and all audit-item behavior.

## 0.2.4

- Audit Item 32: made Copy and Select All follow the active Source/Preview text surface.
- Prevented source-only mutations from operating on Source while Preview owns the interaction focus in Split mode.
- Added double-click reset of the Source/Preview splitter to the canonical persisted 3:2 position.
- Find/Replace remains deliberately untouched for later cross-family work.
- No Item 31/33, status-bar, Paste, file-lifecycle, theme/icon or toolbar-inventory changes.

## 0.2.3

- Audit Item 30: corrected the misleading Paste command semantics in coordination with Marko Plus 0.4.7.
- Ordinary Paste (`Ctrl+V`) now owns the smart HTML/rich-to-Markdown conversion path.
- Paste as Plain Text (`Ctrl+Shift+V`) now owns the literal guarded-text path.
- Remapped the second command to `paste-plain`; retained `paste-markdown` as a packaged but unwired canonical asset.
- Preserved existing Classic-toolbar customisation semantics via legacy item IDs.
- No editor-engine, file/document lifecycle, theme, shortcut, toolbar inventory, status or Properties changes.

## 0.2.2

- Audit Item 29: rebuilt Classic customization inventory in AppMenu order and flattened normal submenu commands.
- Added compact binary Toolbar Style and App Drag-and-Drop toggles; Toolbar Style is used in both Tabbed and Classic.
- Kept only the two dirty-document policy controls as flyouts.
- Revised Classic default to include Image Reference, all three editor layouts, Toolbar Style and Customise Classic Bar; Exit remains available and Classic may still be empty.
- Migrated old Classic drag/drop radio selections to the new single toggle without changing the stored App Drag-and-Drop preference.
- Item 30 Paste behavior remains unchanged.

## 0.2.1

- Corrected the Tabbed Settings presentation to the approved flat model.
- App Theme is now direct **Light / Dark / System** controls; App Drag-and-Drop is direct **Active Window / New Window** controls.
- Kept only the final Duplicate/Open Externally dirty-document policies as flyouts.
- Added exact setting-provenance tooltips for the direct controls.
- Recorded Audit Item 30 for a later Paste-command convergence investigation; Paste behavior is unchanged.
- Classic inventory remains deferred to 0.2.2.

# Markopad changelog

## 0.2.0

- Audit Item 28: converged Markopad's Tabbed Home, Insert and View command inventory/order to current Marko Plus wherever the commands are shared.
- Added a Settings tab reusing the live AppMenu submenu actions for App Theme, App Drag-and-Drop, dirty Duplicate and dirty Open Externally policies.
- Added the missing Select All, Duplicate Line / Selection, Delete Line, Full Screen and Tab Width Tabbed controls; grouped Inline Code + Code Block under Code and added Normal Paragraph to Heading.
- Classic toolbar inventory/build/customization remains byte-for-byte method-stable for the separate Item 29 phase.
- No command behavior, shortcut, theme, icon-asset, editor/file lifecycle, status or Properties changes.

## 0.1.10

- Audit Item 17: AppMenu now explicitly uses the native/global-menu contract and stays available in both Tabbed and Classic modes.
- Audit Item 27B: Keyboard Shortcuts now derives menu-backed shortcut membership recursively from the live AppMenu tree, with only genuine menu-less shortcuts listed explicitly.
- Preserved 0.1.7 shortcut assignments/fuzzy matching, 0.1.8 theme defaults, 0.1.9 icon family, toolbar inventories, editor/file behavior and standalone lifecycle.

## 0.1.9

- Audit Item 21 only: adopted Marko Plus 0.4.4 as the authoritative Marko command-icon family.
- Imported the complete 121-icon light/dark family and remapped shared command semantics to canonical Plus assets rather than merely replacing same-named PNGs.
- Added canonical mappings for Paste as Markdown, Quote Block, Inline Code, Code Block, Edit/Remove Link, Heading group and App Theme choices.
- No command behavior/availability, toolbar/menu layout, shortcut, theme/default, editor/file lifecycle, Settings layout, status or Properties changes.

## 0.1.8

- Audit Item 20 only: fresh/default application theme is Light and a missing editor-canvas preference independently defaults to Light, matching current Marko Plus.
- Replaced the older near-white Markopad Light application palette with the exact current Marko Plus neutral Light palette.
- Existing explicit user theme/editor-canvas preferences continue to win; no preference migration rewrites them.
- No editor, file lifecycle, Delete, preference-I/O, menu-layout, toolbar-layout, shortcut, icon, Settings-layout, status or Properties changes.

## 0.1.7

- Audit Item 19: aligned common Markopad shortcuts to current Marko Plus, including New Window, Line Numbers, Dark Editor and Source/Preview Font; removed Save As and Task List shortcuts because current Plus intentionally leaves those same commands unassigned.
- Audit Item 27: ported Plus-style fuzzy Keyboard Shortcuts matching and changed the live inventory filter from toolbar tabs to application menus.
- Preserved explicit standalone-only shortcuts for Open, Tabbed/Classic switching and command-tab cycling.
- No editor, file lifecycle, Delete, preference, menu-layout, toolbar-layout, theme, icon, status or Properties changes.

## 0.1.6

- Audit Item 23 only: document snapshots now distinguish the opened path entry from its regular-file target for symbolic-link safety.
- Save through an unchanged symlink preserves the symlink and atomically updates the verified target; symlink retargeting or target replacement is refused.
- Retains the historical resolved-path semantics for ordinary UI, Rename and Delete, including Item 6 live-editor preservation after Delete.
- No source-editor, preview, QAction, preference, menu, shortcut, theme, icon, status or Properties changes.

## 0.1.5

- Audit Item 22 only: hardened the existing Markopad preferences JSON persistence without changing any setting key, default, UI or preference semantics.
- Preferences reads are now bounded to 1 MiB and accept only a stable regular non-symlink file; malformed, oversized or unsafe input falls back to normal defaults.
- Preferences writes now use a private configuration directory, same-directory 0600 temporary file, flush/fsync, atomic replacement, directory fsync and cleanup on failure.
- Retains 0.1.4 Undo/Redo state behaviour and the protected source-editor, preview, document-I/O, Delete-preservation, action-ownership, menu, shortcut, theme and icon contracts.

## 0.1.4

- Audit Item 14 only: Undo and Redo now follow the live QTextDocument undo/redo availability instead of being enabled merely because editing is allowed.
- Locked Mode and Preview Only remain hard disable conditions for Undo/Redo.
- No source-editor, preview, document-I/O, Delete-preservation, action-ownership, menu, shortcut, theme or icon changes.

## 0.1.3

- Completed Marko-family Audit Item 3 by adopting the Plus 25 MiB, encoding/BOM-preserving Save As, explicit legacy-encoding selection, UTF-32 BOM and strict-extension policies.
- Harmonised View Only to persistent Locked Mode and Properties to the Marko Plus grouped dialog with F4.
- Reorganised File/Markdown/Insert/View/Settings menus to the approved family layout and exposed the two remembered dirty-file policies under Settings.
- Added explicit Qt desktop-file identity so Linux window lists associate Markopad with its desktop entry instead of Python.
- Kept Audit Item 8 shortcuts and the existing status architecture unchanged.

## 0.1.2

- Phase 2B Marko-family lifecycle hardening, closing audit Item 6.
- Added targeted active-file/parent monitoring with normal/changed/missing backing states and non-destructive external-change banner.
- Added protected Reload / Save Version As / explicit Overwrite conflict handling and clean-but-missing close protection.
- Hardened Save, Rename and Delete against filesystem replacement/race conditions; Delete now retains the live editor as the only guaranteed copy.
- Added dirty Duplicate Current vs Last Saved and dirty External Editor Save/Open vs Last Saved workflows.
- Preserved Markopad's 64 MiB/file-fidelity, shortcut and status policies; no Plus workspace/tabs/dashboard scaffolding was imported.


## 0.1.1

- Phase 2A Marko-family editor-parity backport from Marko Plus 0.4.2, closing audit Items 2, 9 and 10.
- Hardened the existing bottom Find/Replace panel with bounded query/results, X/Y position, F3/Shift+F3, focus-aware Ctrl+F/Ctrl+H toggle-close, size-safe Replace and one-block Replace All.
- Replaced the primitive Symbols dropdown with the shared 40-symbol grid plus More Symbols.
- Preserved Source Font weight/italic, adopted blue Preview links, added optional italic block quotations and protected dirty state across presentation-only changes.
- Added Toggle Comment (Ctrl+/), Insert/Overwrite mode and horizontal-scrollbar-aware gutter geometry.
- No Plus workspace/lifecycle/status architecture was imported.


## 0.1.0-r2

- AppImage packaging-only hotfix; application behaviour is unchanged from 0.1.0-r1.
- Corrected final Qt payload validation: Qt PrintSupport remains required and unexpected Qt WebEngine remains fatal, while incidental QtPdf shared libraries no longer fail the build.
- Retained the pre-existing PyInstaller exclusions for unused QtPdf/QtWebEngine Python modules.


## 0.1.0-r1

- AppStream metadata-only hotfix; application behaviour is unchanged from 0.1.0.
- Added homepage and bug-tracker URLs.
- Added structured developer metadata and OARS 1.1 content rating.

## 0.1.0

- Promoted the 0.0.2-r8.2 behavioral baseline to application version 0.1.0.
- Standardized the Suite Pythoine portable/AppImage packaging contract and hardened build validation/provenance.
- Corrected the Pad-family slogan to **Friendly. Fast. Focused.**
- No Markdown editing, preview, UI, routing, theme, shortcut or document-workflow behavior changed.

## 0.0.2-r8.2

- Export PDF... now uses Ctrl+Shift+P.
- Indent now uses Ctrl+] and Outdent Ctrl+[.
- Swapped File-menu positions so Exit precedes Save and Exit.
- No other behavior changed.

## 0.0.2-r8.1

- Added Ctrl+Tab / Ctrl+Shift+Tab navigation for Tabbed toolbar pages.
- Swapped Go To Line... and Find and Replace positions on the Tabbed Home toolbar only.
- Added Ctrl+Shift+H for Horizontal Rule.
- Removed Ctrl+Alt+1 / Ctrl+Alt+2 from the App Drag and Drop choices.
- No other behavior changed.

## 0.0.2-r8

- Applied the reviewed Markopad keybinding map and removed the requested Help shortcuts.
- Added shortcut text to toolbar hover tooltips and toolbar right-click access to Tabbed/Classic switching and Classic customisation.
- Added non-binding menu syntax hints for Quote Block, Indent and Code Block.
- Applied the requested Edit/View menu order and naming without changing editor/preview/packaging behavior.

## 0.0.2-r7

- Reworked Keyboard Shortcuts to match Ricopad 0.7.2 r5.1's current two-column `Command | Shortcut` table presentation.
- Retained Markopad's live Search field and All/File/Home/Insert/View/Help Tab filter above the table.
- The table is read-only, hides row numbers, selects whole rows, stretches the Shortcut column and uses native-platform key text.
- Like Ricopad, the dialog now lists only commands that actually have an assigned shortcut; unbound commands are omitted rather than shown as `—`.
- Restored Ricopad's 700×560 dialog geometry and OK-button presentation while keeping the one-instance modeless lifecycle.

## 0.0.2-r6

- Replaced the simple Keyboard Shortcuts message box with a retained, modeless Ricopad-style reference dialog.
- Shortcuts are grouped by Markopad's Tabbed toolbar categories: File, Home, Insert, View and Help.
- Added an All-by-default category dropdown plus live search across command names and rendered shortcut text.
- Shortcut key text uses Qt NativeText and remains mouse-selectable; the dialog follows the Pad-family `Keyboard Shortcuts — Markopad` title convention.

## 0.0.2-r5

- Fixed empty-line Bullet/Numbered/Task List insertion, including indented empty lines.
- Added an AppImage-only high-contrast Classic/Tabbed overflow chevron while deliberately leaving Portable/source native overflow styling untouched.
- Applied the reviewed Edit/View menu ordering and labels; renamed Overall Theme to Theme and Tabbed to Tabbed (default) in the Toolbar submenu.
- Removed the Dark Theme action icon.
- Added focused Markdown-action and UI/runtime regression checks.


## 0.0.2-r1

- Corrected the slogan to **Simple. Fast. Focused.**
- Made Home the default Tabbed page.
- Replaced the stored-executable External Editor chooser with desktop/OS file association opening via `QDesktopServices`, saving pending edits first.
- Renamed the command to **Customise Classic Bar…** and made it available in both Tabbed and Classic modes.

## 0.0.2

- Promoted the refined Markdown-only line to application version 0.0.2 for hands-on testing.
- Renamed user-facing Interface to **Toolbar**, Ribbon to **Tabbed**, and Retro to **Classic**, with preference migration from the old names.
- Removed the Button Labels feature entirely; Tabbed and Classic are now icon-only.
- Replaced the monochrome-teal command pack with the approved traditional neutral-plus-teal light/dark icon family.
- Renamed the icon asset directory to `assets/toolbar-icons/`.
- Preserved exact 52×52 buttons with 36×36 icons, native bordered decoration, Tabbed overflow/collapse, Classic customisation, Markdown fidelity and privacy guarantees.

## 0.0.1-r2.3

- Replaced the horizontally pannable Ribbon page with one-line `QToolBar` pages using Qt's native overflow/extension button when commands do not fit; tab-strip scrolling remains.
- Top-aligned Ribbon command buttons.
- Consolidated Heading 1–6 into one Ribbon Heading dropdown while preserving individual heading actions for Retro customisation.
- Standardised Ribbon and Retro commands to fixed 52×52 buttons with 36×36 icons.
- Restored bordered Ricopad-family button decoration by disabling flat auto-raise styling.
- Extended Dark/Light Editor to control both Source and Preview canvases.

## 0.0.1-r2.2

- Removed Ribbon section labels and section borders entirely.
- Replaced visual section boxes with simple vertical separators between logical Ribbon groups, matching the Retro toolbar's minimal grouping language.
- Kept the r2.1 one-row button model and all other r2/r2.1 behaviour unchanged.

## 0.0.1-r2.1

- Moved Ribbon section labels from the top back to the bottom for UI evaluation; all other r2 Ribbon/button behaviour remains unchanged.

## 0.0.1-r2

- Removed Open Recent and all recent-file tracking for privacy, including cleanup of the obsolete r1 preference.
- Rebuilt the global File/Edit/Markdown/Insert/View/Help menu organization from the first hands-on review.
- Added F2/F3/F4 layout shortcuts, F5 Date and Time, and Esc dismissal of the unchanged Find/Replace bar.
- Kept Markopad's one-row Ribbon, restored simple section borders/top labels, and made Retro customization Retro-only.
- Reworked command icons into Markopad teal for light/dark schemes, including dedicated Task List and layout icons; Ribbon/Retro remain 32×32.
- Optional button labels remain off by default, use smaller text and can wrap to two lines.
- Removed the file-format field from the status bar.
- Added independent Dark/Light Editor canvas control while retaining Overall Theme and independent Source/Preview fonts.

## 0.0.1-r1

- Restored Pad-family About/dialog titles, Preview Only, persistent view/interface/theme state, Ribbon collapse/reveal, Retro customization, optional labels, 32×32 icons, drag/drop behaviour selection and Preview Font.

## 0.0.1

- Initial Markdown-only fork from the preserved Ricopad 0.5.0 codebase.
- Markdown source became the sole document authority; RTF and the Rich Markdown private snapshot architecture were removed.
