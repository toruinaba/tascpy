"""analytics.functional の約束: numpy と標準ライブラリだけに依存し、単体で使える"""

import ast
import sys
from pathlib import Path

import tascpy.analytics.functional as functional

ALLOWED_THIRD_PARTY = {"numpy"}


def _imported_roots(path: Path) -> set[str]:
    roots = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_functional_imports_only_numpy_and_stdlib():
    root = Path(functional.__file__).parent
    for path in root.rglob("*.py"):
        third_party = _imported_roots(path) - set(sys.stdlib_module_names)
        assert third_party <= ALLOWED_THIRD_PARTY, f"{path.relative_to(root)} imports {third_party}"


def test_functional_has_no_relative_imports_outside_package():
    root = Path(functional.__file__).parent
    for path in root.rglob("*.py"):
        depth = len(path.relative_to(root).parts) - 1
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.level:
                assert node.level <= depth + 1, f"{path.relative_to(root)} imports outside functional"
