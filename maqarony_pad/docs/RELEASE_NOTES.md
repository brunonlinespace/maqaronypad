# MaqaronyPad 1.0.2 — AppDir smoke-test exit 3 hotfix (2026-11-01)

- Resolves the exact Fedora 44 AppDir system-theme smoke-test exit code 3 reported for Maqarony Pad 1.0.1. Root cause: hard-coded `APP_VERSION == "1.0.0"` in `smoke_test()` survived the bump to 1.0.1.
- Smoke check now validates the runtime Qt application version against `APP_VERSION`; includes dependency-light execution of the real smoke-test logic across all three themes and four icon families, plus negative version-mismatch/stale-assertion reproductions.
- AppStream public final release ordering remains 1.0.2, 1.0.1, 1.0.0, 0.3.4; experimental history retained in the changelog.
- Application features, Markdown preservation, file operations, icons, styles and README content outside the approved current-version field are unchanged.
- Native Fedora build and actual Qt interactive smoke test still require execution on the target environment; dependency-light QA must not be confused with full runtime verification.

# MaqaronyPad 1.0.1 — Final AppStream release-order correction (2026-11-01)

- Fix the confirmed Fedora 44 AppDir assembly failure: AppStream rejected a 1.0.0 public release followed by 1.0.0-x17.10 development editions as not newest-first.
- Public AppStream release list is now 1.0.1, 1.0.0, 0.3.4. Development source history remains documented in these release notes and docs/CHANGELOG.md.
- Fedora builder runs the native AppStream validator in source preflight (when available) before PyInstaller, retains AppDir validation, and explicitly checks stable release order without external Python dependencies. Regression reproduces exact x17.10 error and corrupted stable order.
- No runtime code, icon artwork, application behavior, source layout or README content beyond the current version is modified.

# MaqaronyPad 1.0.0 — Final version promotion (2026-11-01)

- Promote 1.0.0-x17.10 to final 1.0.0 only. No editor, Markdown parsing, file handling, theme/icon behavior or icon asset changes.
- Keep the x17.10 generated-build exclusion QA and all retained packaging checks. Update version-dependent Fedora/Windows packaging fields and source-release gate assertions.
- Add current final AppStream release without removing historical releases; preserve protected GitHub README except the authorized current-version field.

# MaqaronyPad 1.0.0-x17.10 — Markdown-only QA repeat-build correction (2026-11-01)

- Fix second/subsequent Fedora build failures when QA scans prior generated build virtual environments and AppDirs for RTF references. Only application Python and routing metadata are now scanned, never generated dependencies or build outputs.
- Regression exercises the actual verifier with staged venv/Qt/pyinstaller files and asserts true application/desktop RTF changes are still rejected.
- No application code, editor behavior, image assets, or bundled README text change beyond the current-version field.
- Fedora PyInstaller/AppImage runtime and Suite adoption remain unverified in this environment.

# MaqaronyPad 1.0.0-x17.9 — AppStream metadata / actual builder preflight (2026-11-01)

- Fix x17.8 Fedora build abort at AppDir assembly: the AppStream `<releases>` list lacked the current edition, despite passing source QA and PyInstaller.
- Restore omitted x17.8 history and add x17.9 to AppStream without altering established identity or past releases.
- Execute builder's actual `check_inputs` metadata verification before PyInstaller, with a mandatory positive/negative QA harness also exercising `assemble_appdir` using a dummy frozen payload.
- Source editor, themes, icon families and file operations unchanged. README version field only. Real Fedora AppImage packaging/runtime remains untested locally.

# MaqaronyPad 1.0.0-x17.8 — Frozen status-message import and real settings-action smoke (2026-11-01)

- Fix one import in `EditorMessageStatusBar.showMessage`: use `widgets.message_conventions`, the actual module root for both Portable and frozen AppImage, instead of `maqarony_pad.widgets.message_conventions` (which is unavailable when PyInstaller freezes `app.py` from the package directory). This is the shared callback path invoked when choosing Light/Dark/System and Harmony/Humility/Heritage/Halcyon.
- Expand the existing AppDir and final AppImage smoke test to invoke the **real checkable QActions** for all three themes and all four icon families, asserting state, status-message text, and a non-empty command icon. Prevent the previous startup-only smoke test from overlooking Qt callback aborts.
- Add `qa/x178-frozen-status-qa.py`, executing the status callback under a simulated frozen import root without requiring PyQt6. It also guards the actual QAction smoke matrix.
- Keep Markdown editing, assets, component identity, appearance algorithms, file operations, and all other production behavior unchanged. The protected GitHub README changes only its current release version.
- Local QA is dependency-light; real PyQt6/AppImage interaction tests must pass on the Fedora build host.

# MaqaronyPad 1.0.0-x17.7 — Protected README and Halcyon asset correction (2026-11-01)

- Replace the GitHub README with the user-approved updated copy, changing only current-version metadata. Save the supplied bytes as the independently pinned README authority.
- Rename dark Halcyon `impport-file.png` to `import-file.png` without modifying the PNG contents. Validate that both Halcyon themes contain the exact same 144 filenames.
- Preserve all other icon families, command wiring, configuration and editor functionality.

---

# MaqaronyPad 1.0.0-x17.6 — GitHub README authority correction (2026-11-01)

- Correct the root GitHub README against the user-supplied x14.4 authority. Only its current release field becomes x17.6; all other bytes are preserved exactly.
- Correct the independently pinned authority file and README lock checksum. Reject unauthorized additions, historical heading changes, or unrelated edits.
- Preserve previous release history in the existing changelog and documentation. No changes to editor behavior, Halcyon or other icon packs, or file operations.

---

## Earlier release notes (x17.5)

# MaqaronyPad 1.0.0-x17.5 — Halcyon icon family and GitHub README protection (2026-11-01)

- Add Maqa Icons Halcyon to Settings → App Icons, using `assets/toolbar-icons-aero`. The new radio choice has no icon or toolbar command.
- Preserve the previous icon families, family settings, toolbar controls, editor and file-handling behavior.
- Restore the root GitHub README to its protected wording, allowing only the current-version field(s) to change. Archive recovered historical README changes in `docs/history/`; add a mandatory reference-checksum QA gate.
- Static source gates passed; live KDE/PyQt6 GUI behavior remains unverified.

---

## Earlier release notes (x17.4)

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

# MaqaronyPad 1.0.0-x17.0 — Grapheme-aware Chars (2026-10-24)

From x14.4. Count extended grapheme clusters of literal Markdown source through Qt `QTextBoundaryFinder` and per-block revision caching. Preserve document-total caching and invalidate on text edits, including programmatic loads; no full-text extraction for cursor-only status updates. Logical newline between blocks counts once. Leave all file-size/safety limits and editor/preview/file I/O mechanics unchanged. Keep x14.4 warning identity/dismissal correction, labels, status layout and current messaging. No SVG assets in baseline; preserve all 257 PNGs byte-for-byte and leave external SVG import/file dialogs untouched.

The Qt-free QA uses protocol test doubles; live PyQt6, Unicode-version fidelity and large-document performance remain runtime checks.

---

# MaqaronyPad 1.0.0-x14.4 — Status warning identity and character-count caching (2026-10-24)

Built directly from x14.3. Backing-state normalization clears only an active warning explicitly tagged as a backing-file alert. Unrelated critical warnings remain. The Chars indicator retains its previous Python `len(toPlainText())` meaning, including Unicode behavior, but caches the count between text edits to avoid copying the entire document for cursor-only status changes. No Words count, layout, timeouts, ordinary message wording, file transaction, formatting or editor changes. The new Qt-free QA exercises these contracts; live PyQt6 interaction is not verified here.

---

# MaqaronyPad 1.0.0-x14.3 — Message conventions (2026-10-24)

From 1.0.0-x14.2. Status messages use the approved four-second duration for noncritical events; critical unresolved file warnings remain persistent. Save confirmations name the file, file-operation messages use the approved action vocabulary, and complete messages end in periods. No source/editor/drag-and-drop/layout changes.

# MaqaronyPad 1.0.0-x14.2 — Status-message coverage convergence (2026-10-24)

- Ten agreed status-feedback additions, using MaqaronyDesk x18.3 or RiqatonyPad x13.1 as the authority: successful Open, Save As, Save Version As, PDF export, missing local link, Dark Editor canvas switch, application theme switch, external editor launch, containing-folder launch, and external backing-file transition.
- Status messages appear in the existing left editor message field. Existing notification text, status indicator fields, layout and editor/file operations remain unchanged. PDF success requires a fresh nonempty PDF output; watcher alerts occur only on changes of backing state.
- No wording-convergence changes, new dialogs, new actions, workspace features or layout changes. Static x14.2 delivery/preservation regression added; live Fedora Qt GUI validation remains pending.

# MaqaronyPad 1.0.0-x14.1 — Editor status-bar correction (2026-10-23)

- Use exactly two visible editor status labels: independent messages at left; a permanent, right-aligned consolidated indicator at right.
- Editing · document line/column/total characters · encoding/newline · viewing/zoom. Only middle dots between groups; existing thousands separators remain.
- Preserve all Pad styling, status-message timeouts, numerical calculations, file/editor behavior and geometry settings. No workspace changes.

# MaqaronyPad 1.0.0-x14.0 — Editor status bar

- Editing: Insert/Overwrite. Document: Ln current/total, Col current, total Chars. Viewing: Source/Split/Preview and numerical zoom. Format: encoding and newline. Messages: independent final expanding field.
- Preserve existing Pad styling and number formatting, with no workspace or editor changes beyond status presentation.

# MaqaronyPad 1.0.0-x13.0 — Exclusive-install fallback permission parity

Restore Desk-equivalent source permission bits immediately after exclusive destination creation when hard-link installation is unavailable. Only `os.fchmod(descriptor, source_mode)` and its availability guard were added to the existing fallback; the copy loop, no-clobber checks and cleanup remain unchanged. Release identity and targeted regression QA updated. No other production behavior changed.

# MaqaronyPad 1.0.0-x12.6 — Source editor end-of-file scrolling

Correct the excessive blank space reachable below the last line of Markdown source by changing only the editor constructor from `setCenterOnScroll(True)` to `setCenterOnScroll(False)`. This follows the established Sheepy Pad 0.4.1 correction. Explicit Go To Line and the existing scroll/gutter/layout logic remain unchanged. Updated release identity and static QA only; live GUI verification remains outstanding.

# MaqaronyPad 1.0.0-x12.5

Behaviour-preserving presentation extraction: relocate existing About, Quick Tour and Keyboard Shortcuts application methods into `widgets/about_dialog.py`, `widgets/quick_tour.py` and `widgets/keyboard_shortcuts.py`; consolidate the existing shortcut-search helper without changing its implementations. No dialog classes or unrelated changes.

# MaqaronyPad 1.0.0-x12.4 — Keyboard-shortcut helper convergence (2026-10-18)

- Relocated existing keyboard-shortcut query helpers to `widgets/shortcut_search.py`, preserving original implementations and user behaviour.
- Moved the original private helper functions from `app.py`, retained their names and behaviour, and updated their import paths.
- Kept document Find/Replace and editing code unchanged; updated version metadata, manifests and QA.
- No public README content edits beyond current-version references.

---

# MaqaronyPad 1.0.0-x12.3 — Widget-tree reorganisation (2026-10-18)

- Relocated existing graphical modules into `widgets/` and editor-specific components into `widgets/mwpyn/`, without changing application/editor class methods.
- Updated imports, the RiqatonyPad resource-root lookup where applicable, build staging, active source QA and manifests.
- Kept application startup, document codecs and services outside the widget folders; no compatibility shims were added.
- Preserved GitHub root and internal README content apart from current version references. Live Qt/AppImage/Windows builds remain unverified.

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

- Derived strictly from 1.0.0-x2.0, itself based on the corrected 0.3.4 source lineage.
- Moved 16 existing source-editor keyboard/IME, paste, drag-and-drop, Markdown insertion, duplication, indentation and newline methods into `editor_insertion.py` as `EditorInsertionMixin`.
- Original method text, product-specific safety messages, source-of-truth semantics, document limits, subclass APIs and Qt signal behaviour retained.
- Introduced x3 exact-text fingerprint gate for the full 57-method inventory, while retaining the x1/x2 gates.
- No dialog migration, constants extraction, folder reorganisation, preview changes or filename alignment; the approved `editor_source.py`/`editor_preview.py` rename remains reserved for x4.0.

---

# MaqaronyPad 1.0.0-x2.0 — editor formatting extraction

- Derived strictly from **1.0.0-x1.1**, preserving separate standalone/workspace responsibilities.
- Relocated 13 existing Markdown source-editor formatting methods into `editor_formatting.py` as `EditorFormattingMixin`, without editing their definition text.
- The Markdown source editor continues to expose the same class and commands through inheritance. No Markdown preview, insertion, clipboard, file lifecycle, preferences or dialog changes.
- An exact-text method fingerprint gate verifies all 57 baseline source-editor methods, including the 44 retained in the original class.
- Updated active build/source-package contracts and retained historical release records.
- File-name alignment to `editor_source.py` and `editor_preview.py` is reserved for x4.0; no module renames now.

---

# MaqaronyPad 1.0.0-x1.1 — editor-widget extraction from 0.3.4

- Corrective branch from the previously omitted **MaqaronyPad 0.3.4** baseline. This supersedes `1.0.0-x1.0` as the source master for later MaqaronyPad extraction stages; MepyNamu `1.0.0-x1.0` is unchanged.
- Relocated the unmodified `HighlightRule`, `MarkdownHighlighter`, `LineNumberArea`, `_scheme` and `MARKDOWN_COLOR_SCHEMES` definitions from `source_editor.py` to `editor_widgets.py`.
- Preserved the 0.3.4 `MarkopadSourceEditor` class and `MarkdownPreview` in their original modules. The earlier `mwpyn/` namespace is **not** restored.
- Kept source-editor import compatibility, Markdown source authority, existing UI/menus, preview, preferences and file lifecycle unchanged.
- Extended Fedora AppImage input validation, version identifiers, and source-integrity/release QA for the extracted helper module. Retained all older release-specific QA scripts and release notes intact.
- No dialog migration, `app_constants.py` creation or editor-folder reorganisation.

# MaqaronyPad 0.3.4 — Restore original source editor and preview modules

- Restored `source_editor.py` and `preview.py` from the authoritative Markopad 0.2.10 implementation, retaining only the existing MaqaronyPad product wording in user-visible safety messages and comments.
- Restored the original `MarkopadSourceEditor` and `MarkdownPreview` class names and direct imports; removed the experimental `mwpyn/` package.
- Updated only the dependent application imports, AppImage input checks, active QA paths and current release metadata. Existing editor/preview algorithms and all user-facing MaqaronyPad identity, KDE window-list integration and toolbar/icon assets remain unchanged.
- Earlier release records and version-specific QA files are retained as history; the new 0.3.4 checks validate the restored module layout without rewriting old checks.

# Markopad 0.2.10 — Quick Tour corrective and More Actions ordering

Markopad 0.2.10 is deliberately limited to the approved corrective/UI changes from 0.2.9.

- Fixed the Quick Tour crash: **Open Keyboard Shortcuts…** now calls Markopad's existing `show_shortcuts()` dialog instead of the nonexistent Ricopad callback name.
- About dialog: **Preferences** is renamed to **Configuration**.
- Modern File toolbar: the More Actions buttons now follow File → More Actions AppMenu order: **Duplicate File → Rename → Delete File → Open in External Editor → Open Containing Folder → Properties**.
- The File → More Actions AppMenu itself is unchanged.
- No editor, Preview, file lifecycle, status-bar, Find/Replace, formatting, shortcut, icon, theme, or unrelated toolbar change is included.
