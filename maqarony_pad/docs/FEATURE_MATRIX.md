# Markopad 0.2.10 feature matrix

## Document model

| Capability | 0.0.2 |
|---|---|
| Markdown source is authoritative | Yes |
| `.md`, `.markdown`, `.mdown`, `.mkd` | Yes |
| RTF/rich-document editing | No |
| Private Markopad rich snapshot | No |
| Legacy Ricopad envelope stripping | One-way import only |
| Source Only / Source + Preview / Preview Only | Yes |
| Read-only preview | Yes |

## Toolbar

| Capability | Modern | Classic |
|---|---|---|
| Icon-only commands | Yes | Yes |
| 52×52 buttons / 36×36 icons | Yes | Yes |
| Traditional neutral + teal icon family | Yes | Yes |
| Native overflow when narrow | Yes | Toolbar extension |
| Tab collapse/reveal | Yes | N/A |
| Customisable command selection | No | Yes |
| Settings command page | Yes | Yes — flat choices plus two policy flyouts |
| Normal Paragraph + Heading 1–6 | Dropdown | Optional individual actions |
| Editor Toolbar | One Modern/Classic/Customise flyout | Optional same Editor Toolbar flyout |
| App Drag-and-Drop | Two direct Settings choices | Optional one Active↔New Window toggle |

## Editor

Markdown-native bold/italic/strikethrough, headings, lists, task lists, Quote Block, indent/outdent, inline/fenced code, links, image references, tables, horizontal rules and date/time are supported. Symbols use the shared 40-item curated grid with More Symbols. Find/Replace remains the Markopad bottom panel with bounded inventory, X/Y navigation, gold matches and safe Replace/Replace All. Go To Line, line numbers, word wrap, Locked Mode, source/preview zoom and separate Source/Preview fonts are retained. Source Font preserves weight/italic; Preview Font optionally italicizes block quotations. Ctrl+/ toggles HTML comments and Insert toggles Insert/Overwrite mode.

## Lifecycle hardening

The active file is monitored with exact-content snapshots. External modification/deletion preserves the live buffer, Save requires an explicit conflict decision, clean-but-missing close is protected, and rename/delete re-check filesystem identity before destructive operations. Dirty Duplicate and External Editor workflows can use either the current live document or the last disk version without forcing an unconditional Save.
