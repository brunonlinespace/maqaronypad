#!/usr/bin/env python3
"""Dependency-light Markopad 0.1.3 final Marko-family alignment contract."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APP=(ROOT/'markopad.py').read_text()
IO=(ROOT/'document_io.py').read_text()

COMPONENT=(ROOT.parent/'suite-pythoine-component.json').read_text()
META=(ROOT/'packaging/appimage/io.github.brunonlinespace.markopad.metainfo.xml').read_text()
DESKTOP=(ROOT/'packaging/appimage/markopad.desktop').read_text()
BUILDER=(ROOT/'packaging/fedora/build-appimage.sh').read_text()
assert 'APP_VERSION = "0.1.3"' in APP
# Item 3
assert 'MAX_FILE_BYTES = 25 * 1024 * 1024' in IO
for token in ('codecs.BOM_UTF32_LE','codecs.BOM_UTF32_BE','encoding_override: str | None = None'):
    assert token in IO, token
assert 'return self._save_as_target(target)' in APP and 'preserve_encoding=False' not in APP
assert 'Markopad saves Markdown documents only.' in APP
assert 'def _choose_source_encoding' in APP
# Locked Mode / Properties
assert 'self.view_only_action = self._action("Locked Mode", self.toggle_locked_mode, "F12", checkable=True)' in APP
assert '"locked_mode": self.view_only_action.isChecked()' in APP
assert 'lock_suffix = " — Locked Mode" if self.editor.isReadOnly() else ""' in APP
assert 'self.properties_action = self._action("Properties", self.show_properties, "F4")' in APP
for token in ('add_group("File"','add_group("Document"','("Locked Mode", "On" if self.editor.isReadOnly() else "Off")'):
    assert token in APP, token
# Exact approved menu structure
menu=APP[APP.index('def _create_menus'):APP.index('def _create_central_ui')]
for token in ('self.file_menu.addAction(self.save_as_action)\n        more = self.file_menu.addMenu("More Actions")',
              'markdown.addAction(self.inline_code_action); markdown.addAction(self.code_fence_action)\n        markdown.addSeparator()\n        headings = markdown.addMenu("Heading")',
              'insert.addAction(self.image_action)', 'links = insert.addMenu("Link")',
              'view.addAction(self.fullscreen_action)', 'view.addAction(self.status_bar_action)',
              'view.addAction(self.view_only_action)', 'layout = view.addMenu("Editor Layout")',
              'self.toolbar_menu = view.addMenu("Editor Toolbar")', 'zoom = view.addMenu("Editor Zoom")',
              'more_settings = view.addMenu("Editor Miscellaneous")', 'settings = bar.addMenu("&Settings")',
              'theme_menu = settings.addMenu("App Theme")', 'behaviour = settings.addMenu("App Drag-and-Drop")',
              'dirty_duplicate = settings.addMenu("Duplicate External File with Unsaved Changes")',
              'dirty_external = settings.addMenu("Open Externally with Unsaved Changes")'):
    assert token in menu, token
# Desktop identity
for token in ('app.setApplicationName(APP_ID)','app.setApplicationDisplayName(APP_NAME)','app.setOrganizationDomain(ORGANIZATION_DOMAIN)','app.setDesktopFileName(DESKTOP_ID)'):
    assert token in APP, token
assert '"desktop_id": "markopad"' in COMPONENT
assert '<id>io.github.brunonlinespace.markopad</id>' in META
assert '<launchable type="desktop-id">markopad.desktop</launchable>' in META
assert 'StartupWMClass=markopad' in DESKTOP
assert 'SUITE_DESKTOP_ID="markopad"' in BUILDER
assert 'APPSTREAM_ID="io.github.brunonlinespace.markopad"' in BUILDER
# Explicit non-scope: Item 8 and status remain
assert 'self.save_as_action = self._action("Save As…", self.save_as, QKeySequence.StandardKey.SaveAs)' in APP
assert 'self.status_left.setText(f"Ln {line}/{self.editor.document().blockCount()}  Col {col}  Chars {len(text):,}  Words {words:,}")' in APP
print('Markopad 0.1.3 family-alignment contract passed.')
