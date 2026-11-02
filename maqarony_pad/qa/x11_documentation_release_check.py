#!/usr/bin/env python3
"""x11.0 read-only release/history scope gate; original x10 hashes remain authoritative."""
from pathlib import Path
import hashlib, re, json, xml.etree.ElementTree as ET, base64
A=Path(__file__).resolve().parents[1]
P=A.parent
SHA={'docs/ARCHITECTURE.md': '5c4fe78dc2eb0d75ca8e823d4fcfb2d81dde8451fa3e8acfa8c8fd066c3f7e6a', 'docs/CHANGELOG.md': '16caf28a69bad20b416f0f1bd2c6ca710e6dae530f3d78e2d16f6df9e5520e0e', 'docs/RELEASE_NOTES.md': 'f5f913516682aa89a0cfa8ac5541d3ade3d1d7733de090f24f0b8931aee915f5', 'README.md': '48ec70e11d65f39bb17da77cd0197215c6104f1fe544cdb99a70c788e8825c07', 'document_io.py': 'f8cf3dfdd9eee7a1ded21d6d7ddabbe6b18f71d90265f37dc94d687c624d0aa7', 'SOURCE_MANIFEST.sha256': 'dfba40ed4fa229cc04a273b1388393cb83fcc5fc653d02c12054c6353a511cb5', 'qa/check-1.0.0-x8.0-preserved-ui-order.py': 'edb41a1e57b7d1903b7f3cde83a51859d11b907b0f791971979d7d2949ea6a7b', 'qa/check-1.0.0-x8.0-ui-corrective.py': 'edb41a1e57b7d1903b7f3cde83a51859d11b907b0f791971979d7d2949ea6a7b', 'qa/check-1.0.0-x8.0-rebrand.py': '3dc818b3648a04188ed9cec2dc4b074653df5dea0d2adb07a8635df14704081e'}
ROOT_SHA='96060a7ca3f7e0adfe3676bb2fd2e52984ca75479876bc71e3b2ddb6313dd282'
NOTICE=b'> **Historical attribution correction (1.0.0-x11.0):** The 0.2.10 shortcuts/Quick Tour correction was released as **Markopad 0.2.10**, not MaqaronyPad. The archived sentence immediately below is retained unchanged.\n\n'
OLD_RELEASES=base64.b64decode('ICAgIDxyZWxlYXNlIHZlcnNpb249IjEuMC4wLXgxMC4wIiBkYXRlPSIyMDI2LTEwLTE3Ij48ZGVzY3JpcHRpb24+PHA+Q29ycmVjdGVkIHN0YXJ0dXAtdGltZSBpbXBvcnQgYW5kIHRoZW1lLWhlbHBlciBiaW5kaW5nIG9yZGVyIGluIGV4dHJhY3RlZCBjb21tYW5kL2FwcGVhcmFuY2UgbW9kdWxlLCBhbmQgcmVzdG9yZWQgdGhlIGV4aXN0aW5nIERhdGUvVGltZSBjb21tYW5kcycgZGF0ZXRpbWUgaW1wb3J0OyBubyBjaGFuZ2VzIHRvIGVkaXRvciBvciBjb21tYW5kIG1ldGhvZCBib2RpZXMuPC9wPjwvZGVzY3JpcHRpb24+PC9yZWxlYXNlPgogICAgPHJlbGVhc2UgdmVyc2lvbj0iMS4wLjAteDUuMCIgZGF0ZT0iMjAyNi0xMC0xNyI+PGRlc2NyaXB0aW9uPjxwPkV4aXN0aW5nIFByaW50aW5nLCBQREYgYW5kIFByb3BlcnRpZXMgbWV0aG9kcyBleHRyYWN0ZWQgdW5jaGFuZ2VkOyBvYnNvbGV0ZSBzb3VyY2UgZWRpdG9yIGFuZCBwcmV2aWV3IGNvbXBhdGliaWxpdHkgZmlsZXMgcmVtb3ZlZC48L3A+PC9kZXNjcmlwdGlvbj48L3JlbGVhc2U+CiAgICA8cmVsZWFzZSB2ZXJzaW9uPSIxLjAuMC14NC4wIiBkYXRlPSIyMDI2LTEwLTE3Ij48ZGVzY3JpcHRpb24+PHA+U291cmNlLWVkaXRvciBpbnNlcnRpb24sIGNsaXBib2FyZCBhbmQgaW5wdXQgbWV0aG9kIGV4dHJhY3Rpb24gd2l0aG91dCBiZWhhdmlvdXIgY2hhbmdlcy48L3A+PC9kZXNjcmlwdGlvbj48L3JlbGVhc2U+PHJlbGVhc2UgdmVyc2lvbj0iMS4wLjAteDIuMCIgZGF0ZT0iMjAyNi0xMC0xNyIvPjxyZWxlYXNlIHZlcnNpb249IjAuMy40IiBkYXRlPSIyMDI2LTEwLTE2Ii8+').decode()
def digest(x): return hashlib.sha256(x).hexdigest()
# Historical documents must have PRECISE original contents as suffixes; no retrospective editing.
for name in ('docs/CHANGELOG.md','docs/RELEASE_NOTES.md'):
    data=(A/name).read_bytes()
    assert data.startswith(b'# MaqaronyPad 1.0.0-x13.0'), name
    # Previous releases may be preceded by later append-only entries.
    previous=data[data.index(b'# MaqaronyPad 1.0.0-x11.0'):]
    assert previous.startswith(b'# MaqaronyPad 1.0.0-x11.0'), name
    # Original pre-x11 historical content preserved as exact bytes.
    original=previous.split(b'---\n\n',1)[1]
    assert digest(original)==SHA[name], ('historical rewrite',name)
assert digest((A/'docs/ARCHITECTURE.md').read_bytes())==SHA['docs/ARCHITECTURE.md']
# x13.0: reconstruct historical document_io.py before checking its immutable x11 digest.
# This is the exact two-line Desk-authoritative permission restoration only.
added=b'            if hasattr(os, "fchmod"):\n                os.fchmod(descriptor, source_mode)\n'
current_io=(A/'document_io.py').read_bytes()
assert current_io.count(added)==1, 'x13 permission restoration missing/duplicated'
assert digest(current_io.replace(added,b''))==SHA['document_io.py'], 'document_io changed beyond the approved x13 restoration'
for name in ('qa/check-1.0.0-x8.0-preserved-ui-order.py','qa/check-1.0.0-x8.0-ui-corrective.py','qa/check-1.0.0-x8.0-rebrand.py'):
    assert digest((A/name).read_bytes().replace(b'app.py',b'maqarony_pad.py'))==SHA[name], ('historical QA rewritten beyond the canonical module path',name)
# GitHub historical attribution must remain unchanged; the corrective notice is separate.
root=(P/'README.md').read_bytes()
assert root.count(NOTICE)==1
normal=root.replace(NOTICE,b'').replace(b'1.0.0-x13.0',b'1.0.0-x10.0').replace(b'1.0.0-x11.0',b'1.0.0-x10.0')
assert digest(normal)==ROOT_SHA, 'original GitHub README text was rewritten'
assert b'Markopad 0.2.10' in NOTICE
# Existing old AppStream release XML strings remain EXACT, new entry prepended.
meta=(A/'packaging/appimage/io.github.brunonlinespace.maqaronypad.metainfo.xml').read_text()
assert '<release version="1.0.0-x11.0"' in meta
record=meta.split('  <releases>\n',1)[1].split('</releases>',1)[0]
assert record.endswith(OLD_RELEASES), 'older AppStream release entries rewritten'
ET.fromstring(meta)
assert '29 existing file-lifecycle methods' in meta
assert 'MaqaronyPad 1.0.0-x13.0 is' in (A/'docs/README.md').read_text()
internal=(A/'README.md').read_bytes()
assert internal.startswith(b'# MaqaronyPad 1.0.0-x13.0')
assert b'# MaqaronyPad 1.0.0-x11.0' in internal
base_internal=internal.split(b'## Preserved development history (verbatim below)\n\n',1)[1]
assert digest(base_internal)==SHA['README.md'], 'older internal README modified'
assert (A/'docs/CURRENT_ARCHITECTURE.md').is_file()
assert '.maqarony_pad-' in (A/'docs/CURRENT_ARCHITECTURE.md').read_text()
assert (A/'document_io.py').read_text().count('.maqarony_pad-')==2
assert not (A/'mwpyn').exists()
print('PASS x11: historical bytes/metadata preserved; current documentation and temp-prefix decisions recorded')
