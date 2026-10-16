# Toolchain and common tasks

The repository uses Fedora RPM tooling for spec validation, SRPM creation, and binary builds. Package-specific `BuildRequires:` in each spec remain the source of truth for RPM build dependencies.

## Repository tools

Install the tools used by repository validation and local SRPM builds:

```sh
sudo dnf install rpm-build rpmdevtools rpmlint make python3
```

`rpmdevtools` provides `spectool` for staging declared sources. If `spectool` is missing in COPR's minimal SRPM environment, the shared `.copr/Makefile` installs `rpmdevtools` with DNF.

## Package build dependencies

Install package-specific dependencies when building a package locally. For **actionlint**, these include Go, Fedora Go RPM macros, Go Vendor Tools, GNU Make, and `ronn-ng`:

```sh
sudo dnf install go go-rpm-macros go-vendor-tools make rubygem-ronn-ng
```

CI installs RPM build dependencies from the spec before building the binary RPM. `go2rpm` is optional for package generation or maintenance, not a declared build requirement.

The upstream source archive and generated Go vendor archive are included as SRPM sources; Go modules are not fetched during the build. See [actionlint package notes](../packages/actionlint/README.md) when updating the vendored source.

## Common commands

```sh
make list
make validate
make srpm PACKAGE=actionlint
python3 -m unittest discover -s tests -v
```

`make validate` runs repository checks, creates an SRPM through the same shared Makefile target used by COPR, and runs rpmlint. `make srpm` writes a local source RPM under `dist/srpm` by default. To build a binary RPM from an SRPM, install its declared build dependencies and run `rpmbuild --rebuild <path-to-src.rpm>`.

For repository structure, CI flow, and package updates, see [package development](development.md).
