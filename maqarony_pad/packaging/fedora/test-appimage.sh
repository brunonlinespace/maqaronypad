#!/usr/bin/env bash
set -Eeuo pipefail
APPIMAGE="${1:-}"
[[ -f "$APPIMAGE" ]] || { echo "Usage: $0 MaqaronyPad-1.0.2-ARCH.AppImage" >&2; exit 2; }
[[ -x "$APPIMAGE" ]] || chmod +x "$APPIMAGE"
ROOT="$(mktemp -d)"
trap 'rm -rf "$ROOT"' EXIT
mkdir -p "$ROOT/home/.config" "$ROOT/home/.cache" "$ROOT/home/.local/share" "$ROOT/home/Documents"
COMMON_ENV=(
  HOME="$ROOT/home"
  XDG_CONFIG_HOME="$ROOT/home/.config"
  XDG_CACHE_HOME="$ROOT/home/.cache"
  XDG_DATA_HOME="$ROOT/home/.local/share"
  QT_QPA_PLATFORM=offscreen
  QT_QUICK_BACKEND=software
)
actual="$(env "${COMMON_ENV[@]}" "$APPIMAGE" --appimage-extract-and-run --version)"
[[ "$actual" == "MaqaronyPad 1.0.2" ]] || { echo "Version probe mismatch: $actual" >&2; exit 1; }
for theme in system dark light; do
  timeout 30s env "${COMMON_ENV[@]}" "$APPIMAGE" --appimage-extract-and-run --theme "$theme" --maqaronypad-smoke-test
done
echo "MaqaronyPad AppImage startup, theme and all-four-icon-family action probes passed."
