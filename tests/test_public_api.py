from __future__ import annotations

import ast
from importlib.metadata import version
from pathlib import Path

import tw_quant_core


PUBLIC_NAMESPACES = (
    "tw_quant_core",
    "tw_quant_core.events",
    "tw_quant_core.market",
    "tw_quant_core.strategy",
    "tw_quant_core.broker",
    "tw_quant_core.execution",
    "tw_quant_core.risk",
    "tw_quant_core.backtest",
    "tw_quant_core.replay",
    "tw_quant_core.paper",
)


def test_distribution_version_is_exposed() -> None:
    assert tw_quant_core.__version__ == version("tw-quant-core")


def test_documented_namespaces_have_explicit_exports() -> None:
    for namespace in PUBLIC_NAMESPACES:
        module = __import__(namespace, fromlist=["__all__"])
        assert module.__all__, f"{namespace} must declare its public API"
        for exported_name in module.__all__:
            assert hasattr(module, exported_name), f"missing {namespace}.{exported_name}"


def test_core_does_not_import_private_or_production_packages() -> None:
    package_root = Path(tw_quant_core.__file__).parent
    forbidden_roots = {"tw_quant", "shioaji"}
    for source_file in package_root.rglob("*.py"):
        tree = ast.parse(source_file.read_text(encoding="utf-8"), source_file.as_posix())
        for node in ast.walk(tree):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported = [node.module]
            assert not forbidden_roots.intersection(
                name.split(".", 1)[0] for name in imported
            ), f"forbidden dependency in {source_file}: {imported}"
