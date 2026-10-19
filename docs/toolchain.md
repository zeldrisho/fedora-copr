# Toolchain and common tasks

The repository uses Fedora RPM tooling for spec validation, SRPM creation, and binary builds. Package-specific `BuildRequires:` in each spec remain the source of truth for RPM build dependencies.

## Repository tools

Install the tools used by repository validation and local SRPM builds:

```sh
sudo dnf install rpm-build rpmdevtools rpmlint make copr-cli
```

`rpmdevtools` provides `spectool` for staging declared sources. If `spectool` is missing in COPR's minimal SRPM environment, the shared `.copr/Makefile` installs `rpmdevtools` with DNF.

## COPR CLI setup

Read-only queries such as `copr-cli list-builds zeldrisho/packages` do not need credentials. For submissions, sign in to the [COPR API configuration page](https://copr.fedorainfracloud.org/api/) and save its generated configuration locally as `~/.config/copr` (create `~/.config` if needed). Restrict access with `chmod 600 ~/.config/copr`, then check the configured identity with `copr-cli whoami`. Never commit or print the configuration: it contains an API token. This local configuration is separate from GitHub's `COPR_CONFIG` secret.

Use the CLI for build status and artifacts:

```sh
copr-cli list-builds zeldrisho/packages --output-format json
copr-cli status <build-id>
copr-cli download-build <build-id> -r <chroot> \
  --review --dest dist/review/<name>
```

Replace `<chroot>` with a chroot from the selected build that matches the Fedora release and architecture you want to inspect.

`packages/<name>/` contains packaging inputs, not published binary RPMs or generated COPR review reports. Review downloads belong under ignored `dist/review/`. To install a published package, use DNF as described in the root [README](../README.md); no manual RPM download is needed. Use `download-build --rpms` only when binary artifacts are needed for inspection or a separate test environment.

## Package build dependencies

For **new packages**, perform an initial local package build and record its elapsed time before deciding whether subsequent builds should be local or use COPR. For existing packages, base that choice on measured build time and maintenance needs. Current policy is to use COPR for Herdr and Yazi binary builds because local builds take too long; local SRPM creation and repository validation remain useful and permitted. COPR artifacts/logs are authoritative for their target chroots.

Install package-specific dependencies when building locally. For Rust applications such as Yazi, shared tools include Cargo and Fedora's Rust RPM macros:

```sh
sudo dnf install cargo cargo-rpm-macros lua-devel oniguruma-devel
```

Yazi uses Fedora's system Lua and Oniguruma rather than building these C libraries from bundled sources. For **Herdr**, install the Zig compiler required by the release (0.9.5 requires Zig 0.16.0):

```sh
sudo dnf install zig
```

Herdr's Cargo crate sources and Zig package sources are provided by package-local archives; `%build` and `%check` must not download dependencies. See [Herdr package notes](../packages/herdr/README.md) and [Yazi package notes](../packages/yazi/README.md) for package-specific source and build constraints.

For specs using `%cargo_generate_buildrequires`, static `dnf builddep <spec>` is not enough: first generate the dynamic requirements, then ask DNF to resolve them:

```sh
rpmbuild -br packages/<name>/<name>.spec \
  --define '_sourcedir /path/to/packages/<name>' \
  --define '_srcrpmdir /tmp/buildreqs'
sudo dnf builddep /tmp/buildreqs/<name>-*.buildreqs.nosrc.rpm
```

`cargo-rpm-macros` provides `%cargo_prep`, `%cargo_generate_buildrequires`, `%cargo_build`, `%cargo_test`, and Cargo license-report macros. Use Fedora macros and offline dependency configuration; do not allow Cargo to download crates during `%build` or `%check`.

Install package-specific dependencies when building a package locally. For **actionlint**, these include Go, Fedora Go RPM macros, Go Vendor Tools, and `ronn-ng`:

```sh
sudo dnf install go go-rpm-macros go-vendor-tools rubygem-ronn-ng
```

GitHub Actions validates and lints SRPMs but does not build binary RPMs. COPR performs published builds in its configured chroots once you submit them; a successful PR check is not evidence that package compilation, installation, or runtime smoke tests pass. `go2rpm` is optional for package generation or maintenance, not a declared build requirement.

The upstream source archive and generated Go vendor archive are included as SRPM sources; Go modules are not fetched during the build. See [actionlint package notes](../packages/actionlint/README.md) and current [Fedora Go guidance](references.md#fedora-packaging) when updating vendored sources and licensing.

## Common commands

```sh
make list
make validate
make srpm PACKAGE=actionlint
python3 -m unittest discover -s tests -v
```

`make validate` runs repository checks, creates SRPMs through the shared Makefile target used by COPR, and runs rpmlint on specs and SRPMs; it does not build or lint binary RPMs. Validation copies packages into temporary directories and removes SRPMs and scratch build files when it exits; use `make srpm` when you want to retain an SRPM. By default, `make srpm` writes it under `dist/srpm` in the repository. CI verifies each package's `docs/checksums.sha256` manifest with `sha256sum --check`; run `for manifest in packages/*/docs/checksums.sha256; do sha256sum --check "$manifest"; done` locally. When changing the Yazi syntax filter helper, run `cargo test --locked --manifest-path packages/yazi/scripts/filter-syntax-database/Cargo.toml`.

A quick **host binary build** is not an isolated or CI-equivalent check. For a new package's initial local build, or a package whose measured build time makes local builds practical, replace `<name>` below with its package directory/spec name. Do not use these commands for current Herdr or Yazi binary builds; use COPR unless the maintainer revises that choice based on timing evidence.

```sh
make srpm PACKAGE=<name> OUTDIR="$HOME/rpmbuild/SRPMS"
rpmbuild --rebuild "$HOME"/rpmbuild/SRPMS/<name>-*.src.rpm \
  --define "_topdir $HOME/rpmbuild"
```

The SRPM is retained in `~/rpmbuild/SRPMS`; binary RPMs and build logs are written under `~/rpmbuild/RPMS/` and `~/rpmbuild/BUILD/`. The `make srpm` step may download declared source archives into the package directory; those sources are retained there as well. If you only want to keep the SRPM, use `make srpm` without rebuilding it.

## Build and inspect binary RPMs

A local isolated binary build can use Mock and its Fedora chroot configurations for new-package initial builds and packages whose build duration permits it. For current Herdr and Yazi builds, diagnose failures from COPR logs and use COPR. Mock resolves static and dynamic build requirements inside its buildroot:

```sh
sudo dnf install mock mock-core-configs
sudo usermod -a -G mock "$USER"  # log out/in so the new group takes effect
mock -r fedora-44-x86_64 --rebuild <path-to-src.rpm> --resultdir "$PWD/results"
```

Use `fedora-45-x86_64` or `fedora-rawhide-x86_64` to check other COPR targets. Mock buildroot package installation needs network access; disable RPM build networking when testing that `%build` and `%check` do not fetch undeclared sources.

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
