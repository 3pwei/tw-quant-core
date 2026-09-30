"""Stable top-level API for the standalone quantitative trading core.

Domain-specific contracts are also available from the documented
``tw_quant_core.events``, ``market``, ``strategy``, ``broker``, ``execution``,
and ``risk`` namespaces. Undocumented implementation modules are internal.
"""

from importlib.metadata import PackageNotFoundError, version

from .strategy import (
    CompositeEvaluationRequest,
    CompositeMember,
    CompositeStrategy,
    Decision,
    DiagnosticRecord,
    ParameterField,
    ParameterKind,
    ParameterSchemaMetadata,
    ParameterValidationResult,
    PluginArtifactIdentity,
    Strategy,
    StrategyAnalysisResult,
    StrategyCapability,
    StrategyDescriptor,
    StrategyEvaluationRequest,
    StrategyEvaluationResult,
    StrategyIdentity,
    StrategyIntent,
    StrategyPluginProvider,
    StrategyReference,
    StrategyRegistry,
    StrategyRuntime,
)

try:
    __version__ = version("tw-quant-core")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0+unknown"

__all__ = [
    "CompositeStrategy",
    "CompositeEvaluationRequest",
    "CompositeMember",
    "Decision",
    "DiagnosticRecord",
    "ParameterField",
    "ParameterKind",
    "ParameterSchemaMetadata",
    "ParameterValidationResult",
    "PluginArtifactIdentity",
    "Strategy",
    "StrategyAnalysisResult",
    "StrategyCapability",
    "StrategyDescriptor",
    "StrategyEvaluationRequest",
    "StrategyEvaluationResult",
    "StrategyIdentity",
    "StrategyIntent",
    "StrategyPluginProvider",
    "StrategyReference",
    "StrategyRegistry",
    "StrategyRuntime",
    "__version__",
]
