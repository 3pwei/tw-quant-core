# Architecture

`tw-quant-core` is a standalone public Python package.

```text
Market data -> deterministic events -> strategy runtime
            -> backtest / replay / paper
            -> generic risk -> simulated execution
```

The package exposes broker-neutral identity, order, capability, registry, and execution-target contracts. It contains no broker SDK adapter or production composition root.

Private production systems may depend on the versioned public package and implement its ports. The public package must never import, discover, or require a private production package.

## Boundaries

Included: event engine, market models, backtesting, replay, paper trading, strategy protocol/runtime/composition/examples, simulation, generic risk, and broker contracts.

Excluded: production strategies and parameters, proprietary risk policy, real-broker adapters, secret resolution, execution-worker composition, recovery/reconciliation internals, position guardian mechanics, deployment, credentials, account mappings, and internal runbooks.


## Package namespace

The distribution name is `tw-quant-core` and its import namespace is
`tw_quant_core`. The namespace is intentionally distinct from private
production packages. This allows both distributions to be installed in one
environment without one wheel overwriting or shadowing the other's modules.
