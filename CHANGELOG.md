# Changelog

All notable changes follow Semantic Versioning.

## 1.1.0 - Unreleased

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
