# Releasing

Releases use Semantic Versioning and tags in the form `vMAJOR.MINOR.PATCH`.

1. Update `project.version` in `pyproject.toml` and move the changelog entry
   from `Unreleased` to the release date.
2. Run `python -m pytest -q` and `python -m build`.
3. Install the wheel into a clean virtual environment and run the import smoke
   test described in the README.
4. Merge the release commit, then create and push the matching tag (for
   example, `v1.0.0`).
5. Confirm the Release workflow passes and attach its verified wheel and sdist
   artifacts to the GitHub release. Publishing to a package index is a separate
   explicit maintainer action.

The tag and package version must match. Release artifacts must be built from a
clean checkout; production code, secrets, broker adapters, deployment files,
and private dependencies are prohibited.
