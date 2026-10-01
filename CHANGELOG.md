# Changelog

All notable changes follow Semantic Versioning.

## 1.2.0 - Unreleased

- Add exact-identity immutable parameter-normalization request/result contracts
  for provider-owned alias handling, optional-value normalization, and runtime
  materialization.
- Add provider-owned parameter-template envelopes without placing strategy
  defaults or proprietary values in Core.
- Add broker-neutral composite-analysis requests that reuse exact strategy
  references, composite members, diagnostics, and analysis results while
  leaving topology and signal semantics to strategy providers.
- Add normalization, template, and composite-analysis capabilities through
  separate optional provider Protocols; keep the v1.1 `StrategyPluginProvider`
  Protocol unchanged.
- Make Registry dispatch for new optional operations fail closed on missing
  capability/port, unknown artifact/strategy/schema, invalid normalized or
  template parameters, and mismatched result identity, without fallback or
  dynamic discovery.
- Document that reusable Demo envelopes need no Core implementation and that
  product-specific cases belong in a future Platform-level `DemoProvider`.

## 1.1.0 - 2026-10-01

- Add exact-version strategy identity, descriptor, parameter-schema, intent,
  diagnostics, composite-evaluation, plugin-provider, and registry contracts.
- Fail closed when a plugin, artifact, strategy, schema version, capability, or
  provider result identity is unknown or inconsistent.
- Deprecate `MovingAverageCross` and `CompositeStrategy` with runtime warnings;
  retain both exports until the next major release.

## 1.0.0

- Declare the stable Public Core namespaces and compatibility policy.
- Mark the distribution as typed and expose its installed version.
- Add wheel, clean-install, metadata, and public-boundary verification.
- Add a tag-driven release build that produces wheel and source artifacts.

## 0.1.1

- Isolate the public `tw_quant_core` package namespace.

## 0.1.0

- Establish the initial broker-neutral public core.
