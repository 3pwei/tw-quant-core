from __future__ import annotations

from typing import Mapping, Protocol, Sequence, runtime_checkable

from .contracts import (
    CompositeAnalysisRequest,
    CompositeEvaluationRequest,
    ParameterNormalizationRequest,
    ParameterNormalizationResult,
    ParameterTemplateRequest,
    ParameterTemplateResult,
    ParameterValidationResult,
    PluginArtifactIdentity,
    StrategyAnalysisResult,
    StrategyDescriptor,
    StrategyEvaluationRequest,
    StrategyEvaluationResult,
    StrategyReference,
)


@runtime_checkable
class StrategyPluginProvider(Protocol):
    """Injected provider implemented by a separately distributed plugin.

    Discovery, installation, allowlisting and artifact verification are Platform
    responsibilities. Core only validates exact identities and result envelopes.
    """

    @property
    def identity(self) -> PluginArtifactIdentity: ...

    def descriptors(self) -> Sequence[StrategyDescriptor]: ...

    def validate_parameters(
        self,
        reference: StrategyReference,
        parameter_schema_version: str,
        parameters: Mapping[str, object],
    ) -> ParameterValidationResult: ...

    def evaluate(self, request: StrategyEvaluationRequest) -> StrategyEvaluationResult: ...

    def analyze(self, request: StrategyEvaluationRequest) -> StrategyAnalysisResult: ...

    def evaluate_composite(
        self,
        request: CompositeEvaluationRequest,
    ) -> StrategyEvaluationResult: ...


@runtime_checkable
class StrategyParameterNormalizationProvider(StrategyPluginProvider, Protocol):
    """Optional port for provider-owned parameter canonicalization."""

    def normalize_parameters(
        self,
        request: ParameterNormalizationRequest,
    ) -> ParameterNormalizationResult: ...


@runtime_checkable
class StrategyParameterTemplateProvider(StrategyPluginProvider, Protocol):
    """Optional port for provider-owned runtime configuration templates."""

    def parameter_template(
        self,
        request: ParameterTemplateRequest,
    ) -> ParameterTemplateResult: ...


@runtime_checkable
class StrategyCompositeAnalysisProvider(StrategyPluginProvider, Protocol):
    """Optional port for provider-owned composite analysis semantics."""

    def analyze_composite(
        self,
        request: CompositeAnalysisRequest,
    ) -> StrategyAnalysisResult: ...
