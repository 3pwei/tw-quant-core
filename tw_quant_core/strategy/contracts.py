from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Literal, Mapping, Sequence

from ..market import KBar


def _required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


def _immutable_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(value))


def _immutable_payload(value: object) -> object:
    """Copy a provider payload into recursively immutable containers."""

    if isinstance(value, Mapping):
        return MappingProxyType(
            {key: _immutable_payload(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_immutable_payload(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_immutable_payload(item) for item in value)
    return value


def _immutable_payload_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(
        {key: _immutable_payload(item) for key, item in value.items()}
    )


@dataclass(frozen=True, order=True)
class PluginArtifactIdentity:
    """Exact identity of one installed, pre-approved strategy artifact."""

    plugin_id: str
    plugin_version: str
    artifact_name: str
    artifact_version: str
    artifact_digest: str

    def __post_init__(self) -> None:
        for field_name in (
            "plugin_id",
            "plugin_version",
            "artifact_name",
            "artifact_version",
            "artifact_digest",
        ):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name),
            )


@dataclass(frozen=True, order=True)
class StrategyIdentity:
    """Stable strategy key plus its exact implementation contract version."""

    strategy_id: str
    strategy_version: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "strategy_id", _required(self.strategy_id, "strategy_id"))
        object.__setattr__(
            self,
            "strategy_version",
            _required(self.strategy_version, "strategy_version"),
        )


@dataclass(frozen=True, order=True)
class StrategyReference:
    """An exact strategy implementation inside an exact plugin artifact."""

    plugin: PluginArtifactIdentity
    strategy: StrategyIdentity


class ParameterKind(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"


@dataclass(frozen=True)
class ParameterField:
    """Display-safe parameter metadata; deliberately has no default value."""

    name: str
    kind: ParameterKind
    required: bool = True
    title: str | None = None
    description: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", _required(self.name, "name"))
        if self.title is not None:
            object.__setattr__(self, "title", _required(self.title, "title"))
        if self.description is not None:
            object.__setattr__(
                self,
                "description",
                _required(self.description, "description"),
            )


@dataclass(frozen=True)
class ParameterSchemaMetadata:
    """Versioned public shape of accepted parameters, without parameter values."""

    schema_version: str
    fields: tuple[ParameterField, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "schema_version",
            _required(self.schema_version, "schema_version"),
        )
        object.__setattr__(self, "fields", tuple(self.fields))
        names = [parameter.name for parameter in self.fields]
        if len(names) != len(set(names)):
            raise ValueError("parameter field names must be unique")


class StrategyCapability(str, Enum):
    EVALUATE = "evaluate"
    ANALYZE = "analyze"
    COMPOSITE_EVALUATE = "composite_evaluate"
    NORMALIZE_PARAMETERS = "normalize_parameters"
    PARAMETER_TEMPLATE = "parameter_template"
    COMPOSITE_ANALYZE = "composite_analyze"


@dataclass(frozen=True)
class StrategyDescriptor:
    """Public catalog metadata for one exact strategy implementation."""

    reference: StrategyReference
    display_name: str
    parameter_schema: ParameterSchemaMetadata
    capabilities: frozenset[StrategyCapability]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "display_name",
            _required(self.display_name, "display_name"),
        )
        object.__setattr__(self, "capabilities", frozenset(self.capabilities))
        if not self.capabilities:
            raise ValueError("at least one strategy capability is required")


@dataclass(frozen=True)
class ParameterValidationResult:
    valid: bool
    errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        errors = tuple(_required(error, "validation error") for error in self.errors)
        object.__setattr__(self, "errors", errors)
        if self.valid == bool(errors):
            raise ValueError("valid results have no errors; invalid results require errors")


@dataclass(frozen=True)
class ParameterNormalizationRequest:
    """Request a provider-owned canonical parameter snapshot."""

    reference: StrategyReference
    parameter_schema_version: str
    supplied_parameters: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "parameter_schema_version",
            _required(self.parameter_schema_version, "parameter_schema_version"),
        )
        object.__setattr__(
            self,
            "supplied_parameters",
            _immutable_payload_mapping(self.supplied_parameters),
        )


@dataclass(frozen=True)
class ParameterNormalizationResult:
    """Provider-owned immutable canonicalization result with exact identity."""

    reference: StrategyReference
    parameter_schema_version: str
    supplied_parameters: Mapping[str, object]
    normalized_parameters: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "parameter_schema_version",
            _required(self.parameter_schema_version, "parameter_schema_version"),
        )
        object.__setattr__(
            self,
            "supplied_parameters",
            _immutable_payload_mapping(self.supplied_parameters),
        )
        object.__setattr__(
            self,
            "normalized_parameters",
            _immutable_payload_mapping(self.normalized_parameters),
        )


@dataclass(frozen=True)
class ParameterTemplateRequest:
    """Request a runtime-supplied configuration template for an exact schema."""

    reference: StrategyReference
    parameter_schema_version: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "parameter_schema_version",
            _required(self.parameter_schema_version, "parameter_schema_version"),
        )


@dataclass(frozen=True)
class ParameterTemplateResult:
    """Immutable provider-owned template values for an exact strategy schema."""

    reference: StrategyReference
    parameter_schema_version: str
    template_parameters: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "parameter_schema_version",
            _required(self.parameter_schema_version, "parameter_schema_version"),
        )
        object.__setattr__(
            self,
            "template_parameters",
            _immutable_payload_mapping(self.template_parameters),
        )


@dataclass(frozen=True)
class StrategyEvaluationRequest:
    reference: StrategyReference
    parameter_schema_version: str
    parameters: Mapping[str, object]
    bars: Sequence[KBar]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "parameter_schema_version",
            _required(self.parameter_schema_version, "parameter_schema_version"),
        )
        object.__setattr__(self, "parameters", _immutable_mapping(self.parameters))
        object.__setattr__(self, "bars", tuple(self.bars))


IntentAction = Literal["enter", "exit", "hold"]
IntentDirection = Literal["long", "short"]


@dataclass(frozen=True)
class StrategyIntent:
    """Non-executable strategy intent; Platform retains order and risk authority."""

    action: IntentAction
    reason: str
    direction: IntentDirection | None = None
    quantity: int = 0
    attributes: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "reason", _required(self.reason, "reason"))
        object.__setattr__(self, "attributes", _immutable_mapping(self.attributes))
        if self.action == "hold":
            if self.direction is not None or self.quantity != 0:
                raise ValueError("hold intents cannot have direction or quantity")
        elif self.direction is None or self.quantity < 1:
            raise ValueError("enter and exit intents require direction and positive quantity")


@dataclass(frozen=True)
class StrategyEvaluationResult:
    reference: StrategyReference
    intents: tuple[StrategyIntent, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "intents", tuple(self.intents))
        if not self.intents:
            raise ValueError("evaluation results require at least one intent")


@dataclass(frozen=True)
class DiagnosticRecord:
    """Versioned, renderer-neutral diagnostic payload supplied by a plugin."""

    diagnostic_id: str
    schema_version: str
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "diagnostic_id",
            _required(self.diagnostic_id, "diagnostic_id"),
        )
        object.__setattr__(
            self,
            "schema_version",
            _required(self.schema_version, "schema_version"),
        )
        object.__setattr__(self, "payload", _immutable_mapping(self.payload))


@dataclass(frozen=True)
class StrategyAnalysisResult:
    reference: StrategyReference
    diagnostics: tuple[DiagnosticRecord, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))
        identifiers = [item.diagnostic_id for item in self.diagnostics]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("diagnostic identifiers must be unique")


@dataclass(frozen=True)
class CompositeMember:
    member_id: str
    strategy: StrategyReference
    parameter_schema_version: str
    parameters: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "member_id", _required(self.member_id, "member_id"))
        object.__setattr__(
            self,
            "parameter_schema_version",
            _required(self.parameter_schema_version, "parameter_schema_version"),
        )
        object.__setattr__(self, "parameters", _immutable_mapping(self.parameters))


@dataclass(frozen=True)
class CompositeEvaluationRequest:
    evaluator: StrategyReference
    evaluator_parameter_schema_version: str
    evaluator_parameters: Mapping[str, object]
    composite_id: str
    composite_version: int
    members: tuple[CompositeMember, ...]
    bars: Sequence[KBar]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evaluator_parameter_schema_version",
            _required(
                self.evaluator_parameter_schema_version,
                "evaluator_parameter_schema_version",
            ),
        )
        object.__setattr__(
            self,
            "evaluator_parameters",
            _immutable_mapping(self.evaluator_parameters),
        )
        object.__setattr__(
            self,
            "composite_id",
            _required(self.composite_id, "composite_id"),
        )
        if self.composite_version < 1:
            raise ValueError("composite_version must be positive")
        object.__setattr__(self, "members", tuple(self.members))
        object.__setattr__(self, "bars", tuple(self.bars))
        if not self.members:
            raise ValueError("composite evaluation requires at least one member")
        member_ids = [member.member_id for member in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("composite member identifiers must be unique")


@dataclass(frozen=True)
class CompositeAnalysisRequest:
    """Broker-neutral analysis request interpreted only by its provider."""

    evaluator: StrategyReference
    evaluator_parameter_schema_version: str
    evaluator_parameters: Mapping[str, object]
    composite_id: str
    composite_version: int
    members: tuple[CompositeMember, ...]
    bars: Sequence[KBar]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "evaluator_parameter_schema_version",
            _required(
                self.evaluator_parameter_schema_version,
                "evaluator_parameter_schema_version",
            ),
        )
        object.__setattr__(
            self,
            "evaluator_parameters",
            _immutable_mapping(self.evaluator_parameters),
        )
        object.__setattr__(
            self,
            "composite_id",
            _required(self.composite_id, "composite_id"),
        )
        if self.composite_version < 1:
            raise ValueError("composite_version must be positive")
        object.__setattr__(self, "members", tuple(self.members))
        object.__setattr__(self, "bars", tuple(self.bars))
        if not self.members:
            raise ValueError("composite analysis requires at least one member")
        member_ids = [member.member_id for member in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("composite member identifiers must be unique")
