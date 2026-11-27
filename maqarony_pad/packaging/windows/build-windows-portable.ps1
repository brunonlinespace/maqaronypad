$ErrorActionPreference = "Stop"
$Version = "1.1.7"
$ProgramRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ProjectRoot = (Resolve-Path (Join-Path $ProgramRoot "..")).Path
$BuildRoot = Join-Path $ProgramRoot "build\windows"
$Venv = Join-Path $BuildRoot "venv"
$Dist = Join-Path $ProgramRoot "dist"
$PyInstallerDist = Join-Path $BuildRoot "pyinstaller-dist"
$Out = Join-Path $Dist "MaqaronyPad-$Version-windows-portable"
Remove-Item $BuildRoot -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $Out -Recurse -Force -ErrorAction SilentlyContinue
New-Item $BuildRoot -ItemType Directory -Force | Out-Null
New-Item $Dist -ItemType Directory -Force | Out-Null
py -3 -m venv $Venv
$Python = Join-Path $Venv "Scripts\python.exe"
$Pyi = Join-Path $Venv "Scripts\pyinstaller.exe"
$VersionInfo = Join-Path $PSScriptRoot "windows-version-info.txt"
& $Python -m pip install --disable-pip-version-check -r (Join-Path $ProgramRoot "requirements.txt") -r (Join-Path $PSScriptRoot "build-requirements.txt")
& $Pyi --noconfirm --clean --windowed --onedir --name maqaronypad `
  --icon (Join-Path $ProgramRoot "assets\icons\maqaronypad.ico") `
  --version-file $VersionInfo `
  --distpath $PyInstallerDist --workpath (Join-Path $BuildRoot "work") --specpath $BuildRoot `
  --add-data "$(Join-Path $ProgramRoot 'assets');assets" `
  --add-data "$(Join-Path $ProgramRoot 'docs');docs" `
  --exclude-module PyQt6.QtPdf --exclude-module PyQt6.QtPdfWidgets `
  --exclude-module PyQt6.QtWebEngineCore --exclude-module PyQt6.QtWebEngineWidgets `
  (Join-Path $ProgramRoot "app.py")
$PyInstallerPackage = Join-Path $PyInstallerDist "maqaronypad"
New-Item $Out -ItemType Directory -Force | Out-Null
Copy-Item -Path (Join-Path $PyInstallerPackage "*") -Destination $Out -Recurse -Force
$Exe = Join-Path $Out "maqaronypad.exe"
Copy-Item -LiteralPath (Join-Path $ProjectRoot "README.md") -Destination (Join-Path $Out "README.md") -Force
$BuiltVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($Exe).ProductVersion
if ($BuiltVersion -ne $Version) { throw "Version probe failed: $BuiltVersion" }
Remove-Item $BuildRoot -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Portable build complete: $Out"
