#!/usr/bin/env python3
"""Exercise the real Markdown-only source gate against stale-build false positives.

Positive: populated build/venv, PyInstaller payload, generated AppDir, dist/ with
RTF strings/binary. Negative: forbidden capability in production Python and MIME.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

CHECKER = Path(__file__).with_name("markdown-only-surface-qa.py")

with tempfile.TemporaryDirectory(prefix="maqapad-markdown-scope-") as tmp:
    outer = Path(tmp)
    app = outer / "maqarony_pad"
    widgets = app / "widgets"
    for d in (widgets, app / "assets", app / "packaging/appimage"):
        d.mkdir(parents=True, exist_ok=True)
    minimal = [outer / "main.py", outer / "suite-pythoine-component.json",
               app / "app.py", widgets / "editor.py", app / "assets/maqaronypad.desktop",
               app / "packaging/appimage/maqaronypad.desktop",
               app / "packaging/appimage/io.github.brunonlinespace.maqaronypad.metainfo.xml"]
    for path in minimal:
        path.write_text("# Markdown only\n", encoding="utf-8")
    # Recreate the exact failure mode: third-party packages and frozen outputs
    # in pre-existing build/ and dist/ from a successful/failed build.
    generated = [app / "build/appimage-fedora44-x86_64/venv/lib/python3.14/site-packages/pip/_vendor/pygments/formatters/_mapping.py",
                 app / "build/appimage-fedora44-x86_64/pyinstaller-dist/maqaronypad/_internal/PyQt6/Qt6/translations/qtbase_ca.qm",
                 app / "build/appimage-fedora44-x86_64/MaqaronyPad.AppDir/usr/lib/maqaronypad/rtf-dummy.txt",
                 app / "dist/sample.rtf", app / "qa/generated-excluded.py"]
    for path in generated:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'RtfFormatter; application/rtf; Rich Text Format; \x00\x01')

    def run():
        return subprocess.run([sys.executable, str(CHECKER), str(outer)],
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
    normal = run()
    assert normal.returncode == 0, (normal.stdout, normal.stderr)
    assert "build/dist excluded" in normal.stdout
    source_bad = widgets / "editor.py"
    source_bad.write_text('SUPPORTED_MIME = "application/rtf"\n', encoding="utf-8")
    bad = run()
    assert bad.returncode != 0 and "prohibited RTF" in bad.stderr, (bad.stdout, bad.stderr)
    source_bad.write_text('# Markdown only\n', encoding='utf-8')
    desktop_bad = app / "assets/maqaronypad.desktop"
    desktop_bad.write_text('MimeType=text/rtf;\n', encoding='utf-8')
    bad = run()
    assert bad.returncode != 0 and "prohibited RTF" in bad.stderr, (bad.stdout, bad.stderr)
print('PASS x17.10 Markdown-only gate ignores generated build payload and rejects real application/desktop violations')
