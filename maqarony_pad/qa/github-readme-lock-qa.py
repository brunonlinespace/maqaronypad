#!/usr/bin/env python3
"""Immutable GitHub README gate; authoritative original is SHA-256 pinned.
Only the explicitly approved 1.1.7 README corrections are permitted to vary.
Never update this reference or its fingerprint as part of routine release versioning.
"""
from pathlib import Path
import hashlib, re, sys
root=Path(__file__).resolve().parents[2]
reference=Path(__file__).with_name("github-readme-authority.txt").read_bytes()
assert hashlib.sha256(reference).hexdigest()=="5deb6ff8c497b453f7f6db20195f0394773e4ef7c1d20a957cfac9aaf118d3a2", "Protected README authority was changed"
expected=reference.decode("utf-8")
assert expected.count("Current release: **1.0.0-x17.6**")==1
expected=expected.replace("Current release: **1.0.0-x17.6**", "Current release: **1.1.7**")
expected=expected.replace(
    "- **Modern** six-tab toolbar plus a fully customisable **Classic** toolbar.",
    "- **Modern** six-tab toolbar plus a fully customisable **Classic** toolbar and an explicit **Disabled (AppMenu only)** mode.",
)
expected=expected.replace(
    "- Persistent native/global **AppMenu** available in both toolbar modes.",
    "- **Modern** hides the local AppMenu while preserving compatible desktop global-menu export; **Classic** and **Disabled (AppMenu only)** keep the local AppMenu visible.",
)
expected=expected.replace(
    "- Searchable **Keyboard Shortcuts**, persistent **Quick Tour**, bundled documentation, GitHub and issue links.",
    "- Searchable **Keyboard Shortcuts**, persistent **Quick Tour**, root-README documentation, GitHub and issue links.",
)
expected=expected.replace(
    "The native application menu remains available in both toolbar modes and follows the canonical:\n\n"
    "**File → Edit → Markdown → Insert → View → Settings → Help**\n\ncommand model.",
    "MaqaronyPad keeps one native application menu as the menu authority. In **Modern**, the local AppMenu is hidden while the same menu objects remain intact so compatible desktop global-menu integration can remain available; on systems without a global menu, Modern intentionally has no local AppMenu. In **Classic** and **Disabled (AppMenu only)**, the local AppMenu remains visible whether or not the desktop also exposes a global menu.\n\n"
    "The canonical menu model remains:\n\n**File → Edit → Markdown → Insert → View → Settings → Help**",
)
expected=expected.replace("MaqaronyPad-1.0.0-x14.4-x86_64", "MaqaronyPad-1.1.7-x86_64")
expected=expected.replace(
    "Its catalogue follows AppMenu order. Every Classic item is removable, so the toolbar may be completely empty; the permanent AppMenu remains the recovery and control surface.\n\n"
    "The **Editor Toolbar** flyout is available from both Modern and Classic and contains:\n\n"
    "- **Modern (default)**\n- **Classic**\n- **Customise Classic Bar…**\n",
    "Its catalogue follows AppMenu order. **Classic Settings...** includes **Clear All** for optional commands, while the Classic Settings control itself remains permanently available on the Classic bar so the toolbar cannot be made completely unusable through customisation.\n\n"
    "The **Editor Toolbar** flyout contains:\n\n"
    "- **Modern (default)**\n- **Classic**\n- **Classic Settings...**\n- **Disabled (AppMenu only)**\n\n"
    "**Disabled (AppMenu only)** hides both toolbar command surfaces while leaving the AppMenu available locally and to compatible desktop global-menu integration.\n",
)
marker=(
    "A finished AppImage can additionally be exercised with:\n\n```bash\n"
    "./maqarony_pad/packaging/fedora/test-appimage.sh\n```\n"
)
windows=(
    "\n## Building the Windows portable application\n\n"
    "On Windows, run the included PowerShell builder with Python 3 available through the `py` launcher:\n\n"
    "```powershell\n.\\maqarony_pad\\packaging\\windows\\build-windows-portable.ps1\n```\n\n"
    "The builder creates an isolated environment and produces an **onedir portable Windows application** under:\n\n"
    "```text\nmaqarony_pad\\dist\\MaqaronyPad-1.1.7-windows-portable\\\n"
    "    maqaronypad.exe\n    README.md\n    _internal\\\n```\n\n"
    "This is a portable Windows build, not an installer. It does not install file associations or write Windows registry entries.\n"
)
expected=expected.replace(marker, marker+windows)
actual=(root/"README.md").read_bytes()
assert actual==expected.encode("utf-8"), "GitHub README differs outside the explicitly approved 1.1.7 corrections"
print("PASS protected GitHub README with only approved 1.1.7 corrections")
