# Public repository security

Only allowlisted public engineering belongs in this repository. Examples and tests use synthetic values.

Never commit credentials, tokens, passwords, private keys, certificates, account identifiers, production paths, production configuration, proprietary parameters, internal runbooks, or real-broker implementation details.

Private Git is not a secret store. A production integration must inject secrets outside source control and depend on this package in one direction only.
