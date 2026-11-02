# MaqaronyPad QA

Run dependency-light release checks from the source tree with:

```bash
bash maqarony_pad/qa/static-qa.sh
```

GUI smoke tests are additionally run by the AppImage builder when PyQt6 is installed in its isolated build environment.

The Pad UI audit also guards the retained modeless Keyboard Shortcuts dialog. Its search keeps the 0.1.7 Plus fuzzy shortcut-token matching; in 0.1.10 its menu-backed inventory is discovered recursively from the live File/Edit/Markdown/Insert/View/Settings/Help AppMenu.

Current release-specific gate: `check-0.3.3-ui-corrective.py`, derived directly from `check-0.2.10-ui-corrective.py`. It enforces the Quick Tour callback correction, About-dialog Configuration label, and More Actions toolbar/AppMenu ordering contract.

The original 0.2.10 static QA runner is restored as the active basis (identity/path/version changes only, plus its own root-README listing correction). The existing 0.3.1 rebrand/UI tests are rebased to 0.3.3 and run as additional gates. Historical QA scripts are retained.

MaqaronyPad 0.3.3: the inherited exact four-item root contract is retained, with `LC_ALL=C sort` so Fedora locale ordering cannot produce false failures. The current release gates are version-adapted copies of the 0.3.2 gates; older historical checks remain unchanged. The Qt display application name is MaqaronyPad, while the technical Wayland desktop-file identifier remains `maqaronypad`, and X11 `StartupWMClass` follows the Qt application name. KDE task-list behavior requires GUI confirmation.

Archive mode preservation: executable bits lost in the 0.3.2 source ZIP are restored from the Markopad 0.2.10 archive (and on current QA scripts), including main.py, Fedora scripts, portable launcher and AppRun. The 0.3.3 identity gate checks that the actual extracted file permissions are executable.

MaqaronyPad 0.3.4: the active release gate uses `check-0.3.4-rebrand.py` and the 0.3.4 UI-ordering copies, preserving the complete inherited static/security/Markdown action checks while referring to restored `source_editor.py` and `preview.py` modules. Historical `check-0.3.1-`, `check-0.3.2-` and `check-0.3.3-` scripts remain unmodified and are not applicable to the new source layout; they document the Mwpyn implementation of their respective releases. No historical checks were deleted or rewritten.

MaqaronyPad 1.0.0-x1.1: based on 0.3.4, the editor widget extraction preserves the restored source_editor.py / preview.py layout. New active release-specific QA scripts and x1 source fingerprints verify the relocated definitions; 0.3.4 checks remain immutable historical records.
