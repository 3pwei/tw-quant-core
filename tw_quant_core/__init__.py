"""Stable top-level API for the standalone quantitative trading core.

Domain-specific contracts are also available from the documented
``tw_quant_core.events``, ``market``, ``strategy``, ``broker``, ``execution``,
and ``risk`` namespaces. Undocumented implementation modules are internal.
"""

from importlib.metadata import PackageNotFoundError, version

from .strategy import (
    CompositeAnalysisRequest,
    CompositeEvaluationRequest,
    CompositeMember,
    CompositeStrategy,
    Decision,
    DiagnosticRecord,
    ParameterField,
    ParameterKind,
    ParameterNormalizationRequest,
    ParameterNormalizationResult,
    ParameterSchemaMetadata,
    ParameterTemplateRequest,
    ParameterTemplateResult,
    ParameterValidationResult,
    PluginArtifactIdentity,
    Strategy,
    StrategyAnalysisResult,
    StrategyCapability,
    StrategyCompositeAnalysisProvider,
    StrategyDescriptor,
    StrategyEvaluationRequest,
    StrategyEvaluationResult,
    StrategyIdentity,
    StrategyIntent,
    StrategyParameterNormalizationProvider,
    StrategyParameterTemplateProvider,
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
    "CompositeAnalysisRequest",
    "CompositeStrategy",
    "CompositeEvaluationRequest",
    "CompositeMember",
    "Decision",
    "DiagnosticRecord",
    "ParameterField",
    "ParameterKind",
    "ParameterNormalizationRequest",
    "ParameterNormalizationResult",
    "ParameterSchemaMetadata",
    "ParameterTemplateRequest",
    "ParameterTemplateResult",
    "ParameterValidationResult",
    "PluginArtifactIdentity",
    "Strategy",
    "StrategyAnalysisResult",
    "StrategyCapability",
    "StrategyCompositeAnalysisProvider",
    "StrategyDescriptor",
    "StrategyEvaluationRequest",
    "StrategyEvaluationResult",
    "StrategyIdentity",
    "StrategyIntent",
    "StrategyParameterNormalizationProvider",
    "StrategyParameterTemplateProvider",
    "StrategyPluginProvider",
    "StrategyReference",
    "StrategyRegistry",
    "StrategyRuntime",
    "__version__",
]
