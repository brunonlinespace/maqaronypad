# Known limitations — 0.2.10

- Preview is deliberately read-only; there is no WYSIWYG-to-Markdown reconstruction path.
- Source/Preview scroll synchronisation is not yet implemented.
- Spell checking is not bundled in 0.0.2.
- Complex Markdown dialect extensions may render according to Qt's supported Markdown subset.
- Remote preview resources are intentionally not fetched automatically.

- Bold, Italic, Strikethrough and Inline Code currently use partial delimiter toggling rather than a fully Markdown-aware formatting-state model (Audit Item 31, parked for later experimental work).
- Raw HTML embedded in Markdown can destabilize the Qt Preview rendering for some GitHub-style README content (Audit Item 33, open).
