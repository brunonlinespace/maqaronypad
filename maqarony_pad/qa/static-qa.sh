#!/usr/bin/env bash
set -Eeuo pipefail
python3 "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/github-readme-lock-qa.py"
python3 "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/halcyon-family-qa.py"
python3 "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/halcyon-dark-import-qa.py"
python3 "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/appimage-metadata-preflight-qa.py"
python3 "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)/appimage-smoke-version-qa.py"
export PYTHONDONTWRITEBYTECODE=1
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
PROJECT="$(cd -- "$ROOT/.." && pwd -P)"
fail(){ echo "QA failure: $*" >&2; exit 1; }

echo "==> Compiling Python source"
[[ -f "$ROOT/widgets/mwpyn/editor_lifecycle.py" && -f "$ROOT/editor_platform_startup.py" && -f "$ROOT/widgets/mwpyn/editor_widgets.py" && -f "$ROOT/widgets/mwpyn/editor_search_view.py" && -f "$ROOT/widgets/window_search_view.py" && -f "$ROOT/widgets/mwpyn/editor_printing.py" && -f "$ROOT/widgets/mwpyn/editor_preferences.py" ]] || fail "extracted editor widget module missing"
python3 -m py_compile "$PROJECT/main.py" "$ROOT/app.py" "$ROOT/widgets/keyboard_shortcuts.py" "$ROOT/widgets/about_dialog.py" "$ROOT/widgets/quick_tour.py" "$ROOT/widgets/mwpyn/editor_source.py" "$ROOT/widgets/mwpyn/editor_widgets.py" "$ROOT/widgets/mwpyn/character_count.py" "$ROOT/widgets/mwpyn/editor_formatting.py" "$ROOT/widgets/mwpyn/editor_insertion.py" "$ROOT/widgets/mwpyn/editor_search_view.py" "$ROOT/widgets/window_search_view.py" "$ROOT/widgets/mwpyn/editor_printing.py" "$ROOT/widgets/mwpyn/editor_preferences.py" "$ROOT/widgets/editor_commands_appearance.py" "$ROOT/widgets/mwpyn/editor_lifecycle.py" "$ROOT/editor_platform_startup.py" "$ROOT/document_io.py" "$ROOT/widgets/mwpyn/editor_preview.py" "$ROOT/legacy_ricopad.py" "$ROOT/settings_io.py"
rm -rf "$PROJECT/__pycache__" "$ROOT/__pycache__"

echo "==> Checking canonical four-item outer tree"
mapfile -t outer < <(find "$PROJECT" -mindepth 1 -maxdepth 1 -printf '%f\n' | LC_ALL=C sort)
[[ "${outer[*]}" == "README.md main.py maqarony_pad suite-pythoine-component.json" ]] || fail "outer tree must contain README.md, main.py, maqarony_pad/, and suite-pythoine-component.json (found: ${outer[*]})"

echo "==> Verifying source manifest"
(cd "$PROJECT" && sha256sum -c maqarony_pad/SOURCE_MANIFEST.sha256 >/dev/null) || fail "source manifest verification failed"

echo "==> Checking Suite component manifest"
python3 - "$PROJECT/suite-pythoine-component.json" <<'PY'
import json, sys
from pathlib import Path
data=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
expected={
 'id':'maqaronypad','name':'MaqaronyPad','component_kind':'editor','version':'1.1.7',
 'portable_command':['main.py'],'extensions':['.md','.markdown','.mdown','.mkd'],
 'desktop_id':'maqaronypad','publisher_id':'brunonlinespace',
 'tagline':'Friendly. Fast. Focused.',
 'capabilities':{'routing':True,'open':True,'create':True},
}
for k,v in expected.items():
    assert data.get(k)==v, (k,data.get(k),v)
PY

echo "==> Checking Markdown-only format surface"
python3 "$ROOT/qa/markdown-only-surface-qa.py" "$PROJECT"
python3 "$ROOT/qa/x1710-markdown-scope-qa.py"
grep -Fq 'SUPPORTED_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}' "$ROOT/document_io.py" || fail "Markdown extension set changed"
grep -Fq 'MimeType=text/markdown;' "$ROOT/assets/maqaronypad.desktop" || fail "desktop MIME is not Markdown-only"

echo "==> Checking source-authoritative save invariant"
grep -Fq 'safe_atomic_save(' "$ROOT/widgets/mwpyn/editor_lifecycle.py" || fail "normal Save is not source-authoritative"
if grep -nE 'toMarkdown\(\).*(atomic_save|safe_atomic_save)|(atomic_save|safe_atomic_save)\([^\n]*preview' "$ROOT/widgets/mwpyn/editor_lifecycle.py"; then fail "preview/rich reconstruction leaked into save path"; fi
grep -Fq 'self.setReadOnly(True)' "$ROOT/widgets/mwpyn/editor_preview.py" || fail "preview is not explicitly read-only"
grep -Fq 'if scheme in {"http", "https", "ftp", "data"}' "$ROOT/widgets/mwpyn/editor_preview.py" || fail "remote preview resource block missing"

echo "==> Checking safety bounds"
grep -Fq 'MAX_PASTE_CHARACTERS = 5_000_000' "$ROOT/widgets/mwpyn/editor_source.py" || fail "paste bound changed"
grep -Fq 'MAX_DOCUMENT_CHARACTERS = 25_000_000' "$ROOT/widgets/mwpyn/editor_source.py" || fail "source document bound changed"
grep -Fq 'MAX_SEARCH_MATCHES = 10_000' "$ROOT/app.py" || fail "search cap changed"

echo "==> Checking branding/version"
grep -Fq 'APP_NAME = "MaqaronyPad"' "$ROOT/app.py" || fail "application name mismatch"
grep -Fq 'APP_VERSION = "1.1.7"' "$ROOT/app.py" || fail "application version mismatch"
grep -Fq 'APP_TAGLINE = "Friendly. Fast. Focused."' "$ROOT/app.py" || fail "Pad-family slogan mismatch"
grep -Fq 'value, _kind = winreg.QueryValueEx(key, "AppsUseLightTheme")' "$ROOT/app.py" || fail "Windows System theme detection missing"
grep -Fq 'hints.setColorScheme(Qt.ColorScheme.Dark if resolved == "dark" else Qt.ColorScheme.Light)' "$ROOT/app.py" || fail "Windows System native colour-scheme correction missing"
grep -Fq 'palette.setColor(QPalette.ColorRole.Window, QColor("#D4D4D4"))' "$ROOT/app.py" || fail "MaqaronyPad 1.0.2 Light palette not restored"
grep -Fq 'palette.setColor(QPalette.ColorRole.WindowText, QColor("#2A2A2A"))' "$ROOT/app.py" || fail "MaqaronyPad Light text colour not restored"
grep -Fq 'palette.setColor(QPalette.ColorRole.Window, QColor("#202326"))' "$ROOT/app.py" || fail "MaqaronyPad 1.0.2 Dark palette not restored"
grep -Fq 'palette.setColor(QPalette.ColorRole.WindowText, QColor("#F1F3F4"))' "$ROOT/app.py" || fail "MaqaronyPad Dark text colour not restored"
grep -Fq 'palette.setColor(QPalette.ColorRole.Accent, QColor("#0B8781"))' "$ROOT/app.py" || fail "Light-theme MaqaronyPad teal Accent missing"
grep -Fq 'palette.setColor(QPalette.ColorRole.Accent, QColor("#158B86"))' "$ROOT/app.py" || fail "Dark-theme MaqaronyPad teal Accent missing"
if grep -Fq '_shell_stylesheet' "$ROOT/app.py"; then fail "global shell stylesheet must not override native toolbar geometry"; fi
if grep -Fq 'app.setStyleSheet(_shell_stylesheet' "$ROOT/app.py"; then fail "application-wide theme stylesheet must not override native toolbar geometry"; fi
grep -Fq 'class AppearanceThemeGuard(QObject):' "$ROOT/app.py" || fail "runtime explicit-theme guard missing"
grep -Fq 'hints.colorSchemeChanged.connect(self._system_scheme_changed)' "$ROOT/app.py" || fail "runtime theme guard is not listening for host colour-scheme changes"
grep -Fq 'self._restore_timer = QTimer(self)' "$ROOT/app.py" || fail "runtime theme guard owned timer missing"
grep -Fq 'self._restore_timer.timeout.connect(self._restore)' "$ROOT/app.py" || fail "runtime theme guard timer is not connected"
grep -Fq 'app.aboutToQuit.connect(self.shutdown)' "$ROOT/app.py" || fail "runtime theme guard shutdown hook missing"
grep -Fq 'app.removeEventFilter(self)' "$ROOT/app.py" || fail "runtime theme guard does not detach application event filter"
grep -Fq 'colorSchemeChanged.disconnect(self._system_scheme_changed)' "$ROOT/app.py" || fail "runtime theme guard does not disconnect host colour-scheme signal"
grep -Fq 'self._window_ref = weakref.ref(window)' "$ROOT/app.py" || fail "runtime theme guard still strongly retains window"
grep -Fq 'if selected != "system" and not force and _theme_palette_matches(app, selected):' "$ROOT/app.py" || fail "runtime theme guard must refresh System while preserving explicit themes"
if grep -A60 -F 'class AppearanceThemeGuard(QObject):' "$ROOT/app.py" | grep -Fq 'if selected == "system":'; then fail "runtime theme guard still suppresses System refresh"; fi
grep -Fq 'apply_theme(app, selected)' "$ROOT/app.py" || fail "runtime theme guard does not reapply selected theme"
grep -Fq 'self._appearance_theme_guard = AppearanceThemeGuard(self)' "$ROOT/app.py" || fail "runtime theme guard is not installed"
grep -Fq 'self.settings.get("editor_font_size", 11)' "$ROOT/widgets/window_search_view.py" || fail "Source default is not 11 pt"
grep -Fq 'font.setPointSizeF(11.0)' "$ROOT/widgets/editor_commands_appearance.py" || fail "Preview default is not 11 pt"
[[ -f "$ROOT/assets/icons/maqaronypad.png" ]] || fail "canonical logo missing"

echo "==> Checking toolbar identity"
[[ -d "$ROOT/assets/toolbar-icons/light" && -d "$ROOT/assets/toolbar-icons/dark" ]] || fail "toolbar icon schemes missing"
[[ ! -d "$ROOT/assets/ribbon-icons" ]] || fail "obsolete ribbon-icons directory remains"
grep -Fq 'self.toolbar_menu = view.addMenu("Editor Toolbar")' "$ROOT/widgets/editor_commands_appearance.py" || fail "Toolbar menu rename missing"
if grep -Fq 'self._action("Button Labels"' "$ROOT/app.py"; then fail "Button Labels action remains"; fi

echo "==> Checking retained list/menu/AppImage overflow fixes"
grep -Fq 'return [lines[0] + "- "]' "$ROOT/widgets/mwpyn/editor_formatting.py" || fail "empty-line bullet-list insertion fix missing"
grep -Fq 'return [lines[0] + "1. "]' "$ROOT/widgets/mwpyn/editor_formatting.py" || fail "empty-line numbered-list insertion fix missing"
grep -Fq 'return [lines[0] + "- [ ] "]' "$ROOT/widgets/mwpyn/editor_formatting.py" || fail "empty-line task-list insertion fix missing"
grep -Fq 'return bool(os.environ.get("APPIMAGE"))' "$ROOT/widgets/editor_ribbon_retro.py" || fail "AppImage runtime guard missing"
grep -Fq 'toolbar.findChild(QToolButton, "qt_toolbar_ext_button")' "$ROOT/widgets/editor_ribbon_retro.py" || fail "AppImage overflow extension lookup missing"
grep -Fq 'extension.setText("›")' "$ROOT/widgets/editor_ribbon_retro.py" || fail "visible AppImage overflow chevron missing"
grep -Fq 'self.menuBar().setVisible(classic or appmenu_only)' "$ROOT/widgets/editor_ribbon_retro.py" || fail "Modern/Classic/AppMenu-only local AppMenu visibility contract missing"
grep -Fq 'self.appmenu_only_mode_action = self._action("Disabled (AppMenu only)"' "$ROOT/widgets/editor_commands_appearance.py" || fail "Disabled AppMenu-only mode missing"
grep -Fq 'clear_button = QPushButton("Clear All", dialog)' "$ROOT/widgets/editor_ribbon_retro.py" || fail "Classic Clear All control missing"
grep -Fq 'self.classic_toolbar.addAction(self.customize_classic_action)' "$ROOT/widgets/editor_ribbon_retro.py" || fail "persistent Classic Settings control missing"
grep -Fq '$PyInstallerDist = Join-Path $BuildRoot "pyinstaller-dist"' "$ROOT/packaging/windows/build-windows-portable.ps1" || fail "Windows temporary PyInstaller dist missing"
grep -Fq '$Exe = Join-Path $Out "maqaronypad.exe"' "$ROOT/packaging/windows/build-windows-portable.ps1" || fail "Windows portable output is still nested"
grep -Fq 'Remove-Item $BuildRoot -Recurse -Force -ErrorAction SilentlyContinue' "$ROOT/packaging/windows/build-windows-portable.ps1" || fail "Windows build cleanup missing"
grep -Fq 'doc = documentation_path()' "$ROOT/app.py" || fail "Documentation does not use source-root README resolver"
grep -Fq '$BuiltVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($Exe).ProductVersion' "$ROOT/packaging/windows/build-windows-portable.ps1" || fail "Windows GUI-safe version probe missing"

echo "==> Checking x1.1 editor widget source identity"
python3 "$ROOT/qa/x1_editor_widgets_check.py"

echo "==> Running dependency-light security/fidelity QA"
python3 "$ROOT/qa/security-qa.py"
# Historical x14.2/x14.3 checks remain unmodified in the source archive;
# their exact old method hashes and version strings are edition-specific.
printf "SKIP: archived x14.2/x14.3 gates (superseded by the scoped x14.5 gate)\n"
# x14.4 gate is archived (its exact pre-change counter expectation no longer applies).
python3 "$ROOT/qa/x170-toolbar-icons-qa.py"
python3 "$ROOT/qa/x171-toolbar-menu-icons-qa.py"
python3 "$ROOT/qa/x172-exit-toolbar-qa.py"
# x17.3 version-pinned tour test is historical; its runtime construction contract
# remains exercised separately by the current-family regression test.
python3 "$ROOT/qa/x174-icon-families-qa.py"
python3 "$ROOT/qa/x178-frozen-status-qa.py"
python3 "$ROOT/qa/x130-permission-fallback-qa.py"
echo "MaqaronyPad 1.1.7 static QA passed."
