# Toolchain and common tasks

The repository uses Fedora RPM tooling for spec validation, SRPM creation, and binary builds. Package-specific `BuildRequires:` in each spec remain the source of truth for RPM build dependencies.

## Repository tools

Install the tools used by repository validation and local SRPM builds:

```sh
sudo dnf install rpm-build rpmdevtools rpmlint make
```

`rpmdevtools` provides `spectool` for staging declared sources. If `spectool` is missing in COPR's minimal SRPM environment, the shared `.copr/Makefile` installs `rpmdevtools` with DNF.

## Package build dependencies

Install package-specific dependencies when building a package locally. For Rust applications such as Yazi, install Cargo and Fedora's Rust RPM macros before resolving the spec's generated crate requirements:

```sh
sudo dnf install cargo cargo-rpm-macros lua-devel oniguruma-devel
```

For **Herdr**, install the Zig compiler required by the release (0.9.5 requires Zig 0.16.0):

```sh
sudo dnf install zig
```

Herdr's Cargo crate sources and Zig package sources are provided by package-local archives; `%build` and `%check` must not download dependencies. See [Herdr package notes](../packages/herdr/README.md) for source-bundle refresh guidance.

Yazi uses Fedora's Lua 5.4 and Oniguruma libraries rather than building those C libraries from bundled sources. For specs using `%cargo_generate_buildrequires`, static `dnf builddep <spec>` is not enough: first generate the dynamic requirements, then ask DNF to resolve them:

```sh
rpmbuild -br packages/<name>/<name>.spec \
  --define '_sourcedir /path/to/packages/<name>' \
  --define '_srcrpmdir /tmp/buildreqs'
sudo dnf builddep /tmp/buildreqs/<name>-*.buildreqs.nosrc.rpm
```

`cargo-rpm-macros` provides `%cargo_prep`, `%cargo_generate_buildrequires`, `%cargo_build`, `%cargo_test`, and the Cargo license-report macros. Build with Fedora macros and an offline dependency configuration; do not let Cargo download crates during `%build` or `%check`. If generated crate requirements are unavailable in Fedora, resolve that dependency gap before proceeding; do not silently switch to an unreviewed vendor bundle. For Yazi-specific source and license update notes, see [Yazi package notes](../packages/yazi/README.md).

Install package-specific dependencies when building a package locally. For **actionlint**, these include Go, Fedora Go RPM macros, Go Vendor Tools, and `ronn-ng`:

```sh
sudo dnf install go go-rpm-macros go-vendor-tools rubygem-ronn-ng
```

GitHub Actions validates and lints SRPMs but does not build binary RPMs. COPR performs published builds in its configured chroots after changes reach `main`; a successful PR check is not evidence that package compilation, installation, or runtime smoke tests pass. `go2rpm` is optional for package generation or maintenance, not a declared build requirement.

The upstream source archive and generated Go vendor archive are included as SRPM sources; Go modules are not fetched during the build. See [actionlint package notes](../packages/actionlint/README.md) and the [Go Packaging Guidelines](packaging-guidelines/golang.md) when updating vendored sources and licensing.

## Common commands

```sh
make list
make validate
make srpm PACKAGE=actionlint
python3 -m unittest discover -s tests -v
```

`make validate` runs repository checks, creates an SRPM through the same shared Makefile target used by COPR, and runs rpmlint on the spec and SRPM. It does not build or lint binary RPMs. Validation copies each package into a temporary directory and removes the SRPM and scratch build files when it exits; use `make srpm` when you want to keep an SRPM. By default, `make srpm` writes it under `dist/srpm` in the repository. CI verifies each package's `docs/checksums.sha256` manifest with `sha256sum --check`; run `for manifest in packages/*/docs/checksums.sha256; do sha256sum --check "$manifest"; done` locally. When changing the Yazi syntax filter helper, run `cargo test --locked --manifest-path packages/yazi/scripts/filter-syntax-database/Cargo.toml`.

For a quick **host build** (not an isolated or CI-equivalent check), keep artifacts in the standard RPM workspace by writing the SRPM to `~/rpmbuild/SRPMS` and rebuilding it with `~/rpmbuild` as the top directory:

```sh
make srpm PACKAGE=yazi OUTDIR="$HOME/rpmbuild/SRPMS"
mkdir -p /tmp/buildreqs
rpmbuild -br packages/yazi/yazi.spec \
  --define '_sourcedir packages/yazi' \
  --define '_srcrpmdir /tmp/buildreqs'
sudo dnf builddep /tmp/buildreqs/yazi-*.buildreqs.nosrc.rpm
rpmbuild --rebuild "$HOME"/rpmbuild/SRPMS/yazi-*.src.rpm \
  --define "_topdir $HOME/rpmbuild"
```

The SRPM is retained in `~/rpmbuild/SRPMS`; binary RPMs and build logs are written under `~/rpmbuild/RPMS/` and `~/rpmbuild/BUILD/`. The `make srpm` step may download declared source archives into the package directory; those sources are retained there as well. If you only want to keep the SRPM, use `make srpm` without rebuilding it.

## Build and inspect binary RPMs

For an optional local isolated build, install Mock and its Fedora chroot configurations, then rebuild the SRPM in a target chroot. This is useful for pre-merge checks and targeted debugging; COPR remains authoritative for its configured publishing chroots. Mock resolves static and dynamic build requirements inside its buildroot:

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
