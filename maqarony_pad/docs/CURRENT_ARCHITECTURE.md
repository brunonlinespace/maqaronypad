# Current architecture — MaqaronyPad 1.0.0-x12.2

This document describes the existing x10 extracted architecture as carried forward unchanged into x11.0. `ARCHITECTURE.md` remains the historical **Markopad 0.2.10** source account and must not be retrospectively rewritten. Older x4 import/shim discussions there describe earlier development states, not current runtime requirements.

## Source-authoritative Markdown flow

```text
Markdown file -> document_io.py -> MarkopadSourceEditor (editor_source.py)
                                        | 
                                        v
                                MarkdownPreview (editor_preview.py)
                                [read-only rendered preview]
```

The document's Markdown source text remains authoritative. Saving uses `document_io.py`; preview is not a serialization input. There is no RTF codec in this application.

## Existing runtime modules

- `maqarony_pad.py`: application identity, Qt window class (`MaqaronyPadWindow`), command coordination and startup bindings.
- `editor_platform_startup.py`: the pre-existing extracted resource, argument and entry-point helpers.
- `editor_source.py`: `MarkopadSourceEditor`; source editing with existing `editor_search_view.py`, `editor_insertion.py` and `editor_formatting.py` mixins.
- `editor_widgets.py`: syntax highlighting and line-number widgets.
- `editor_preview.py`: `MarkdownPreview`, the read-only Qt rendering surface.
- `editor_lifecycle.py`: existing main-window document/file-lifecycle methods extracted at x10, with no algorithm changes.
- `window_search_view.py`: main-window search/view interaction.
- `editor_printing.py`: print/PDF and related methods.
- `editor_preferences.py`: preference handling.
- `editor_ribbon_retro.py`: Tabbed/Classic toolbar presentation.
- `editor_commands_appearance.py`: existing commands, icon handling and appearance orchestration.
- `document_io.py`: bounded and atomic Markdown I/O with the existing external-change protections.
- `settings_io.py`: preferences helper; `legacy_ricopad.py`: narrow existing compatibility helper.

## Version-history and temporary-file note

The **Markopad 0.2.10** architecture is a historical snapshot, not an up-to-date module inventory. The source editor and preview were later relocated during the approved x1–x10 refactor; their existing implementations and behavior were preserved.

The temporary-save/create prefix in `document_io.py` is still `.maqarony_pad-` (previously `.markopad-` in Markopad 0.2.10). The prefix is an internal transient filename convention, not a document format or a public identity. This release deliberately does **not** restore the old prefix or change file I/O logic. No new compatibility semantics are asserted.

## Preservation boundary

x11.0 changes only documentation, current release identity metadata, relevant version-sensitive QA, and the source checksum manifest. It does not change the implementation of editor mixins, document I/O, file monitoring, preview or Ribbon icons.
