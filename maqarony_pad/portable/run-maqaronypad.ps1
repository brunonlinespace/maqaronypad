$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
python (Join-Path $Root "main.py") @args
