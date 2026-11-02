# Toolbar and layout behaviour — Markopad 0.2.10


## 0.2.4 Source / Preview interaction

In Source + Preview, Copy and Select All follow the last text surface the user actually interacted with. While Preview owns that interaction focus, source-mutating commands are unavailable rather than silently acting on Source. Returning to Source restores normal editing availability. Double-clicking the Source/Preview divider restores the canonical 3:2 split and persists the reset. Find/Replace behavior is unchanged.


## 0.2.2 Tabbed / Classic alignment

Modern (internally `tabbed`) pages remain **File | Home | Insert | View | Settings | Help**. The View page exposes **Editor Toolbar** as a `toolbar-classic` flyout containing the canonical AppMenu entries **Modern (default)**, **Classic**, separator, and **Customise Classic Bar…**. The dedicated binary toolbar button remains removed, while `Ctrl+Alt+Shift+T` independently flips Modern↔Classic.

Classic customization follows the AppMenu's **File → Edit → Markdown → Insert → View → Settings → Help** order. Normal submenu commands are flattened except the approved **Editor Toolbar** flyout and the two dirty-document policy flyouts. Multi-choice sets such as Light/Dark/System and Source/Split/Preview stay separate; App Drag-and-Drop remains the single compact binary toggle. Exit stays available as an optional Classic item. Classic can still be saved with no controls at all.

The default Classic selection includes Image Reference, all three editor layouts, and the single Editor Toolbar flyout in addition to the established core commands.

## Toolbar

Markopad offers two toolbar modes over the same QAction command model. **Modern (default)** is the user-facing name of the internal `tabbed` mode; **Classic** is the traditional customisable toolbar. The selected Toolbar mode persists, and `Ctrl+Alt+Shift+T` flips between them.

The application AppMenu is independent of toolbar mode: it remains available in both Tabbed and Classic and explicitly uses Qt's native/global-menu contract.

### Modern

Modern (internal `tabbed` mode) is deliberately one command row tall. Each tab hosts a non-movable `QToolBar`; when the window is too narrow, Qt's native right-side overflow/extension control contains commands that no longer fit. The command row itself is not horizontally pannable or scrollable. The tab strip keeps normal scroll buttons and mouse-wheel tab navigation. Logical command groups use simple vertical separators.

Double-click a tab to collapse its controls. While collapsed, click a tab once to reveal them. The collapsed state persists.

Heading is a single dropdown containing Normal Paragraph and Heading 1 through Heading 6. Home also uses the shared Code flyout for Inline Code and Code Block.

### Classic

Classic uses the same actions and button geometry in one traditional toolbar. Its customization catalogue follows AppMenu order and is flat by default. **Editor Toolbar** is one optional flyout containing Modern, Classic and Customise Classic Bar…; **App Drag-and-Drop** remains one optional binary toggle; the two dirty-document policy controls remain flyouts. Individual Normal Paragraph and Heading 1–6 actions remain available for Classic customisation. Every item is removable, so Classic may be empty; the permanent AppMenu remains the recovery/control surface. Right-click either toolbar, including its command buttons, to switch mode or open Classic customisation.

## Command-button standard

Both modes are icon-only. There is no button-label option. Every command button is exactly 52×52 pixels and displays a 36×36 icon. Buttons retain bordered desktop/Ricopad-family decoration rather than flat auto-raise styling.

Markopad uses the canonical Marko Plus command-icon family introduced in 0.1.9. Tabbed and Classic resolve the same QAction to the same semantic icon; the two toolbar presentations do not maintain separate icon mappings.

## Document layouts

- **Source Only** — authoritative Markdown editor only (Ctrl+1).
- **Source + Preview** — source editor and read-only Markdown preview in a splitter (Ctrl+2).
- **Preview Only** — rendered read-only viewing surface (Ctrl+3).

Layout and splitter position persist. Preview never writes back to source.

### AppImage overflow visibility

Portable/source runs leave Qt's host-native toolbar extension control untouched. In the self-contained AppImage only, Markopad gives the native `qt_toolbar_ext_button` a larger high-contrast chevron treatment so Classic and Tabbed overflow remain discoverable across System, Dark and Light themes without changing Portable behaviour.
