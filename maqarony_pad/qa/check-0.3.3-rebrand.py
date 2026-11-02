#!/usr/bin/env python3
"""MaqaronyPad 0.3.3 identity, packaging and preserved-behavior source audit.

Independent of PyQt6; original Markopad 0.2.10 source remains immutable.
"""
from __future__ import annotations
import ast, json, subprocess, xml.etree.ElementTree as ET, hashlib
from pathlib import Path

P = Path(__file__).resolve().parents[1]
ROOT = P.parent
src = (P / "app.py").read_text(encoding="utf-8")
engine = (P / "mwpyn/engine.py").read_text(encoding="utf-8")
parser = (P / "mwpyn/parser.py").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "suite-pythoine-component.json").read_text())
expected={"id":"maqaronypad", "name":"MaqaronyPad", "version":"0.3.3", "desktop_id":"maqaronypad", "publisher_id":"brunonlinespace", "component_kind":"editor", "portable_command":["main.py"], "extensions":[".md",".markdown",".mdown",".mkd"], "capabilities":{"routing":True,"open":True,"create":True}, "icon":"maqarony_pad/assets/icons/maqaronypad.png", "repository":"https://github.com/brunonlinespace/maqaronypad"}
for key,value in expected.items():assert manifest.get(key)==value,(key,manifest.get(key),value)
assert sorted(p.name for p in ROOT.iterdir())==['README.md','main.py','maqarony_pad','suite-pythoine-component.json']
for file in [ROOT/'main.py',*P.rglob('*.py')]:compile(file.read_text(encoding='utf-8'),str(file),'exec')
for key in ('APP_NAME = "MaqaronyPad"','APP_ID = "maqaronypad"','DESKTOP_ID = "maqaronypad"','APP_VERSION = "0.3.3"','CONFIG_FILE = CONFIG_DIR / "maqaronypad.json"','from mwpyn.engine import MwpynSourceEditor','from mwpyn.parser import MwpynPreview'):
 assert key in src,key
assert 'from source_editor import' not in src and 'from preview import' not in src
assert 'class MwpynSourceEditor' in engine
assert 'class MwpynPreview' in parser
assert 'self.setReadOnly(True)' in parser
assert 'if scheme in {"http", "https", "ftp", "data"}' in parser
assert 'self.setMarkdown(str(markdown))' in parser
assert 'MAX_PASTE_CHARACTERS = 5_000_000' in engine
assert 'MAX_DOCUMENT_CHARACTERS = 25_000_000' in engine
assert 'MAX_FILE_BYTES = 25 * 1024 * 1024' in (P/'document_io.py').read_text()
assert 'safe_atomic_save(' in src and 'self.source_only_action = self._action("Source Only"' in src
assert 'self.editor = MwpynSourceEditor(central)' in src
assert 'self.preview = MwpynPreview(central)' in src
assert '--maqaronypad-smoke-test' in src
assert 'if args.maqaronypad_smoke_test: return smoke_test(theme)' in src
assert 'MaqaronyPadWindow' in src
assert 'load_json_settings' in src and '.config' in src and 'markopad.json' not in src
for where in ('assets/maqaronypad.desktop','packaging/appimage/maqaronypad.desktop'):
 text=(P/where).read_text()
 for line in ('Name=MaqaronyPad','Exec=maqaronypad %F','Icon=maqaronypad','MimeType=text/markdown;','StartupWMClass=MaqaronyPad'):
  assert line in text,(where,line)
meta=ET.parse(P/'packaging/appimage/io.github.brunonlinespace.maqaronypad.metainfo.xml').getroot()
assert meta.findtext('id')=='io.github.brunonlinespace.maqaronypad'
assert meta.findtext("launchable[@type='desktop-id']")=='maqaronypad.desktop'
assert meta.findtext('name')=='MaqaronyPad'
assert meta.find("./releases/release[@version='0.3.3']") is not None
assert meta.find("./releases/release[@version='0.2.10']") is None
assert (P/'assets/icons/maqaronypad.png').is_file()
assert (P/'assets/icons/maqaronypad.ico').is_file()
assert (P/'assets/icons/maqaronypad-about.png').is_file()
assert "about_art = asset_path(\"icons\", \"maqaronypad-about.png\")" in src
assert (P/'assets/icons/maqaronypad-master.png').is_file()
assert (P/'packaging/appimage/maqaronypad.png').read_bytes()==(P/'assets/icons/maqaronypad.png').read_bytes()
for size in ('16x16','22x22','24x24','32x32','48x48','64x64','128x128','256x256','512x512'):
 assert (P/f'assets/hicolor/{size}/apps/maqaronypad.png').is_file(),size
builder=(P/'packaging/fedora/build-appimage.sh').read_text()
for key in ('APP_NAME="MaqaronyPad"','APP_ID="maqaronypad"','APP_VERSION="0.3.3"','APPSTREAM_ID="io.github.brunonlinespace.maqaronypad"','mwpyn/engine.py','mwpyn/parser.py','validate_build_root','pip check','pip freeze --all','Qt PrintSupport was not bundled.','Unexpected Qt WebEngine payload was bundled.','appstreamcli validate --no-net','run_theme_smoke_matrix "final AppImage"'):
 assert key in builder,key
for required in ('"$HERE/maqaronypad"', '"$APPDIR/usr/lib/maqaronypad"'):
 assert required in builder or required=='"$APPDIR/usr/lib/maqaronypad"',required
assert '/usr/bin/markopad' not in (P/'packaging/appimage/AppRun').read_text()
assert 'markopad' not in (P/'app.py').read_text().lower()
# KDE/X11 window class and Wayland desktop identity are deliberately different layers.
assert 'app.setApplicationName(APP_NAME); app.setApplicationDisplayName(APP_NAME); app.setApplicationVersion(APP_VERSION)' in src
assert 'app.setDesktopFileName(DESKTOP_ID)' in src
assert 'DESKTOP_ID = "maqaronypad"' in src
# Both application desktop entries must advertise the same explicit X11 class.
assert all('StartupWMClass=MaqaronyPad' in (P / where).read_text() for where in ('assets/maqaronypad.desktop','packaging/appimage/maqaronypad.desktop'))
# Source-tree test stays exact and locale-independent, on every host.
static_qa = (P/'qa/static-qa.sh').read_text()
assert 'LC_ALL=C sort' in static_qa
# Preserve the execute permissions carried by the pre-rebrand source archive.
import stat
for executable in (ROOT/'main.py',P/'packaging/fedora/build-appimage.sh',P/'packaging/fedora/test-appimage.sh',P/'packaging/appimage/AppRun',P/'portable/run-maqaronypad.sh',P/'qa/static-qa.sh'):
 assert executable.stat().st_mode & stat.S_IXUSR, f'missing executable permission: {executable}'
assert '"README.md main.py maqarony_pad suite-pythoine-component.json"' in static_qa

subprocess.run(['bash','-n',str(P/'packaging/fedora/build-appimage.sh')],check=True)
subprocess.run(['bash','-n',str(P/'packaging/fedora/test-appimage.sh')],check=True)
subprocess.run(['bash','-n',str(P/'packaging/appimage/AppRun')],check=True)
print('PASS MaqaronyPad 0.3.3 identity, technology and packaging gate')
