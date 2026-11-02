#!/usr/bin/env python3
"""Check only shipped application sources and routing metadata for non-Markdown support.

The source archive can be built repeatedly. Generated build/, dist/, virtualenv,
PyInstaller bundles and Qt translations are NEVER application source and must not
be used for a Markdown-only capability assertion.
"""
from pathlib import Path
import re
import sys

SOURCE_ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
APP = SOURCE_ROOT / "maqarony_pad"
PATTERN = re.compile(r"\.rtf\b|text/rtf|application/rtf|Rich Text Format|new_rtf|mode_rtf|rtf_to|to_rtf|parse_rtf", re.IGNORECASE)

# Only production Python, never tests or third-party/generated code. Historical
# documentation may legitimately discuss old RTF capabilities that were removed.
IGNORED_TOP_LEVEL = {"qa", "packaging", "assets", "docs", "build", "dist", "__pycache__"}
sources = [SOURCE_ROOT / "main.py", SOURCE_ROOT / "suite-pythoine-component.json",
           APP / "assets/maqaronypad.desktop",
           APP / "packaging/appimage/maqaronypad.desktop",
           APP / "packaging/appimage/io.github.brunonlinespace.maqaronypad.metainfo.xml"]
sources.extend(sorted(path for path in APP.rglob("*.py")
                      if path.relative_to(APP).parts[0] not in IGNORED_TOP_LEVEL
                      and "__pycache__" not in path.parts))
for path in sources:
    if not path.is_file():
        raise SystemExit(f"Markdown-only QA missing expected source: {path}")
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if PATTERN.search(line):
            raise SystemExit(f"Markdown-only QA: prohibited RTF capability/reference at {path}:{lineno}: {line.strip()}")
print(f"PASS Markdown-only source/routing surface ({len(sources)} production files; build/dist excluded)")
