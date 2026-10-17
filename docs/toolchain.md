# Toolchain and common tasks

The repository uses Fedora RPM tooling for spec validation, SRPM creation, and binary builds. Package-specific `BuildRequires:` in each spec remain the source of truth for RPM build dependencies.

## Repository tools

Install the tools used by repository validation and local SRPM builds:

```sh
sudo dnf install rpm-build rpmdevtools rpmlint make
```

`rpmdevtools` provides `spectool` for staging declared sources. If `spectool` is missing in COPR's minimal SRPM environment, the shared `.copr/Makefile` installs `rpmdevtools` with DNF.

## Package build dependencies

Install package-specific dependencies when building a package locally. For **actionlint**, these include Go, Fedora Go RPM macros, Go Vendor Tools, and `ronn-ng`:

```sh
sudo dnf install go go-rpm-macros go-vendor-tools rubygem-ronn-ng
```

CI installs RPM build dependencies from the spec before building the binary RPM. `go2rpm` is optional for package generation or maintenance, not a declared build requirement.

The upstream source archive and generated Go vendor archive are included as SRPM sources; Go modules are not fetched during the build. See [actionlint package notes](../packages/actionlint/README.md) and the [Go Packaging Guidelines](packaging-guidelines/golang.md) when updating vendored sources and licensing.

## Common commands

```sh
make list
make validate
make srpm PACKAGE=actionlint
python3 -m unittest discover -s tests -v
```

`make validate` runs repository checks, creates an SRPM through the same shared Makefile target used by COPR, and runs rpmlint on the spec and SRPM. It does not build or lint binary RPMs. `make srpm` writes a local source RPM under `dist/srpm` by default.

## Build and inspect binary RPMs

Build in a Fedora environment. Install the spec's declared build dependencies, including dependencies requested dynamically by `%generate_buildrequires` where applicable, then rebuild the SRPM:

```sh
sudo dnf builddep packages/<name>/<name>.spec
rpmbuild --rebuild <path-to-src.rpm>
```

Review the resulting binary RPMs (and any debuginfo/subpackages):

```sh
rpmlint /path/to/*.rpm
rpm -qp --info /path/to/package.rpm
rpm -qp --requires /path/to/package.rpm
rpm -qp --provides /path/to/package.rpm
rpm -qp --list /path/to/package.rpm
rpm -qp --licensefiles /path/to/package.rpm
```

Confirm the metadata, dependencies, provides, installed paths, and license files match the spec and upstream. Install the RPM in a clean Fedora environment and smoke-test the packaged command where practical. A host rebuild is not an isolated build and does not by itself demonstrate offline behavior; CI/COPR build constraints and logs remain relevant.

For repository structure, CI flow, and package updates, see [package development](development.md).
