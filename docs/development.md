# Development

These conventions support a personal COPR; use a package-specific exception when it solves a real problem. See the [package notes template](template.md) for documentation.

## Layout and names

Keep each spec and its supporting files in `packages/<name>/`, and its notes in `docs/<name>.md`. Use `<name>.spec`, `prepare-sources.sh` for optional SRPM preparation, `test-*` for tests, and `0001-descriptive-name.patch` for patches. Launchers and desktop files should reflect their installed names. Shared Packit and GitHub helpers belong in `.packit/` and `.github/scripts/` respectively.

Preserve upstream license and notice filenames where practical. When creating a distinct downstream filename, use `LICENSE-<component>`, `NOTICE-<component>`, or `COPYRIGHT-<component>` as appropriate. Never discard a notice to make names uniform. Source aliases, checksum manifests, preparation and `%license` must agree.

## Specs and source preparation

The [Fedora packaging tutorial](https://docs.fedoraproject.org/en-US/package-maintainers/Packaging_Tutorial/), [Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/), [licensing guidance](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) and [source URL guidance](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/) are useful references, not an official submission checklist. Language-specific guidance covers [Go](https://docs.fedoraproject.org/en-US/packaging-guidelines/Golang/), [Rust](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/), [Node.js](https://docs.fedoraproject.org/en-US/packaging-guidelines/Node.js/) and [Java](https://docs.fedoraproject.org/en-US/packaging-guidelines/Java/).

Group package metadata, sources and patches, architecture and dependencies before the standard `%description`, `%prep`, `%build`, `%install`, `%check`, `%files`, and `%changelog` sections, omitting sections when unnecessary. Retain upstream source URLs and explain important adaptations and patches; link upstream issues or pull requests when available. Use appropriate dependencies and architecture restrictions for each toolchain rather than copying another spec.

Packit calls `.packit/prepare-sources.sh` from the package directory. An optional package `prepare-sources.sh` receives the spec path and sources directory; it must honor `SOURCES_DEPS_PREINSTALLED=1`. Declare source-builder dependencies in `.packit.yaml`. Verify downloaded inputs using the supported `source.sha256` or `checksums.sha256` layout, and keep source aliases and manifest filenames synchronized. Check livecheck after source or version layout changes; document an explicit manual-update reason when automation cannot safely handle a package.

Keep RPM builds offline by default. Document any per-package network exception, downloaded toolchain or prebuilt component, runtime bootstrap, and relevant redistribution constraints. Source preparation may download verified inputs. Preserve applicable license texts and notices without inventing an exhaustive audit requirement.

## Package review

Prefer simple, maintainable source builds; prebuilt components are acceptable when they save disproportionate effort. This is not a Fedora submission: avoid official-review process or complexity without a concrete benefit.

For new packages and updates, review:

- Version sources and stability: tags, releases and registry `latest` labels can differ. Verify immutable source URLs and hashes; a checksum detects changes but does not independently prove provenance. Review pinned inputs, lockfiles and generated bundles together.
- Build and runtime dependencies, optional features and conflicts, including alternative Fedora names and providers on each target. Document bundled dependencies, prebuilt artifacts, runtime downloads and their security and licensing implications.
- Upstream license texts and applicable notices, known redistribution or corresponding-source obligations, and COPR rules. An exhaustive inventory of every dependency is not required.
- Installed commands, completions, docs, licenses, configuration, ownership and upgrade behavior. Document self-update or bootstrap downloads that bypass RPM management.
- Downstream patches: explain their purpose, link an upstream issue or PR when available, and revisit them on updates. Do not assume a patch can be dropped without building and testing.

For runtime dependency changes, inspect both spec declarations and generated binary RPM metadata. For example, with the relevant repository enabled:

```sh
dnf repoquery --available --latest-limit=1 --arch=x86_64,noarch --requires <package>
dnf repoquery --available --latest-limit=1 --arch=x86_64,noarch --recommends <package>
```

Select the target architecture and repository being reviewed; use `aarch64,noarch` for aarch64. The architecture filter excludes source RPMs and their build requirements. DNF normally installs available recommendations as well as hard requirements. Check whether providers are already pulled in transitively, and verify installation or feature behavior where practical. A query of an existing published RPM does not validate an unbuilt spec change.

## Testing and validation

Run applicable repository tests; package notes list additional checks. The CI workflow checks Packit paths, Python helpers and Vite+ source preparation separately from RPM builds:

```sh
(
  python3 .packit/test-paths.py || exit "$?"
  for t in .github/scripts/test-*.py packages/*/test-*.py; do
    python3 "$t" || exit "$?"
  done
  bash packages/vite-plus/test-source-preparation.sh || exit "$?"
)
```

Prefer a `%check` that exercises installed functionality and asserts a result or failure, beyond version or help output. Run upstream suites where practical and document tests skipped due to network, interactive requirements or other constraints.

Request [Packit builds](packit.md) for affected packages where practical, prioritizing the Fedora releases and architectures you use. Inspect RPM contents and test installation when useful; six-target builds and rpmlint are not mandatory for every change. Report tests, targets actually checked and important gaps; an SRPM build alone is not a successful RPM build. Document build blockers and update-specific concerns in the package notes without repeating common operational instructions.
