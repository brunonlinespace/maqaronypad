# Format support

## Supported editing formats

- `.md`
- `.markdown`
- `.mdown`
- `.mkd`

All are treated as ordinary Markdown text.

Markopad intentionally does not expose a generic plain-text compatibility mode. Unsupported file types are rejected rather than silently opened under a different document model.

## Markdown dialect

The source remains unconstrained plain Markdown. Rendering uses Qt's built-in Markdown support, so preview presentation may not reproduce every extension from every external Markdown dialect. Unsupported syntax remains untouched in source and can still be saved faithfully.

## Application metadata

New Markopad files contain no private Markopad payload. A small one-way compatibility recognizer can remove historical Ricopad rich-envelope metadata from an older Markdown file after informing the user.
