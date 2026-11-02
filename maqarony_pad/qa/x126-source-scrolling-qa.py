#!/usr/bin/env python3
"""x12.6: Sheepy Pad 0.4.1 cursor-centering correction only."""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "widgets/mwpyn/editor_source.py").read_text(encoding="utf-8")
old = "        self.setCenterOnScroll(True)"
new = "        self.setCenterOnScroll(False)"
assert source.count(new) == 1 and old not in source
# Removing the one agreed change recovers the exact x12.5 source bytes.
assert hashlib.sha256(source.replace(new, old).encode()).hexdigest() == "e24c7255b60735e8d54381eca0cc82e63343027876cfce1f96259f0424b7b193"
print("PASS x12.6: only source-editor automatic centering changed")
