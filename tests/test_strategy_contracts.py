from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

import pytest

from tw_quant_core.market import KBar
from tw_quant_core.strategy import (
    CompositeEvaluationRequest,
    CompositeMember,
    CompositeStrategy,
    DiagnosticRecord,
    MovingAverageCross,
    ParameterField,
    ParameterKind,
    ParameterSchemaMetadata,
    ParameterValidationResult,
    PluginArtifactIdentity,
    StrategyAnalysisResult,
    StrategyCapability,
    StrategyCapabilityError,
    StrategyDescriptor,
    StrategyEvaluationRequest,
    StrategyEvaluationResult,
    StrategyIdentity,
    StrategyIntent,
    StrategyParameterError,
    StrategyPluginContractError,
    StrategyReference,
    StrategyRegistry,
    UnknownPluginError,
    UnknownStrategyError,
)


def _plugin(version: str = "1.0.0") -> PluginArtifactIdentity:
    return PluginArtifactIdentity(
        plugin_id="scripted-test-plugin",
        plugin_version=version,
        artifact_name="scripted-test-plugin",
        artifact_version=version,
        artifact_digest=f"sha256:{version.replace('.', '')}",
    )


def _reference(
    *,
    plugin: PluginArtifactIdentity | None = None,
    strategy_id: str = "scripted",
    strategy_version: str = "1",
) -> StrategyReference:
    return StrategyReference(
        plugin=plugin or _plugin(),
        strategy=StrategyIdentity(strategy_id, strategy_version),
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


class ScriptedProvider:
    """Inert contract double; it contains no market or trading rule."""

    def __init__(
        self,
        identity: PluginArtifactIdentity | None = None,
        descriptors: Sequence[StrategyDescriptor] | None = None,
    ) -> None:
        self._identity = identity or _plugin()
        self._descriptors = tuple(descriptors or (self._descriptor(),))
        self.next_intent = StrategyIntent("hold", "scripted response")
        self.return_reference: StrategyReference | None = None

    @property
    def identity(self) -> PluginArtifactIdentity:
        return self._identity

    def _descriptor(self) -> StrategyDescriptor:
        return StrategyDescriptor(
            reference=_reference(plugin=self._identity),
            display_name="Scripted test provider",
            parameter_schema=ParameterSchemaMetadata(
                "1",
                (ParameterField("enabled", ParameterKind.BOOLEAN),),
            ),
            capabilities=frozenset(
                {
                    StrategyCapability.EVALUATE,
                    StrategyCapability.ANALYZE,
                    StrategyCapability.COMPOSITE_EVALUATE,
                }
            ),
        )

    def descriptors(self) -> Sequence[StrategyDescriptor]:
        return self._descriptors

    def validate_parameters(
        self,
        reference: StrategyReference,
        parameter_schema_version: str,
        parameters: Mapping[str, object],
    ) -> ParameterValidationResult:
        del reference, parameter_schema_version
        if parameters == {"enabled": True}:
            return ParameterValidationResult(True)
        return ParameterValidationResult(False, ("enabled must be true",))

    def evaluate(self, request: StrategyEvaluationRequest) -> StrategyEvaluationResult:
        return StrategyEvaluationResult(
            self.return_reference or request.reference,
            (self.next_intent,),
        )

    def analyze(self, request: StrategyEvaluationRequest) -> StrategyAnalysisResult:
        return StrategyAnalysisResult(
            self.return_reference or request.reference,
            (DiagnosticRecord("scripted", "1", {"points": ()}),),
        )

    def evaluate_composite(
        self,
        request: CompositeEvaluationRequest,
    ) -> StrategyEvaluationResult:
        return StrategyEvaluationResult(
            self.return_reference or request.evaluator,
            (self.next_intent,),
        )


def _registry(provider: ScriptedProvider | None = None) -> tuple[StrategyRegistry, ScriptedProvider]:
    provider = provider or ScriptedProvider()
    registry = StrategyRegistry()
    registry.register(provider)
    registry.freeze()
    return registry, provider


def _request(reference: StrategyReference | None = None) -> StrategyEvaluationRequest:
    return StrategyEvaluationRequest(
        reference or _reference(),
        parameter_schema_version="1",
        parameters={"enabled": True},
        bars=_bars(),
    )


def test_scripted_provider_evaluation_analysis_and_composition() -> None:
    registry, _ = _registry()
    request = _request()

    evaluation = registry.evaluate(request)
    analysis = registry.analyze(request)
    composite = registry.evaluate_composite(
        CompositeEvaluationRequest(
            evaluator=request.reference,
            evaluator_parameter_schema_version="1",
            evaluator_parameters={"enabled": True},
            composite_id="member-owned-definition",
            composite_version=1,
            members=(
                CompositeMember(
                    "member-a",
                    request.reference,
                    "1",
                    {"enabled": True},
                ),
            ),
            bars=_bars(),
        )
    )

    assert evaluation.intents == (StrategyIntent("hold", "scripted response"),)
    assert analysis.diagnostics[0].payload == {"points": ()}
    assert composite.reference == request.reference


def test_parameter_metadata_and_requests_copy_mutable_inputs() -> None:
    parameters: dict[str, object] = {"enabled": True}
    bars = list(_bars())
    request = StrategyEvaluationRequest(_reference(), "1", parameters, bars)
    parameters["enabled"] = False
    bars.clear()

    assert request.parameters == {"enabled": True}
    assert len(request.bars) == 1
    assert not hasattr(ParameterField("enabled", ParameterKind.BOOLEAN), "default")


def test_unknown_plugin_artifact_and_version_fail_closed() -> None:
    registry, _ = _registry()

    with pytest.raises(UnknownPluginError):
        registry.evaluate(_request(_reference(plugin=_plugin("2.0.0"))))

    altered_artifact = replace(_plugin(), artifact_digest="sha256:different")
    with pytest.raises(UnknownPluginError):
        registry.evaluate(_request(_reference(plugin=altered_artifact)))


def test_unknown_strategy_and_schema_versions_fail_closed() -> None:
    registry, _ = _registry()

    with pytest.raises(UnknownStrategyError):
        registry.evaluate(_request(_reference(strategy_version="2")))

    with pytest.raises(StrategyParameterError, match="unknown parameter schema"):
        registry.evaluate(replace(_request(), parameter_schema_version="2"))


def test_invalid_parameters_and_unadvertised_capabilities_fail_closed() -> None:
    reference = _reference()
    descriptor = StrategyDescriptor(
        reference=reference,
        display_name="Evaluation only",
        parameter_schema=ParameterSchemaMetadata("1"),
        capabilities=frozenset({StrategyCapability.EVALUATE}),
    )
    registry, _ = _registry(ScriptedProvider(descriptors=(descriptor,)))

    with pytest.raises(StrategyParameterError, match="enabled must be true"):
        registry.evaluate(replace(_request(), parameters={"enabled": False}))

    with pytest.raises(StrategyCapabilityError, match="analyze"):
        registry.analyze(_request())


def test_provider_result_identity_mismatch_fails_closed() -> None:
    registry, provider = _registry()
    provider.return_reference = _reference(strategy_version="unexpected")

    with pytest.raises(StrategyPluginContractError, match="identity"):
        registry.evaluate(_request())
    with pytest.raises(StrategyPluginContractError, match="identity"):
        registry.analyze(_request())


def test_registry_rejects_duplicate_or_mismatched_descriptors_and_freezes() -> None:
    provider = ScriptedProvider()
    registry = StrategyRegistry()
    registry.register(provider)

    with pytest.raises(ValueError, match="duplicate strategy plugin"):
        registry.register(provider)

    registry.freeze()
    with pytest.raises(RuntimeError, match="frozen"):
        registry.register(ScriptedProvider(_plugin("2.0.0")))

    mismatched = ScriptedProvider(
        _plugin("2.0.0"),
        descriptors=provider.descriptors(),
    )
    other_registry = StrategyRegistry()
    with pytest.raises(ValueError, match="does not match provider"):
        other_registry.register(mismatched)


def test_legacy_concrete_exports_emit_deprecation_warning_and_still_work() -> None:
    with pytest.warns(DeprecationWarning, match="MovingAverageCross"):
        moving_average = MovingAverageCross()
    with pytest.warns(DeprecationWarning, match="CompositeStrategy"):
        composite = CompositeStrategy((moving_average,))

    assert moving_average.evaluate(_bars()).side == "flat"
    assert composite.evaluate(_bars()).side == "flat"


def test_strategy_contract_modules_have_no_reverse_or_runtime_dependencies() -> None:
    package_root = Path(__file__).parents[1] / "tw_quant_core" / "strategy"
    forbidden = ("fastapi", "sqlite", "shioaji", "tw_quant.", "broker sdk")

    for source_file in package_root.glob("*.py"):
        source = source_file.read_text(encoding="utf-8").lower()
        for marker in forbidden:
            assert marker not in source, f"forbidden dependency marker in {source_file}: {marker}"


def test_public_api_document_lists_new_contracts() -> None:
    documentation = (Path(__file__).parents[1] / "docs" / "public-api.md").read_text(
        encoding="utf-8"
    )
    required_names = {
        "PluginArtifactIdentity",
        "StrategyDescriptor",
        "ParameterSchemaMetadata",
        "StrategyEvaluationResult",
        "StrategyAnalysisResult",
        "CompositeEvaluationRequest",
        "StrategyPluginProvider",
        "StrategyRegistry",
    }
    assert all(name in documentation for name in required_names)
