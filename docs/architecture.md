# Architecture

`tw-quant-core` is a standalone public Python package.

```text
Market data -> deterministic events -> strategy runtime
            -> backtest / replay / paper
            -> generic risk -> simulated execution
```

The package exposes broker-neutral identity, order, capability, registry, and
execution-target contracts. Strategy plugins integrate through exact artifact
and strategy identities, display-safe parameter metadata, non-executable
intents, versioned diagnostics, and an explicitly assembled registry. It
contains no broker SDK adapter, private strategy implementation, dynamic plugin
installer, or production composition root.

Private production systems may depend on the versioned public package and implement its ports. The public package must never import, discover, or require a private production package.

## Boundaries

Included: event engine, market models, backtesting, replay, paper trading,
strategy protocol/runtime and plugin contracts, simulation, generic risk, and
broker contracts. The v1 concrete `MovingAverageCross` and
`CompositeStrategy` exports are deprecated compatibility surfaces in 1.1 and
remain available until the next major release.

Excluded: production strategies and parameters, proprietary risk policy, real-broker adapters, secret resolution, execution-worker composition, recovery/reconciliation internals, position guardian mechanics, deployment, credentials, account mappings, and internal runbooks.

The Platform composition root is responsible for installing and verifying
approved artifacts before registering providers. Core performs no entry-point
discovery or downloads. Exact plugin/artifact/strategy/schema versions are
required at lookup time, and missing or inconsistent identities fail closed.


## Package namespace

The distribution name is `tw-quant-core` and its import namespace is
`tw_quant_core`. The namespace is intentionally distinct from private
production packages. This allows both distributions to be installed in one
environment without one wheel overwriting or shadowing the other's modules.
