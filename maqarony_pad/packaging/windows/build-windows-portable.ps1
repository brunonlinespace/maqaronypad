$ErrorActionPreference = "Stop"
$ProgramRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ProjectRoot = (Resolve-Path (Join-Path $ProgramRoot "..")).Path
$BuildRoot = Join-Path $ProgramRoot "build\windows"
$Venv = Join-Path $BuildRoot "venv"
$Dist = Join-Path $ProgramRoot "dist"
$Out = Join-Path $Dist "MaqaronyPad-1.0.2-windows-portable"
Remove-Item $BuildRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $Out -Recurse -Force -ErrorAction SilentlyContinue
New-Item $BuildRoot -ItemType Directory -Force | Out-Null
New-Item $Dist -ItemType Directory -Force | Out-Null
py -3 -m venv $Venv
$Python = Join-Path $Venv "Scripts\python.exe"
$Pyi = Join-Path $Venv "Scripts\pyinstaller.exe"
& $Python -m pip install --disable-pip-version-check -r (Join-Path $ProgramRoot "requirements.txt") -r (Join-Path $PSScriptRoot "build-requirements.txt")
& $Pyi --noconfirm --clean --windowed --onedir --name maqaronypad `
  --icon (Join-Path $ProgramRoot "assets\icons\maqaronypad.ico") `
  --distpath $Out --workpath (Join-Path $BuildRoot "work") --specpath $BuildRoot `
  --add-data "$(Join-Path $ProgramRoot 'assets');assets" `
  --add-data "$(Join-Path $ProgramRoot 'docs');docs" `
  --exclude-module PyQt6.QtPdf --exclude-module PyQt6.QtPdfWidgets `
  --exclude-module PyQt6.QtWebEngineCore --exclude-module PyQt6.QtWebEngineWidgets `
  (Join-Path $ProgramRoot "app.py")
$Exe = Join-Path $Out "maqaronypad\maqaronypad.exe"
$Version = & $Exe --version
if ($Version -ne "MaqaronyPad 1.0.2") { throw "Version probe failed: $Version" }
Write-Host "Portable build complete: $Out"
