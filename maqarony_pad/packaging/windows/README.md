# MaqaronyPad Windows portable build

This folder contains the PowerShell builder for the self-contained **MaqaronyPad Windows portable package**.

The builder uses the same project-root `README.md`, canonical `maqarony_pad/app.py`, runtime requirements, application assets, and version metadata as the source-portable and Linux builds.

## Requirements

Build on **Windows** with:

- Python 3 available through the `py` launcher;
- internet access when the isolated build environment needs to install Python build dependencies;
- PowerShell permission to run the build script.

The builder does not install MaqaronyPad system-wide.

## Running the builder

### From the repository root

Open PowerShell in the repository root.

If PowerShell blocks local scripts, allow scripts for the **current PowerShell process only**:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

Then run:

```powershell
.\maqarony_pad\packaging\windows\build-windows-portable.ps1
```

### From `maqarony_pad\packaging\windows`

If PowerShell is already open in the `maqarony_pad\packaging\windows` folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build-windows-portable.ps1
```

If your current PowerShell execution policy already allows the script to run, the `Set-ExecutionPolicy` command is not required.

## What the builder does

The builder:

1. creates a clean temporary Windows build workspace under `maqarony_pad\build\windows`;
2. creates an isolated Python virtual environment;
3. installs the MaqaronyPad runtime requirements and PyInstaller build requirements into that environment;
4. builds the Windows application with PyInstaller in `--windowed --onedir` mode;
5. embeds the MaqaronyPad icon and Windows version resource;
6. copies the PyInstaller onedir contents directly into the final portable folder, with no extra nested `maqaronypad` wrapper directory;
7. copies the current source-root `README.md` into the portable root;
8. validates the frozen `maqaronypad.exe` ProductVersion;
9. removes the temporary Windows build workspace after the build has completed successfully.

If the build fails before completion, PowerShell stops at the failing command.

## Outputs

Successful builds are written under:

```text
maqarony_pad\dist\
```

For MaqaronyPad 1.1.7, the expected portable folder is:

```text
MaqaronyPad-1.1.7-windows-portable\
    maqaronypad.exe
    README.md
    _internal\
```

The executable and supporting files live directly in the final portable folder; there is no additional `maqaronypad\` wrapper directory.

## What the builder does not do

The Windows builder does **not**:

- install MaqaronyPad into Windows;
- create file associations;
- create or modify MaqaronyPad registry entries;
- require a system-wide PyInstaller installation;
- reuse the host Python environment for the packaged application.

Build dependencies are installed only into the isolated virtual environment under the temporary Windows build workspace. That workspace is removed after a successful build.

## Troubleshooting

### PowerShell says running scripts is disabled

Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

and then run the builder again in the same PowerShell window.

### `py` is not found

Confirm that Python is installed and available through the Windows Python launcher:

```powershell
py -3 --version
```

The current MaqaronyPad builder expects the `py` launcher.

### The version probe fails

Do not treat a failed version probe as a successful release build. The builder validates the frozen executable through its embedded Windows `ProductVersion`; review the generated executable and version resource before rebuilding.

## Packaging model

The Windows release is a **portable onedir application**. Users can copy the completed folder and run `maqaronypad.exe` directly.

No installer is produced by this builder.
