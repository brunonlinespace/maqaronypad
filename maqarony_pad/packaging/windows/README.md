# Windows portable build

Run `build-windows-portable.ps1` from PowerShell on a Windows host with Python 3 available through the `py` launcher.

The builder creates an isolated virtual environment, installs PyQt6/PyInstaller there, builds an onedir portable application, and performs an exact `MaqaronyPad 0.3.2` version probe.
