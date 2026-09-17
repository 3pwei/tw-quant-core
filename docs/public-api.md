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

## Compatibility

This project follows Semantic Versioning from 1.0 onward.

- Patch releases contain compatible fixes and documentation changes.
- Minor releases may add optional fields, exports, enum values, and protocol
  methods with compatible defaults. Consumers must handle unknown enum/event
  values defensively at system boundaries.
- Major releases may remove or incompatibly change public contracts.
- Public dataclass field names, meanings, validation rules, enum values,
  protocol method signatures, and documented exports are compatibility
  commitments.
- Deprecations remain available for at least one minor release and emit a
  `DeprecationWarning` before removal in the next major release.

Anything not exported from a documented namespace, including underscore-prefixed
names and implementation modules, may change without notice. Serialization is
only guaranteed through documented helpers such as `event_to_dict`; dataclass
implementation details are not a general wire-format promise.

## Boundary

The public API is broker-neutral and contains no production strategy,
production risk policy, broker SDK adapter, credentials, secret resolution,
execution-worker composition, recovery/reconciliation implementation,
deployment configuration, or internal runbook.
