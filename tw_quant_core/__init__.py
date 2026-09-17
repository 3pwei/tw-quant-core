"""Stable top-level API for the standalone quantitative trading core.

Domain-specific contracts are also available from the documented
``tw_quant_core.events``, ``market``, ``strategy``, ``broker``, ``execution``,
and ``risk`` namespaces. Undocumented implementation modules are internal.
"""

from importlib.metadata import PackageNotFoundError, version

from .strategy import CompositeStrategy, Decision, Strategy, StrategyRuntime

try:
    __version__ = version("tw-quant-core")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0+unknown"

__all__ = [
    "CompositeStrategy",
    "Decision",
    "Strategy",
    "StrategyRuntime",
    "__version__",
]
