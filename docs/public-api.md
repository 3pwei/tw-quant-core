# Public API and compatibility policy

Version 1.0 establishes the supported API used by downstream applications.
The authoritative public surface is the names exported through `__all__` from
these namespaces:

- `tw_quant_core`
- `tw_quant_core.events`
- `tw_quant_core.market`
- `tw_quant_core.strategy`
- `tw_quant_core.broker`
- `tw_quant_core.execution`
- `tw_quant_core.risk`
- `tw_quant_core.backtest`
- `tw_quant_core.replay`
- `tw_quant_core.paper`

Consumers should import contracts from those namespaces, not from their
implementation modules. For example:

```python
from tw_quant_core.broker import BrokerOrderRequest, BrokerPort
from tw_quant_core.events import EventMetadata, OrderIntent
from tw_quant_core.market import KBar, TickEvent
from tw_quant_core.strategy import Decision, Strategy, StrategyRuntime
```

## Strategy and plugin contracts added in 1.1

The `tw_quant_core.strategy` namespace exports these broker/platform-neutral
contract groups:

- Identity and catalog: `PluginArtifactIdentity`, `StrategyIdentity`,
  `StrategyReference`, `StrategyDescriptor`, `StrategyCapability`
- Parameter metadata: `ParameterField`, `ParameterKind`,
  `ParameterSchemaMetadata`, `ParameterValidationResult`
- Evaluation: `StrategyEvaluationRequest`, `StrategyIntent`,
  `StrategyEvaluationResult`
- Analysis: `DiagnosticRecord`, `StrategyAnalysisResult`
- Composition: `CompositeMember`, `CompositeEvaluationRequest`
- Integration: `StrategyPluginProvider`, `StrategyRegistry`, and typed
  fail-closed registry errors

The registry only resolves exact identities registered by the application
composition root. It does not discover, install, import by user-supplied name,
or download plugins. Unknown plugin/artifact/strategy/schema versions,
unadvertised capabilities, invalid parameters, and mismatched provider result
identities raise registry errors. Strategy intents are not executable orders;
risk approval and order construction remain outside strategy plugins.

Parameter fields intentionally have no default-value member. Providers may
publish only display-safe schema metadata and must not expose production
parameters or proprietary implementation logic through descriptors or
diagnostics.

## Optional strategy capabilities added in 1.2

Core 1.2 adds three optional capability families without adding required
methods to the v1.1 `StrategyPluginProvider` Protocol:

- Parameter normalization: `ParameterNormalizationRequest`,
  `ParameterNormalizationResult`, and
  `StrategyParameterNormalizationProvider`
- Parameter templates: `ParameterTemplateRequest`, `ParameterTemplateResult`,
  and `StrategyParameterTemplateProvider`
- Composite analysis: `CompositeAnalysisRequest` and
  `StrategyCompositeAnalysisProvider`, returning the existing
  `StrategyAnalysisResult` and `DiagnosticRecord` envelopes

The matching `StrategyCapability` values are `NORMALIZE_PARAMETERS`,
`PARAMETER_TEMPLATE`, and `COMPOSITE_ANALYZE`. Providers opt into each port
independently. A descriptor that does not advertise the capability is rejected
before dispatch. A descriptor that advertises it while its provider omits the
corresponding optional Protocol is a provider-contract error. There is no
fallback to validation, evaluation, analysis, another provider, or dynamic
import/discovery.

Normalization requests carry the exact `StrategyReference`, parameter schema
version, and immutable supplied snapshot. Results repeat that identity and
supplied snapshot and add the provider-owned immutable normalized snapshot.
This permits aliases, omitted optional values, and provider-owned runtime
materialization without placing a default value in Core. Registry accepts the
result only when the identity, schema, and supplied snapshot exactly match the
request and the existing provider validator accepts the normalized snapshot.

Template requests and results likewise carry exact strategy/schema identity.
Template values exist only in the runtime provider result, are copied into
immutable containers, and must pass the provider's existing parameter
validator. Core defines only the envelope and never supplies a template or
strategy default.

`CompositeAnalysisRequest` reuses `StrategyReference`, `CompositeMember`, and
the same immutable bar/input shape as composite evaluation. Registry verifies
the evaluator capability and validates every evaluator/member identity, schema,
and parameter set before dispatch. The provider alone interprets topology,
ALL/ANY behavior, signals, and concrete diagnostics. The returned
`StrategyAnalysisResult` must identify the exact evaluator requested.

### Demo boundary decision

The reusable Core surface is the exact strategy/plugin identity model,
parameter schema and immutable parameter envelopes, bars, members, diagnostics,
and evaluation/analysis result contracts. Legacy Demo case IDs, TMF synthetic
cases, scenario catalogs, concrete strategies, and product presentation rules
are application-level data and behavior. A future Public Platform can compose
those concerns behind its own `DemoProvider`; Core 1.2 intentionally adds no
Demo provider, Demo implementation, or case catalog.

## Compatibility

This project follows Semantic Versioning from 1.0 onward.

- Patch releases contain compatible fixes and documentation changes.
- Minor releases may add optional fields, exports, enum values, and separate
  optional protocols. Required methods are not added to an existing provider
  protocol in a minor release. Consumers must handle unknown enum/event values
  defensively at system boundaries.
- Major releases may remove or incompatibly change public contracts.
- Public dataclass field names, meanings, validation rules, enum values,
  protocol method signatures, and documented exports are compatibility
  commitments.
- Deprecations remain available for at least one minor release and emit a
  `DeprecationWarning` before removal in the next major release.

### Deprecated in 1.1

`MovingAverageCross` and `CompositeStrategy` remain exported with their 1.0
constructor and evaluation behavior. Instantiation emits `DeprecationWarning`.
They are retained for the full 1.1 line and may be removed only in 2.0 or a
later major release. `Decision`, `Strategy`, and `StrategyRuntime` remain
unchanged.

Anything not exported from a documented namespace, including underscore-prefixed
names and implementation modules, may change without notice. Serialization is
only guaranteed through documented helpers such as `event_to_dict`; dataclass
implementation details are not a general wire-format promise.

## Boundary

The public API is broker-neutral and contains no production strategy,
production risk policy, broker SDK adapter, credentials, secret resolution,
execution-worker composition, recovery/reconciliation implementation,
deployment configuration, or internal runbook.
