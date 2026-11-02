#!/usr/bin/env python3
"""x12.1 bounded cleanup: no obsolete documentation, canonical Windows location and README protection."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
OUTER=ROOT.parent
VERSION='1.0.0-x13.0'
ORIG='1.0.0-x12.0'
def sha(b): return hashlib.sha256(b).hexdigest()
assert not (ROOT/'OFFICIAL_SOURCE.md').exists(), 'obsolete provenance file remains'
assert not (ROOT/'windows').exists(), 'old Windows build folder remains'
WIN=ROOT/'packaging'/'windows'
assert WIN.is_dir()
for name in ('README.md','build-requirements.txt','build-windows-portable.ps1','windows-version-info.txt'):
    assert (WIN/name).is_file(), f'missing Windows file: {name}'
builder=(WIN/'build-windows-portable.ps1').read_text(encoding='utf-8')
assert "..\\.." in builder, 'builder root path not updated'
assert VERSION in builder
assert sha((OUTER/'README.md').read_bytes().replace(VERSION.encode(),ORIG.encode()))=='fa4c46b1e3a9e547a6c4f19f001a4cbe1855295e00e59d72b380a63aa642890f', 'public GitHub README altered beyond current version'
# x12.6 adds a new current-release preface; retain x12.5 and prior bytes verbatim.
inner=(ROOT/'README.md').read_bytes()
inner=inner[inner.index(b'# MaqaronyPad 1.0.0-x12.5'):]
assert sha(inner.replace(b'1.0.0-x12.5',ORIG.encode()))=='6ab4cf3794a91a4a8b87148789f45b2f9b714d381ad0fe91b7751d414b8946c0', 'internal historical README altered'
manifest=(ROOT/'SOURCE_MANIFEST.sha256').read_text(encoding='utf-8')
assert 'OFFICIAL_SOURCE.md' not in manifest
assert '/windows/build-windows-portable.ps1' in manifest
assert "./maqarony_pad/windows/" not in manifest
# Pin all four Windows packaging files to their issued x12.0 contents,
# allowing only the approved version literal and application-root relocation.
BASELINE_WINDOWS = {'README.md': 'ec7d63d99dd039c301c877b0fd902606fdbe72664153e3a11bd509b4c9f4488e', 'build-requirements.txt': 'a256592bbd2fc0e43d9b4ff8058f8eb7f123f53604e4cbb5f356da7f960afe37', 'windows-version-info.txt': '02bd20aa2f2529ae5e9e97345bb5108c1a8fc87c4088e10c1b2ba764968284c3', 'build-windows-portable.ps1': 'd1006fce633a043d51c4c59351be31f29367b6ec9653d0da269395400b404b69'}
for name in BASELINE_WINDOWS:
    current=(WIN/name).read_bytes()
    if name in ('windows-version-info.txt','build-windows-portable.ps1'):
        current=current.replace(VERSION.encode(),ORIG.encode())
    if name=='build-windows-portable.ps1':
        current=current.replace(b'Join-Path $PSScriptRoot "..\\.."',b'Join-Path $PSScriptRoot ".."')
    assert sha(current)==BASELINE_WINDOWS[name], f'unapproved Windows file changes: {name}'
print('PASS: x12.1 Windows/provenance cleanup and README preservation')
