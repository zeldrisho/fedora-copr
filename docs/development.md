# Development

This repository packages upstream software as ordinary Fedora RPM specs and stages builds on COPR. It follows the root layout of `copr-fedora`—project metadata under `.copr/`, package definitions under `packages/`, helper scripts under `scripts/`, and CI under `.github/workflows/`. GitHub Actions validates changes and automatically syncs/submits COPR builds after successful pushes to `main`; see [COPR setup](copr.md) for the one-time credential configuration.

## Repository layout

```text
.copr/                  COPR SRPM Makefile and project metadata
.github/workflows/      Pull-request package validation
packages/<name>/        Fedora spec and package-specific sources/docs
scripts/                Package validation helpers
docs/                   Development, packaging, COPR, release guides
```

Each package directory, spec filename, and spec `Name:` must agree. Keep specs Fedora-submittable; COPR-specific behavior belongs in `.copr/Makefile`, not in a spec.

## Install tools

Separate repository-wide development tools from package build dependencies. A package's `BuildRequires:` in its spec is the source of truth for what the RPM build needs.

### Core repository tools

These tools are used to validate specs, create SRPMs, and run the repository helpers:

```sh
sudo dnf install rpm-build rpmdevtools rpmlint make
```

`rpmdevtools` supplies `spectool`, which the shared COPR Makefile uses to stage declared sources. Git is useful for normal repository work, but the validation command itself does not require it.

### Package-specific tools

Install these on the host only when you need to build or maintain that package locally. COPR installs the package's declared `BuildRequires:` in its build environment.

For **actionlint**, the spec's build requirements are Go RPM macros, Go Vendor Tools, GNU Make, and the `ronn-ng` man-page generator. On Fedora, install them with:

```sh
sudo dnf install go go-rpm-macros go-vendor-tools make rubygem-ronn-ng
```

The upstream archive and generated Go vendor archive are already checked in/downloaded as SRPM sources; Go module downloads are not needed during the RPM build. `go2rpm` is an optional helper for package generation or maintenance, not a declared build requirement. See [actionlint package notes](../packages/actionlint/README.md) for vendor updates.

## Common tasks

```sh
make list
make validate
make srpm PACKAGE=actionlint
```

`make validate` parses each spec, creates an SRPM through the same `.copr/Makefile` target used by COPR, and runs rpmlint. `make srpm` creates a source RPM locally. COPR performs binary builds in its configured build environments; inspect their logs and test successful RPMs before relying on a release.

## Further reading

- [Fedora packaging policy](packaging.md)
- [COPR setup](copr.md)
- [Release process](release.md)
