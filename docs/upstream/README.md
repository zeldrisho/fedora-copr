# Upstream packaging references

These local copies are Fedora packaging and licensing guidance sourced from `docs.fedoraproject.org`, preserved for offline reference. COPR documentation is not part of this directory; consult its live documentation at `docs.copr.fedorainfracloud.org` when needed. Consult the canonical source URLs recorded in each Fedora document when checking current policy; Fedora guidelines can change.

## Core packaging references

- [Packaging Guidelines](packaging-guidelines.md) — general spec, source, dependency, build, and file policies.
- [Source URL Guidelines](source-url.md) — source provenance, forge archives, and source declarations.
- [Licensing Guidelines](licensing-guidelines.md) — `%license` files and the RPM `License:` field.
- [Go Packaging Guidelines](golang.md) — relevant to actionlint's vendored Go dependencies, build flags, and licensing.

## Additional references

- [Naming Guidelines](naming.md) — package naming when adding a package.
- [Package Review Guidelines](review-guidelines.md) — useful as a self-review checklist.

## Provenance and terms

Each copy records its canonical upstream URL in its `source` metadata. These files are upstream documentation copies, not repository-authored material; do not assume the repository MIT license applies to them. Preserve upstream attribution and licensing notices when available. Verify applicable reuse terms from the source before redistributing or changing these copies; ask for a verified local copy if terms cannot be established.
