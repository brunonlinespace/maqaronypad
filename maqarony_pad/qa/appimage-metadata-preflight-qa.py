#!/usr/bin/env python3
"""Validate actual Fedora builder metadata checks and AppDir assembly.

No PyQt6, Fedora toolchain, network access or PyInstaller is needed. This gate
executes the exact functions used by the builder and rejects mutated metadata.
"""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
builder = root / 'packaging/fedora/build-appimage.sh'
payload = root / 'packaging/appimage'
source = builder.read_text(encoding='utf8')
assert 'validate_desktop_entry_basic "$APPIMAGE_PAYLOAD/maqaronypad.desktop"' in source.split('check_inputs(){', 1)[1].split('run_release_qa(){', 1)[0]
assert 'validate_appstream_basic "$APPIMAGE_PAYLOAD/${APPSTREAM_ID}.metainfo.xml"' in source.split('check_inputs(){', 1)[1].split('run_release_qa(){', 1)[0]
assert 'validate_appstream_basic "$APPDIR/usr/share/metainfo/${APPSTREAM_ID}.metainfo.xml"' in source

env = dict(os.environ)
env['MAQARONY_PAD_ALLOW_ROOT_BUILD'] = '1'
env['MAQARONY_PAD_ALLOW_UNSUPPORTED_HOST'] = '1'
env['PYTHONDONTWRITEBYTECODE'] = '1'

def invoke(script, *args, must_pass=True):
    result = subprocess.run(['bash', '-c', script, 'qa', str(builder), *(str(x) for x in args)],
                            capture_output=True, text=True, env=env, timeout=30)
    if must_pass:
        assert result.returncode == 0, (script, result.stdout, result.stderr)
    else:
        assert result.returncode != 0, (script, 'negative case incorrectly passed', result.stdout)
    return result

# The real unmodified source preflight, not a second Python XML validator.
preflight = 'source "$1"; OS_ID=fedora; FEDORA_RELEASE=44; check_inputs'
invoke(preflight)
with tempfile.TemporaryDirectory(prefix='maqapad-builder-metadata-') as d:
    work = Path(d)
    fixture = work/'appimage'
    fixture.mkdir()
    shutil.copy2(payload/'maqaronypad.desktop',fixture/'maqaronypad.desktop')
    meta_name = 'io.github.brunonlinespace.maqaronypad.metainfo.xml'
    shutil.copy2(payload/meta_name,fixture/meta_name)
    checks = 'source "$1"; OS_ID=fedora; FEDORA_RELEASE=44; APPIMAGE_PAYLOAD="$2"; check_inputs'
    invoke(checks,fixture)

    # The original x17.8 regression: current version absent from release history.
    metadata = fixture/meta_name
    good = metadata.read_text(encoding='utf8')
    assert '<release version="1.0.2"' in good
    metadata.write_text(good.replace('<release version="1.0.2"',
                                     '<release version="1.0.2-absent"', 1), encoding='utf8')
    invoke(checks,fixture,must_pass=False)
    metadata.write_text(good,encoding='utf8')
    # Reproduce the exact Fedora failure: final 1.0.0 followed by x17.10.
    # This historically passed the weak `current version exists` check.
    bad_order=good.replace('<release version="1.0.0"',
        '<release version="1.0.0-x17.10"',1)
    metadata.write_text(bad_order,encoding='utf8')
    invoke(checks,fixture,must_pass=False)
    # Also catch a pure descending-order violation between valid final releases.
    bad_order=good.replace('<release version="1.0.0"',
        '<release version="0.2.0"',1)
    metadata.write_text(bad_order,encoding='utf8')
    invoke(checks,fixture,must_pass=False)
    metadata.write_text(good,encoding='utf8')
    desktop = fixture/'maqaronypad.desktop'
    valid_desktop = desktop.read_text(encoding='utf8')
    desktop.write_text(valid_desktop.replace('MimeType=text/markdown;', 'MimeType=text/plain;',1),encoding='utf8')
    invoke(checks,fixture,must_pass=False)
    desktop.write_text(valid_desktop,encoding='utf8')

    # The builder must honor native appstreamcli's warning/error status early.
    # Use a deliberately failing tool on hosts without appstreamcli, ensuring
    # the preflight cannot silently ignore its result.
    native=work/'bin'
    native.mkdir()
    verifier=native/'appstreamcli'
    verifier.write_text('#!/bin/sh\nexit 23\n',encoding='utf8')
    verifier.chmod(0o755)
    overridden=dict(env)
    overridden['PATH']=str(native)+os.pathsep+env.get('PATH','')
    probe=subprocess.run(['bash','-c',checks,'qa',str(builder),str(fixture)],
                         capture_output=True,text=True,env=overridden,timeout=30)
    assert probe.returncode != 0 and 'AppStream metadata validation failed before freezing' in probe.stderr, (probe.stdout,probe.stderr)

    # Run the real assembler with a harmless dummy PyInstaller onedir payload.
    # This exercises installation paths and the post-copy validators.
    fake_dist = work/'pyi-dist'/'maqaronypad'
    fake_dist.mkdir(parents=True)
    executable = fake_dist/'maqaronypad'
    executable.write_text('#!/bin/sh\nexit 0\n',encoding='utf8')
    executable.chmod(0o755)
    appdir=work/'AppDir'
    assemble = 'source "$1"; APPDIR="$2"; PYI_DIST="$3"; assemble_appdir'
    invoke(assemble,appdir,work/'pyi-dist')
    assert (appdir/'usr/share/metainfo'/meta_name).read_bytes() == (payload/meta_name).read_bytes()
    assert (appdir/'usr/share/applications/maqaronypad.desktop').read_bytes() == (payload/'maqaronypad.desktop').read_bytes()
    assert (appdir/'AppRun').is_file()

print('PASS 1.0.2 actual builder metadata preflight, AppStream negative-order cases, native-validator failure and AppDir assembly')
