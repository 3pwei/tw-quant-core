from __future__ import annotations

from types import MappingProxyType
from typing import Mapping

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
    StrategyCapability,
    StrategyDescriptor,
    StrategyEvaluationRequest,
    StrategyEvaluationResult,
    StrategyReference,
)
from .plugins import (
    StrategyCompositeAnalysisProvider,
    StrategyParameterNormalizationProvider,
    StrategyParameterTemplateProvider,
    StrategyPluginProvider,
)


class StrategyRegistryError(RuntimeError):
    """Base class for fail-closed registry errors."""


class UnknownPluginError(StrategyRegistryError):
    pass


class UnknownStrategyError(StrategyRegistryError):
    pass


class StrategyCapabilityError(StrategyRegistryError):
    pass


class StrategyParameterError(StrategyRegistryError):
    pass


class StrategyPluginContractError(StrategyRegistryError):
    pass


class StrategyRegistry:
    """Exact-version registry assembled by the Platform composition root."""

    def __init__(self) -> None:
        self._providers: dict[PluginArtifactIdentity, StrategyPluginProvider] = {}
        self._descriptors: dict[StrategyReference, StrategyDescriptor] = {}
        self._frozen = False

    @property
    def providers(self) -> Mapping[PluginArtifactIdentity, StrategyPluginProvider]:
        return MappingProxyType(self._providers)

    @property
    def descriptors(self) -> Mapping[StrategyReference, StrategyDescriptor]:
        return MappingProxyType(self._descriptors)

    def register(self, provider: StrategyPluginProvider) -> None:
        if self._frozen:
            raise RuntimeError("strategy registry is frozen")
        identity = provider.identity
        if identity in self._providers:
            raise ValueError(f"duplicate strategy plugin registration: {identity}")

        descriptors = tuple(provider.descriptors())
        if not descriptors:
            raise ValueError("strategy plugins must register at least one descriptor")
        references: set[StrategyReference] = set()
        for descriptor in descriptors:
            if descriptor.reference.plugin != identity:
                raise ValueError("strategy descriptor plugin identity does not match provider")
            if descriptor.reference in references or descriptor.reference in self._descriptors:
                raise ValueError(
                    f"duplicate strategy descriptor: {descriptor.reference}"
                )
            references.add(descriptor.reference)

        self._providers[identity] = provider
        self._descriptors.update(
            (descriptor.reference, descriptor) for descriptor in descriptors
        )

    def freeze(self) -> None:
        self._frozen = True

    def provider(self, identity: PluginArtifactIdentity) -> StrategyPluginProvider:
        try:
            return self._providers[identity]
        except KeyError as exc:
            raise UnknownPluginError(
                f"unknown strategy plugin artifact or version: {identity}"
            ) from exc

    def descriptor(self, reference: StrategyReference) -> StrategyDescriptor:
        self.provider(reference.plugin)
        try:
            return self._descriptors[reference]
        except KeyError as exc:
            raise UnknownStrategyError(
                f"unknown strategy or strategy version: {reference.strategy}"
            ) from exc

    def evaluate(self, request: StrategyEvaluationRequest) -> StrategyEvaluationResult:
        descriptor = self._prepare(
            request.reference,
            request.parameter_schema_version,
            request.parameters,
            StrategyCapability.EVALUATE,
        )
        result = self.provider(descriptor.reference.plugin).evaluate(request)
        self._require_matching_result(request.reference, result)
        return result

    def analyze(self, request: StrategyEvaluationRequest) -> StrategyAnalysisResult:
        descriptor = self._prepare(
            request.reference,
            request.parameter_schema_version,
            request.parameters,
            StrategyCapability.ANALYZE,
        )
        result = self.provider(descriptor.reference.plugin).analyze(request)
        if result.reference != request.reference:
            raise StrategyPluginContractError(
                "analysis result identity does not match the request"
            )
        return result

    def evaluate_composite(
        self,
        request: CompositeEvaluationRequest,
    ) -> StrategyEvaluationResult:
        descriptor = self._prepare(
            request.evaluator,
            request.evaluator_parameter_schema_version,
            request.evaluator_parameters,
            StrategyCapability.COMPOSITE_EVALUATE,
        )
        for member in request.members:
            self._prepare(
                member.strategy,
                member.parameter_schema_version,
                member.parameters,
                StrategyCapability.EVALUATE,
            )
        result = self.provider(descriptor.reference.plugin).evaluate_composite(request)
        self._require_matching_result(request.evaluator, result)
        return result

    def normalize_parameters(
        self,
        request: ParameterNormalizationRequest,
    ) -> ParameterNormalizationResult:
        descriptor = self._require_capability(
            request.reference,
            request.parameter_schema_version,
            StrategyCapability.NORMALIZE_PARAMETERS,
        )
        provider = self.provider(descriptor.reference.plugin)
        if not isinstance(provider, StrategyParameterNormalizationProvider):
            raise StrategyPluginContractError(
                "provider advertises parameter normalization without its optional port"
            )
        result = provider.normalize_parameters(request)
        if not isinstance(result, ParameterNormalizationResult):
            raise StrategyPluginContractError(
                "parameter normalizer returned an invalid result contract"
            )
        if (
            result.reference != request.reference
            or result.parameter_schema_version != request.parameter_schema_version
            or result.supplied_parameters != request.supplied_parameters
        ):
            raise StrategyPluginContractError(
                "parameter normalization result identity does not match the request"
            )
        self._validate_parameters(
            result.reference,
            result.parameter_schema_version,
            result.normalized_parameters,
        )
        return result

    def parameter_template(
        self,
        request: ParameterTemplateRequest,
    ) -> ParameterTemplateResult:
        descriptor = self._require_capability(
            request.reference,
            request.parameter_schema_version,
            StrategyCapability.PARAMETER_TEMPLATE,
        )
        provider = self.provider(descriptor.reference.plugin)
        if not isinstance(provider, StrategyParameterTemplateProvider):
            raise StrategyPluginContractError(
                "provider advertises a parameter template without its optional port"
            )
        result = provider.parameter_template(request)
        if not isinstance(result, ParameterTemplateResult):
            raise StrategyPluginContractError(
                "parameter template provider returned an invalid result contract"
            )
        if (
            result.reference != request.reference
            or result.parameter_schema_version != request.parameter_schema_version
        ):
            raise StrategyPluginContractError(
                "parameter template result identity does not match the request"
            )
        self._validate_parameters(
            result.reference,
            result.parameter_schema_version,
            result.template_parameters,
        )
        return result

    def analyze_composite(
        self,
        request: CompositeAnalysisRequest,
    ) -> StrategyAnalysisResult:
        descriptor = self._prepare(
            request.evaluator,
            request.evaluator_parameter_schema_version,
            request.evaluator_parameters,
            StrategyCapability.COMPOSITE_ANALYZE,
        )
        for member in request.members:
            self._require_schema(
                member.strategy,
                member.parameter_schema_version,
            )
            self._validate_parameters(
                member.strategy,
                member.parameter_schema_version,
                member.parameters,
            )
        provider = self.provider(descriptor.reference.plugin)
        if not isinstance(provider, StrategyCompositeAnalysisProvider):
            raise StrategyPluginContractError(
                "provider advertises composite analysis without its optional port"
            )
        result = provider.analyze_composite(request)
        if not isinstance(result, StrategyAnalysisResult):
            raise StrategyPluginContractError(
                "composite analyzer returned an invalid result contract"
            )
        if result.reference != request.evaluator:
            raise StrategyPluginContractError(
                "composite analysis result identity does not match the request"
            )
        return result

    def _prepare(
        self,
        reference: StrategyReference,
        parameter_schema_version: str,
        parameters: Mapping[str, object],
        capability: StrategyCapability,
    ) -> StrategyDescriptor:
        descriptor = self._require_capability(
            reference,
            parameter_schema_version,
            capability,
        )
        self._validate_parameters(reference, parameter_schema_version, parameters)
        return descriptor

    def _require_schema(
        self,
        reference: StrategyReference,
        parameter_schema_version: str,
    ) -> StrategyDescriptor:
        descriptor = self.descriptor(reference)
        if descriptor.parameter_schema.schema_version != parameter_schema_version:
            raise StrategyParameterError(
                "unknown parameter schema version for exact strategy reference"
            )
        return descriptor

    def _require_capability(
        self,
        reference: StrategyReference,
        parameter_schema_version: str,
        capability: StrategyCapability,
    ) -> StrategyDescriptor:
        descriptor = self._require_schema(reference, parameter_schema_version)
        if capability not in descriptor.capabilities:
            raise StrategyCapabilityError(
                f"strategy capability is unavailable: {capability.value}"
            )
        return descriptor

    def _validate_parameters(
        self,
        reference: StrategyReference,
        parameter_schema_version: str,
        parameters: Mapping[str, object],
    ) -> None:
        validation = self.provider(reference.plugin).validate_parameters(
            reference,
            parameter_schema_version,
            parameters,
        )
        if not isinstance(validation, ParameterValidationResult):
            raise StrategyPluginContractError(
                "parameter validator returned an invalid result contract"
            )
        if not validation.valid:
            raise StrategyParameterError("; ".join(validation.errors))

    @staticmethod
    def _require_matching_result(
        reference: StrategyReference,
        result: StrategyEvaluationResult,
    ) -> None:
        if result.reference != reference:
            raise StrategyPluginContractError(
                "evaluation result identity does not match the request"
            )
