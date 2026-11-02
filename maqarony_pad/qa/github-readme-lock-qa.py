#!/usr/bin/env python3
"""Immutable GitHub README gate; authoritative original is SHA-256 pinned.
Only current-version field(s) are permitted to vary. Never update this
reference or its fingerprint as part of routine release versioning.
"""
from pathlib import Path
import hashlib, re, sys
root=Path(__file__).resolve().parents[2]
reference=Path(__file__).with_name("github-readme-authority.txt").read_bytes()
assert hashlib.sha256(reference).hexdigest()=="5deb6ff8c497b453f7f6db20195f0394773e4ef7c1d20a957cfac9aaf118d3a2", "Protected README authority was changed"
expected=reference.decode("utf-8")
assert expected.count("Current release: **1.0.0-x17.6**")==1
expected=expected.replace("Current release: **1.0.0-x17.6**", "Current release: **1.0.2**")
actual=(root/"README.md").read_bytes()
assert actual==expected.encode("utf-8"), "GitHub README differs outside approved version field(s)"
print("PASS immutable GitHub README (version field(s) only)")
