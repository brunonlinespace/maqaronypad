# Packaging

- `fedora/build-appimage.sh` — non-privileged Fedora 43/44 AppImage builder.
- `fedora/test-appimage.sh` — FUSE-independent finished-AppImage version/theme probes.
- `pyinstaller/build-requirements.txt` — isolated build dependencies.
- `appimage/` — desktop/AppStream/AppRun payload.

The Fedora builder never installs host packages or invokes privilege elevation. Python build dependencies are installed only into the isolated build virtual environment.

`appimagetool` is resolved without host-package installation in this order: an explicit `APPIMAGETOOL_PATH` (or legacy `APPIMAGETOOL`) override, an existing host `appimagetool` command, or a private user-cache copy downloaded over HTTPS from the official AppImage continuous release. The downloaded executable is bounded to 200 MiB, checked for ELF identity, stored beneath `${XDG_CACHE_HOME:-~/.cache}/maqarony_pad-appimage-tools`, and can be SHA-256 pinned with `APPIMAGETOOL_SHA256`. `MAQARONY_PAD_RELEASE_BUILD=1` requires that SHA-256 pin.
