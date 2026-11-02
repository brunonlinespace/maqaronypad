#!/usr/bin/env python3
"""Historical regression-check source view, reconstructed from *real* dialog modules.

This is QA-only: the production app.py remains slim and imports real bound functions.
The new x12.5 identity gate independently verifies every binding and method body.
"""
from __future__ import annotations
import ast
import textwrap
from pathlib import Path

METHOD_MODULES = [('quick_tour', 'show_quick_tour'), ('keyboard_shortcuts', '_shortcut_catalog'), ('keyboard_shortcuts', 'show_shortcuts'), ('about_dialog', 'show_about')]
CLASS_NAME = 'MaqaronyPadWindow'


def contract_text(root: Path) -> str:
    root = Path(root)
    source = (root/'app.py').read_text(encoding='utf-8')
    marker = 'class ' + CLASS_NAME + '('
    assert marker in source, 'application class was lost'
    pos = source.index('    def __init__(', source.index(marker))
    methods = []
    for module, name in METHOD_MODULES:
        path = root/'widgets'/f'{module}.py'
        text = path.read_text(encoding='utf-8')
        tree = ast.parse(text)
        matches = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
        assert len(matches) == 1, f'missing/multiple relocated method: {name}'
        methods.append(textwrap.indent(ast.get_source_segment(text, matches[0]) or '', '    '))
    return source[:pos] + chr(10).join(methods) + chr(10) + source[pos:]
