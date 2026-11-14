# Repository conventions

These conventions support a personal COPR; use a package-specific exception when it solves a real problem. See [development](development.md) for operations and validation, and the [package notes template](template.md) for documentation.

## Layout and names

Keep each spec and its supporting files in `packages/<name>/`, and its notes in `docs/<name>.md`. Use `<name>.spec`, `prepare-sources.sh` for optional SRPM preparation, `test-*` for tests, and `0001-descriptive-name.patch` for patches. Launchers and desktop files should reflect their installed names. Shared Packit and GitHub helpers belong in `.packit/` and `.github/scripts/` respectively.

Preserve upstream license and notice filenames where practical. When creating a distinct downstream filename, use `LICENSE-<component>`, `NOTICE-<component>`, or `COPYRIGHT-<component>` as appropriate. Never discard a notice to make names uniform. Source aliases, checksum manifests, preparation and `%license` must agree.

## Specs and source preparation

Group package metadata, sources and patches, architecture and dependencies before the standard `%description`, `%prep`, `%build`, `%install`, `%check`, `%files`, and `%changelog` sections, omitting sections when unnecessary. Retain upstream source URLs and explain important adaptations and patches; link upstream issues or pull requests when available. Use appropriate dependencies and architecture restrictions for each toolchain rather than copying another spec.

Packit calls `.packit/prepare-sources.sh` from the package directory. An optional package `prepare-sources.sh` receives the spec path and sources directory; it must honor `SOURCES_DEPS_PREINSTALLED=1`. Declare source-builder dependencies in `.packit.yaml`. Verify downloaded inputs using the supported `source.sha256` or `checksums.sha256` layout, and keep source aliases and manifest filenames synchronized. Check livecheck after source or version layout changes; document an explicit manual-update reason when automation cannot safely handle a package.

Keep RPM builds offline by default. Document any per-package network exception, downloaded toolchain or prebuilt component, runtime bootstrap, and relevant redistribution constraints. Source preparation may download verified inputs. Preserve applicable license texts and notices without inventing an exhaustive audit requirement.

## Validation and documentation

Prefer offline functional `%check` assertions beyond version and help. Document skipped checks, actual Fedora targets tested, important gaps, build blockers, and update-specific concerns in the package notes. Use [development](development.md) for the shared test commands and build procedures. Avoid repeating common operational instructions in every package note.

## Commits

Use Conventional Commits: `type(scope): concise imperative description`. Scope package-specific work by package name, for example `fix(yazi): correct Lua notice lookup`; use an appropriate shared scope or omit it for repository-wide work. Common types include `feat`, `fix`, `build`, `ci`, `docs`, and `chore`. Keep unrelated package changes independently reviewable where practical. Do not add changelog entries for unpublished fixes.
