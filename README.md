# tw-quant-core

A standalone, broker-neutral quantitative trading core for deterministic event processing, market models, backtesting, replay, paper trading, strategy runtimes, execution abstractions, and generic risk controls.

## Included

- Deterministic Event Engine and virtual clock
- Market, session, quote, and timeframe models
- Backtest and Replay engines
- Paper account and simulated execution
- Strategy protocol, runtime, composition, and synthetic example strategy
- Broker-neutral ports, models, capabilities, registry, and execution targets
- Generic risk calculations
- Public tests and CI security checks

## Install and test

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

The distribution uses the independent `tw_quant_core` import namespace so it can coexist with private applications that retain a legacy `tw_quant` package.

The package imports independently:

```bash
python -c "import tw_quant_core"
```

## Security and dependency boundary

This repository contains reusable public engineering only. It intentionally excludes production strategies and parameters, proprietary risk policy, broker SDK implementations, secret resolution, production execution composition, recovery/reconciliation internals, guardian mechanics, deployment configuration, internal runbooks, real account identifiers, and secrets.

A private production system may depend on a versioned release of this package. This package never imports or requires private production code.

See [Architecture](docs/architecture.md) and [Public repository security](docs/security.md).
