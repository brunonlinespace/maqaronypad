# Recovered GitHub README changes (historical archive only)

Captured from source MaqaronyPad 1.0.0-x17.4 before restoration. This is NOT the GitHub README.
The canonical README is protected except for current-version field(s).

```diff
--- authoritative README
+++ pre-repair README 1.0.0-x17.4
@@ -1,4 +1,32 @@
-# MaqaronyPad 1.0.0-x14.5 — Unicode Chars correction
+# MaqaronyPad 1.0.0-x17.4 — Quick Tour crash hotfix (2026-10-31)
+
+- Restore the four missing Qt imports (`QWizardPage`, `QVBoxLayout`, `QLabel`, `QTimer`) in the extracted Quick Tour module. The undefined `QWizardPage` raised a Python `NameError` inside the toolbar QAction callback, which PyQt6 translated into a fatal abort.
+- Add an executable, Qt-independent Quick Tour construction regression test covering all seven pages, action handling and close cleanup. Preserve all existing tutorial text, dialogs, other commands and icon files unchanged.
+
+---
+
+# MaqaronyPad 1.0.0-x17.2 — Exit on Editor Toolbar (2026-10-31)
+
+- Expose the existing **Exit QAction** last in the **Modern File** tab, preceded by a separator.
+- Include Exit in the **default Classic toolbar selection**, ordered last among File commands. Preserve saved Classic customizations (including whether Exit was selected).
+- Retain `exit.png` artwork, the existing Quit shortcut (`Ctrl+Q` on Linux) in its tooltip, and the existing close/unsaved-changes workflow.
+- No changes to AppMenu ordering, icon artwork, Markdown functionality or file-handling behavior. Live PyQt6/KDE testing remains pending.
+
+---
+
+# MaqaronyPad 1.0.0-x17.1 — Editor Toolbar icon wiring (2026-10-31)
+
+Targeted icon-only wiring from x17.0: **Editor Toolbar** AppMenu parent and shared toolbar flyout use `layout-ribbon.png`; the **Modern (default)** and **Classic** mutually exclusive submenu actions use `toolbar-tabbed.png` and `toolbar-classic.png`, respectively. The parent icon does not follow selection. No icon artwork, toolbar mode semantics, preferences, or Markdown/file behavior changed.
+
+---
+
+# MaqaronyPad 1.0.0-x17.0 — canonical toolbar icon pack (2026-10-31)
+
+Canonical 288-PNG toolbar icon replacement and five approved icon wiring targets; no legacy toolbar asset retention.
+
+---
+
+# MaqaronyPad 1.0.0-x17.0 — Unicode Chars correction
 
 - Grapheme-aware `Chars` counts literal Markdown source (including syntax/whitespace, with each logical newline counted once).
 - Unchanged source lines are cached by `QTextBlock` revision; the full result is cached between edits. Cursor-only movements do not recalculate.
@@ -23,7 +51,7 @@
 
 MaqaronyPad is a focused standalone Markdown editor built around an authoritative Markdown source editor and a read-only rendered preview. It reads and writes ordinary Markdown files directly, without introducing a private document format or workspace database.
 
-Current release: **1.0.0-x14.4**
+Current release: **1.0.0-x17.1**
 
 > **Historical attribution correction (1.0.0-x11.0):** The 0.2.10 shortcuts/Quick Tour correction was released as **Markopad 0.2.10**, not MaqaronyPad. The archived sentence immediately below is retained unchanged.
 
```
