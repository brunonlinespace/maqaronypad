# Security review — 0.2.10

Markopad keeps the source-authoritative safety baseline: bounded source/paste sizes, bounded search results and no rich-document parser. In 0.1.3, reads use stable exact-content snapshots; saves re-check the expected file identity before atomic replacement; rename/delete refuse raced replacements; and active-file monitoring distinguishes normal, changed and missing backing states without scanning unrelated folders.

Preview is read-only. Implicit remote/data resource loading is blocked. Markdown links require explicit user activation.

Markopad stores presentation/editor preferences but deliberately stores no recent-file history. The 0.0.2 migration removes the obsolete `recent_files` and button-label preferences and migrates the previous toolbar naming without keeping a browsing history.

In 0.1.5, the same preferences data is persisted through a bounded, non-symlink regular-file read and private atomic-write path. Unsafe or damaged input falls back to existing defaults; successful writes use private temporary permissions, fsync and atomic replacement without changing any preference schema.

In 0.1.6, Audit Item 23 hardens document path identity for symbolic links. Stable snapshots record both the final path entry (`lstat`) and opened regular target (`fstat`). Save through an unchanged symlink resolves and revalidates the same target immediately before atomic replacement; retargeting/replacement races are cancelled. Normal regular-file and Delete/Rename semantics remain unchanged.

The Fedora AppImage builder is permanently non-privileged and does not invoke host package managers or elevation helpers.

In 0.1.7, shortcut and shortcut-dialog convergence does not alter document, filesystem, preference, preview or process-launch security boundaries.

In 0.1.8, theme/default convergence changes only application palette/default selection. It does not alter document, filesystem, preference-persistence, preview, process-launch, shortcut or lifecycle security boundaries. Existing stored theme/canvas choices remain data, not migration targets.

In 0.1.9, icon-family convergence changes packaged artwork and QAction icon mapping only. It does not alter filesystem, document, preference, preview, process-launch, shortcut or lifecycle security boundaries.

In 0.2.0, AppMenu/native-menu and shortcut-inventory convergence changes only menu visibility/native-menu policy and how the read-only shortcut reference discovers existing assigned shortcuts. It does not alter shortcut assignments, command execution, filesystem, document, preference, preview, process-launch or lifecycle security boundaries.

In 0.2.1, the Settings-tab corrective changes only which existing QActions are presented directly versus through existing policy flyouts and adds descriptive tooltips to those direct controls. It does not alter the underlying settings, Paste behavior, shortcut assignments, command execution, filesystem, document, preference-persistence, preview, process-launch or lifecycle security boundaries.

In 0.2.2, Classic-toolbar alignment changes only command presentation/inventory and two synthetic binary toolbar controls. It does not alter AppMenu actions, Paste behavior, shortcut assignments, document/filesystem operations, preference persistence, preview, process-launch or lifecycle security boundaries.


In 0.2.4, Audit Item 32 changes only Source/Preview command targeting and splitter interaction. Preview focus can no longer leave source-mutating commands live in Split mode; Copy/Select All target the active read-only Preview when appropriate. The source editor, Preview renderer, Find/Replace, document/filesystem operations, Paste engine and process-launch boundaries are unchanged.

In 0.2.10, runtime changes are limited to the Quick Tour callback correction, the About-dialog label, and Modern File-toolbar More Actions ordering. No icon assets, editor engine, Preview renderer, Item 32 focus-routing guards, document/filesystem operations, Paste engine or process-launch boundaries are changed.


Markopad 0.2.10 changes only UI callback/label/order presentation. No filesystem, process-launch, parser, renderer, clipboard, or document-size safety boundary is changed.
