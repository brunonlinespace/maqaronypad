#!/usr/bin/env python3
"""Original MaqaronyPad platform/resources and startup helpers (x9.0)."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

def program_dir() -> Path:
    return Path(__file__).resolve().parent

def project_root() -> Path:
    return program_dir().parent

def asset_path(*parts: str) -> Path:
    return program_dir().joinpath("assets", *parts)

def application_icon() -> QIcon:
    for candidate in (
        asset_path("icons", "maqaronypad.png"),
        asset_path("hicolor", "256x256", "apps", "maqaronypad.png"),
    ):
        if candidate.is_file():
            return QIcon(str(candidate))
    return QIcon()

def host_process_environment() -> dict[str, str]:
    """Return a clean host environment for external character-map utilities."""
    environment = os.environ.copy()
    if sys.platform == "win32":
        return environment
    if not (environment.get("APPDIR") or getattr(sys, "frozen", False)):
        return environment
    appdir = environment.get("APPDIR")
    original_library_path = environment.pop("LD_LIBRARY_PATH_ORIG", None)
    if original_library_path is None:
        environment.pop("LD_LIBRARY_PATH", None)
    else:
        environment["LD_LIBRARY_PATH"] = original_library_path
    for variable in (
        "APPDIR", "APPIMAGE", "QT_PLUGIN_PATH", "QT_QPA_PLATFORM",
        "QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_PLATFORMTHEME",
        "QT_STYLE_OVERRIDE", "QML_IMPORT_PATH", "QML2_IMPORT_PATH",
    ):
        environment.pop(variable, None)
    if appdir and environment.get("PATH"):
        appdir_real = os.path.realpath(appdir)
        clean_path: list[str] = []
        for entry in environment["PATH"].split(os.pathsep):
            if not entry:
                continue
            try:
                entry_real = os.path.realpath(entry)
                inside = os.path.commonpath((appdir_real, entry_real)) == appdir_real
            except (OSError, ValueError):
                inside = False
            if not inside:
                clean_path.append(entry)
        environment["PATH"] = os.pathsep.join(clean_path)
    return environment


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog=APP_ID, add_help=True)
    parser.add_argument("path", nargs="?")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--theme", choices=["system", "dark", "light"])
    parser.add_argument("--maqaronypad-smoke-test", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    if args.version:
        print(f"{APP_NAME} {APP_VERSION}")
        return 0
    app = QApplication(sys.argv[:1])
    app.setApplicationName(APP_NAME); app.setApplicationDisplayName(APP_NAME); app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName(APP_ORG); app.setOrganizationDomain(ORGANIZATION_DOMAIN); app.setDesktopFileName(DESKTOP_ID); app.setWindowIcon(application_icon())
    settings = load_json_settings(); theme = args.theme or str(settings.get("theme", "light")); apply_theme(app, theme)
    if args.maqaronypad_smoke_test: return smoke_test(theme)
    window = MaqaronyPadWindow(args.path, theme_override=args.theme)
    window.show()
    return app.exec()
