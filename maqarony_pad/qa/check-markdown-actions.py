#!/usr/bin/env python3
"""Dependency-light regression tests for source Markdown line transformations."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / "widgets/mwpyn/editor_formatting.py").read_text(encoding="utf-8")
tree = ast.parse(source)


def nested_transform(method_name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            for child in node.body:
                if isinstance(child, ast.FunctionDef) and child.name == "transform":
                    module = ast.Module(body=[child], type_ignores=[])
                    ast.fix_missing_locations(module)
                    ns = {"re": re}
                    exec(compile(module, str(ROOT / "widgets/mwpyn/editor_formatting.py"), "exec"), ns)
                    return ns["transform"]
    raise AssertionError(f"transform not found for {method_name}")


bullet = nested_transform("toggle_bullet_list")
number = nested_transform("toggle_numbered_list")
task = nested_transform("toggle_task_list")

# Empty current lines must start a usable Markdown list immediately.
assert bullet([""]) == ["- "]
assert number([""]) == ["1. "]
assert task([""]) == ["- [ ] "]
# Preserve intentional indentation on an otherwise empty current line.
assert bullet(["    "]) == ["    - "]
assert number(["\t"]) == ["\t1. "]
assert task(["  "]) == ["  - [ ] "]

# Existing non-empty behavior remains toggle-like and deterministic.
assert bullet(["alpha", "beta"]) == ["- alpha", "- beta"]
assert bullet(["- alpha", "- beta"]) == ["alpha", "beta"]
assert number(["alpha", "beta"]) == ["1. alpha", "2. beta"]
assert number(["1. alpha", "2. beta"]) == ["alpha", "beta"]
assert task(["alpha"]) == ["- [ ] alpha"]
assert task(["- [ ] alpha"]) == ["alpha"]

print("MaqaronyPad Markdown action regression QA passed.")
