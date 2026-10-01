from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Mapping, Sequence

import pytest

from tw_quant_core.market import KBar
from tw_quant_core.strategy import (
    CompositeAnalysisRequest,
    CompositeEvaluationRequest,
    CompositeMember,
    DiagnosticRecord,
    ParameterNormalizationRequest,
    ParameterNormalizationResult,
    ParameterSchemaMetadata,
    ParameterTemplateRequest,
    ParameterTemplateResult,
    ParameterValidationResult,
    PluginArtifactIdentity,
    StrategyAnalysisResult,
    StrategyCapability,
    StrategyCapabilityError,
    StrategyCompositeAnalysisProvider,
    StrategyDescriptor,
    StrategyEvaluationRequest,
    StrategyEvaluationResult,
    StrategyIdentity,
    StrategyIntent,
    StrategyParameterError,
    StrategyParameterNormalizationProvider,
    StrategyParameterTemplateProvider,
    StrategyPluginContractError,
    StrategyPluginProvider,
    StrategyReference,
    StrategyRegistry,
    UnknownPluginError,
)


def _plugin(version: str = "1.0.0") -> PluginArtifactIdentity:
    return PluginArtifactIdentity(
        plugin_id="capability-test-plugin",
        plugin_version=version,
        artifact_name="capability-test-plugin",
        artifact_version=version,
        artifact_digest=f"sha256:{version.replace('.', '')}",
    )


def _reference(plugin: PluginArtifactIdentity | None = None) -> StrategyReference:
    return StrategyReference(
        plugin or _plugin(),
        StrategyIdentity("inert-capability-test", "1"),
    )


def _bars() -> tuple[KBar, ...]:
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return (
        KBar(
            symbol="SYNTH",
            contract="SYNTH-01",
            time=timestamp,
            open=100,
            high=101,
            low=99,
            close=100,
            volume=1,
            status="closed",
            session="day",
            trading_date=timestamp.date(),
            first_tick_time=timestamp,
            last_tick_time=timestamp,
            exchange_time=timestamp,
            received_time=timestamp,
            latency_ms=0,
        ),
    )


def _descriptor(
    identity: PluginArtifactIdentity,
    capabilities: frozenset[StrategyCapability],
) -> StrategyDescriptor:
    return StrategyDescriptor(
        reference=_reference(identity),
        display_name="Inert capability test provider",
        parameter_schema=ParameterSchemaMetadata("1"),
        capabilities=capabilities,
    )


V11_CAPABILITIES = frozenset(
    {
        StrategyCapability.EVALUATE,
        StrategyCapability.ANALYZE,
        StrategyCapability.COMPOSITE_EVALUATE,
    }
)


class V11ScriptedProvider:
    """A provider implementing only the contract published in Core v1.1."""

    def __init__(
        self,
        identity: PluginArtifactIdentity | None = None,
        capabilities: frozenset[StrategyCapability] = V11_CAPABILITIES,
    ) -> None:
        self._identity = identity or _plugin()
        self._descriptor = _descriptor(self._identity, capabilities)

    @property
    def identity(self) -> PluginArtifactIdentity:
        return self._identity

    def descriptors(self) -> Sequence[StrategyDescriptor]:
        return (self._descriptor,)

    def validate_parameters(
        self,
        reference: StrategyReference,
        parameter_schema_version: str,
        parameters: Mapping[str, object],
    ) -> ParameterValidationResult:
        del reference, parameter_schema_version
        if parameters in (
            {"enabled": True},
            {"enabled": True, "settings": {"levels": (1, 2)}},
        ):
            return ParameterValidationResult(True)
        return ParameterValidationResult(False, ("parameters are not canonical",))

    def evaluate(self, request: StrategyEvaluationRequest) -> StrategyEvaluationResult:
        return StrategyEvaluationResult(
            request.reference,
            (StrategyIntent("hold", "inert test response"),),
        )

    def analyze(self, request: StrategyEvaluationRequest) -> StrategyAnalysisResult:
        return StrategyAnalysisResult(
            request.reference,
            (DiagnosticRecord("inert", "1", {"points": ()}),),
        )

    def evaluate_composite(
        self,
        request: CompositeEvaluationRequest,
    ) -> StrategyEvaluationResult:
        return StrategyEvaluationResult(
            request.evaluator,
            (StrategyIntent("hold", "inert composite response"),),
        )


class OptionalCapabilityProvider(V11ScriptedProvider):
    def __init__(self) -> None:
        super().__init__(
            capabilities=V11_CAPABILITIES
            | {
                StrategyCapability.NORMALIZE_PARAMETERS,
                StrategyCapability.PARAMETER_TEMPLATE,
                StrategyCapability.COMPOSITE_ANALYZE,
            }
        )
        self.normalization_reference = self._descriptor.reference
        self.normalization_schema = "1"
        self.normalization_supplied_parameters: Mapping[str, object] | None = None
        self.template_reference = self._descriptor.reference
        self.template_schema = "1"
        self.analysis_reference = self._descriptor.reference

    def normalize_parameters(
        self,
        request: ParameterNormalizationRequest,
    ) -> ParameterNormalizationResult:
        return ParameterNormalizationResult(
            self.normalization_reference,
            self.normalization_schema,
            self.normalization_supplied_parameters or request.supplied_parameters,
            {"enabled": True, "settings": {"levels": [1, 2]}},
        )

    def parameter_template(
        self,
        request: ParameterTemplateRequest,
    ) -> ParameterTemplateResult:
        return ParameterTemplateResult(
            self.template_reference,
            self.template_schema,
            {"enabled": True, "settings": {"levels": [1, 2]}},
        )

    def analyze_composite(
        self,
        request: CompositeAnalysisRequest,
    ) -> StrategyAnalysisResult:
        return StrategyAnalysisResult(
            self.analysis_reference,
            (DiagnosticRecord("composite", "1", {"member_ids": ("member-a",)}),),
        )


def _registry(provider: V11ScriptedProvider) -> StrategyRegistry:
    registry = StrategyRegistry()
    registry.register(provider)
    registry.freeze()
    return registry


def _evaluation_request(reference: StrategyReference) -> StrategyEvaluationRequest:
    return StrategyEvaluationRequest(reference, "1", {"enabled": True}, _bars())


def _composite_request(
    reference: StrategyReference,
    *,
    member_schema: str = "1",
) -> CompositeAnalysisRequest:
    return CompositeAnalysisRequest(
        evaluator=reference,
        evaluator_parameter_schema_version="1",
        evaluator_parameters={"enabled": True},
        composite_id="inert-composite",
        composite_version=1,
        members=(
            CompositeMember(
                "member-a",
                reference,
                member_schema,
                {"enabled": True},
            ),
        ),
        bars=_bars(),
    )


def test_v11_provider_remains_compatible_and_old_behaviors_are_unchanged() -> None:
    provider = V11ScriptedProvider()
    registry = _registry(provider)
    reference = provider.descriptors()[0].reference
    request = _evaluation_request(reference)

    assert isinstance(provider, StrategyPluginProvider)
    assert not isinstance(provider, StrategyParameterNormalizationProvider)
    assert not isinstance(provider, StrategyParameterTemplateProvider)
    assert not isinstance(provider, StrategyCompositeAnalysisProvider)
    assert registry.evaluate(request).reference == reference
    assert registry.analyze(request).reference == reference
    assert (
        registry.evaluate_composite(
            CompositeEvaluationRequest(
                evaluator=reference,
                evaluator_parameter_schema_version="1",
                evaluator_parameters={"enabled": True},
                composite_id="inert-composite",
                composite_version=1,
                members=(
                    CompositeMember("member-a", reference, "1", {"enabled": True}),
                ),
                bars=_bars(),
            )
        ).reference
        == reference
    )


def test_optional_capabilities_return_exact_immutable_provider_payloads() -> None:
    provider = OptionalCapabilityProvider()
    registry = _registry(provider)
    reference = provider.descriptors()[0].reference
    supplied: dict[str, object] = {"on": True, "nested": {"aliases": ["on"]}}

    normalization_request = ParameterNormalizationRequest(reference, "1", supplied)
    supplied["on"] = False
    nested = supplied["nested"]
    assert isinstance(nested, dict)
    nested["aliases"] = []
    normalized = registry.normalize_parameters(normalization_request)
    template = registry.parameter_template(ParameterTemplateRequest(reference, "1"))
    analysis = registry.analyze_composite(_composite_request(reference))

    assert normalization_request.supplied_parameters == {
        "on": True,
        "nested": {"aliases": ("on",)},
    }
    assert normalized.normalized_parameters == {
        "enabled": True,
        "settings": {"levels": (1, 2)},
    }
    assert template.template_parameters == normalized.normalized_parameters
    assert analysis.reference == reference
    assert analysis.diagnostics[0].diagnostic_id == "composite"

    with pytest.raises(TypeError):
        normalized.normalized_parameters["enabled"] = False  # type: ignore[index]
    settings = normalized.normalized_parameters["settings"]
    assert isinstance(settings, Mapping)
    with pytest.raises(TypeError):
        settings["levels"] = ()  # type: ignore[index]
    with pytest.raises(TypeError):
        template.template_parameters["enabled"] = False  # type: ignore[index]


@pytest.mark.parametrize(
    ("call", "capability"),
    (
        (
            lambda registry, reference: registry.normalize_parameters(
                ParameterNormalizationRequest(reference, "1", {"on": True})
            ),
            StrategyCapability.NORMALIZE_PARAMETERS,
        ),
        (
            lambda registry, reference: registry.parameter_template(
                ParameterTemplateRequest(reference, "1")
            ),
            StrategyCapability.PARAMETER_TEMPLATE,
        ),
        (
            lambda registry, reference: registry.analyze_composite(
                _composite_request(reference)
            ),
            StrategyCapability.COMPOSITE_ANALYZE,
        ),
    ),
)
def test_unadvertised_optional_capabilities_fail_closed(call, capability) -> None:
    provider = V11ScriptedProvider()
    registry = _registry(provider)
    reference = provider.descriptors()[0].reference

    with pytest.raises(StrategyCapabilityError, match=capability.value):
        call(registry, reference)


def test_advertised_capability_without_optional_port_fails_closed() -> None:
    provider = V11ScriptedProvider(
        capabilities=V11_CAPABILITIES | {StrategyCapability.NORMALIZE_PARAMETERS}
    )
    registry = _registry(provider)
    reference = provider.descriptors()[0].reference

    with pytest.raises(StrategyPluginContractError, match="optional port"):
        registry.normalize_parameters(
            ParameterNormalizationRequest(reference, "1", {"on": True})
        )


def test_optional_requests_require_exact_plugin_artifact_strategy_and_schema() -> None:
    provider = OptionalCapabilityProvider()
    registry = _registry(provider)
    reference = provider.descriptors()[0].reference

    unknown_plugin = replace(reference.plugin, plugin_version="2.0.0")
    with pytest.raises(UnknownPluginError):
        registry.normalize_parameters(
            ParameterNormalizationRequest(_reference(unknown_plugin), "1", {})
        )

    altered_artifact = replace(reference.plugin, artifact_digest="sha256:different")
    with pytest.raises(UnknownPluginError):
        registry.parameter_template(
            ParameterTemplateRequest(_reference(altered_artifact), "1")
        )

    with pytest.raises(StrategyParameterError, match="schema"):
        registry.normalize_parameters(
            ParameterNormalizationRequest(reference, "2", {})
        )

    with pytest.raises(StrategyParameterError, match="schema"):
        registry.analyze_composite(_composite_request(reference, member_schema="2"))


@pytest.mark.parametrize(
    "mismatch",
    (
        "normalization-reference",
        "normalization-schema",
        "normalization-supplied",
        "template-reference",
        "template-schema",
    ),
)
def test_normalization_and_template_result_identity_mismatches_fail_closed(
    mismatch: str,
) -> None:
    provider = OptionalCapabilityProvider()
    registry = _registry(provider)
    reference = provider.descriptors()[0].reference

    if mismatch == "normalization-reference":
        provider.normalization_reference = replace(
            reference,
            strategy=StrategyIdentity("unexpected", "1"),
        )
    elif mismatch == "normalization-schema":
        provider.normalization_schema = "2"
    elif mismatch == "normalization-supplied":
        provider.normalization_supplied_parameters = {"different": True}
    elif mismatch == "template-reference":
        provider.template_reference = replace(
            reference,
            strategy=StrategyIdentity("unexpected", "1"),
        )
    else:
        provider.template_schema = "2"

    with pytest.raises(StrategyPluginContractError, match="identity"):
        if mismatch.startswith("normalization"):
            registry.normalize_parameters(
                ParameterNormalizationRequest(reference, "1", {"on": True})
            )
        else:
            registry.parameter_template(ParameterTemplateRequest(reference, "1"))


def test_composite_analysis_result_identity_mismatch_fails_closed() -> None:
    provider = OptionalCapabilityProvider()
    registry = _registry(provider)
    reference = provider.descriptors()[0].reference
    provider.analysis_reference = replace(
        reference,
        strategy=StrategyIdentity("unexpected", "1"),
    )

    with pytest.raises(StrategyPluginContractError, match="identity"):
        registry.analyze_composite(_composite_request(reference))
