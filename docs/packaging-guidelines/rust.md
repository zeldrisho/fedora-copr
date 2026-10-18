---
title: "Rust Packaging Guidelines"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/"
author:
published:
created: 2026-10-17
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
[Rust](https://www.rust-lang.org/) is a strongly and statically typed, compiled programming language that supports concepts from both imperative and functional programming.

Because there is not yet a stable Rust ABI, and because conditional compilation is a widely used feature in the Rust ecosystem, Rust libraries ("crates") can not be distributed in compiled form, and are instead distributed as source code.

This document covers how to handle Rust code in packages, specific to the different ways in which projects can be set up:

- [Rust "crates"](#rust-crates): packages that are individually published on [crates.io](https://crates.io/), the official package registry for Rust (primarily libraries, but also "single-crate" applications)
- [Non-crate Rust projects](#non-crate-rust-projects): Rust projects that are not published on crates.io, or larger projects that are comprised of many crates (cargo workspace)
- [Python projects](#python-projects) with a "native" component implemented in Rust: usually built with [setuptools\_rust](https://github.com/PyO3/setuptools-rust) or [maturin](https://github.com/PyO3/maturin)
- [mixed Rust / C/C++ projects](#mixed-rust--cc-projects) where parts of the project are implemented in Rust: either built by wrapping cargo, or by utilizing [meson](https://mesonbuild.com/Rust.html) 's limited support for directly building Rust code

The [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm) tool can be used to generate spec files for Rust crates from cargo / crate metadata. It is designed to produce spec files that are in line with the (Rust) Packaging Guidelines.

There are also guidelines for packaging shared libraries that are implemented in Rust (usually built and installed with [cargo-c](https://crates.io/crates/cargo-c)).

## Generic rules

This section covers rules that apply to *all* packages that ship Rust code.

### Compiler flags

Similarly to other language ecosystems in Fedora, there is a standardized set of compiler flags that **MUST** be passed to the Rust compiler.

The defaults for Rust are defined in the `%build_rustflags` macro from the `rust-srpm-macros` package. It is part of the default buildroot on Fedora 39+, where the `%set_build_flags` macro automatically sets the `$RUSTFLAGS` environment variable based on this macro.

For compatibility with older releases or EPEL, this environment variable can be set manually at the start of `%build` and `%check` in package’s spec files:

```shell
export RUSTFLAGS="%build_rustflags"
```

This is not necessary for packages that use the `%cargo_prep`, `%cargo_build`, and `%cargo_test` macros, which configure `cargo` to use the default `%build_rustflags` directly.

### Mandatory BuildRequires

The RPM macros that provide basic functionality for building Rust code are included in `rust-rpm-macros`, which is part of the default buildroot in Fedora, as it is a dependency of `redhat-rpm-config`. When building for ELN or EPEL8, this is not the case, and packages need to use `BuildRequires:  rust-toolset`.

Packages that build Rust code with cargo - directly or indirectly - or which call any of the `%cargo_*` macros, **MUST** add `BuildRequires:  cargo-rpm-macros`, which provides the implementations of all `%cargo_*` macros. This package is not part of the default buildroot, since it pulls in additional dependencies (i.e. a Python interpreter).

### Dynamically generated BuildRequires for crate dependencies

With Semantic Versioning (*"SemVer"*) being the only supported versioning scheme for Rust crates, dependencies on Rust libraries are almost exclusively specified as *"this version or any newer version that is API-compatible with it"*, i.e. a range of supported versions.

These ranges of supported versions need to be correctly translated into RPM dependencies, otherwise a wrong version of a dependency might get pulled in for builds, causing unhelpful error messages about missing dependencies.

Since dependencies of Rust projects change frequently, packages for projects that build Rust code with cargo **MUST** use dynamically generated `BuildRequires` by calling the `%cargo_generate_buildrequires` macro in the `%generate_buildrequires` scriptlet.

For example, a dependency on `serde = "1.0.100"` specified in a project’s `Cargo.toml` metadata (a dependency on the crate named "serde", with version "1.0.100" or any version API-compatible with "1.0.100", with default features enabled) would cause a dependency like this to be generated for RPM:

```
BuildRequires:  (crate(serde/default) >= 1.0.100 with crate(serde/default) < 2.0.0~)
```

Refer to the section about [RPM macros](#rpm-macros-1) for how to pass feature flags to this macro.

### License tags

Similar to other languages that produce statically linked binaries, Rust executables (and shared libraries) contain code that originates in other packages (i.e. packages for other Rust crates), which in turn are covered by different license terms.

This needs to be taken into account by maintaining a separate `License` tag for the subpackage that contains these binaries. More information about `License` tags is available from the [Fedora Legal docs](https://docs.fedoraproject.org/en-US/legal/license-field/).

The `cargo-rpm-macros` package provides two RPM macros that help with filling the `License` tag correctly for projects that are built with `cargo`:

- `%cargo_license_summary`

This macro determines and prints a summary of all the licenses of the Rust crates that end up statically linked into final binaries (properly excluding build-only or test-only dependencies). This summary can then be copied from the build log into the spec file as a comment. The actual contents of the `License` tag can then be obtained by constructing a conjunction of these individual licenses (with SPDX `AND` operators).

- `%cargo_license`

This macro determines and prints a complete breakdown of all Rust crates that end up statically linked into final binaries (according to the same logic as in the `%cargo_license_summary` macro), their versions, *and* their individual license expressions. Generating this list dynamically at build-time ensures that its contents always match the actual dependencies.

Both macros accept the same arguments as other `%cargo_*` macros (`-a`, `-n`, `-f`), and for their output to match the actual binaries, the same flags **MUST** be passed to them and `%cargo_build`.

### Vendored dependencies

[In general](https://docs.fedoraproject.org/en-US/packaging-guidelines/#bundling), packages **SHOULD NOT** use bundled crate dependencies, whenever possible.

Whenever vendored / bundled crate dependencies *are* used (no matter which mechanism is used for the purpose), all bundled crate dependencies **MUST** be declared with virtual `Provides` in the format `Provides: bundled(crate($crate)) = $version` in the subpackage that contains the Rust component. For example, these virtual `Provides` are used to determine the impact of security vulnerabilities on packages that use vendored Rust dependencies.

There are also two situations in which bundling at least *some* Rust crates is usually unavoidable:

#### Replacing git dependencies

One of the types of dependencies cargo supports are git snapshots, which are usually used to reference either a specific commit, or a reference to a downstream fork of a crate.

The project **SHOULD** be patched to use a version of this crate that is available on [crates.io](https://crates.io/) instead, if that is possible. If it turns out that depending on a git snapshot is no longer necessary, this patch **SHOULD** be submitted to the upstream project.

If the dependency is not published on [crates.io](https://crates.io/), or if the versions published there are not a suitable replacement, a git snapshot of the crate can be bundled. This can be achieved by creating and supplying a tarball with the git snapshot as a separate source, unpacking the tarball in `%prep`, and patching `Cargo.toml` to replace the git-based dependency with a path-based dependency. Adding this subproject as a workspace member ensures that its dependencies are included during dependency resolution.

#### Replacing patched crate sources

Another way in which cargo supports specifying modified dependencies is by "patching" a crate source, specifying an alternative source for specific crates - which will likely be either git references or path-based dependencies that are present to override a crate that is published on [crates.io](https://crates.io/) with a (modified) local copy, or a git repository that points to a (modified) fork of the crate.

These replacements **SHOULD** be dropped in favor of using only published versions of crates. If that is not possible, they must be replaced by path-based dependencies, similar to the process described for [git-type dependencies](#replacing-git-dependencies).

#### Using vendor tarballs

Support for building with vendored dependencies was added in version 25 of cargo-rpm-macros and rust2rpm.

- The `%cargo_prep` macro accepts a `-v $VENDOR` argument, where `$VENDOR` is the path to the directory that contains the vendored crate dependencies. When this argument is passed, the generated cargo configuration is set up for building against dependencies in this directory instead of dependencies from the system-wide registry.
- The `%cargo_generate_buildrequires` macro **MUST NOT** be called when using vendored dependencies.
- The `%cargo_vendor_manifest` macro generates a manifest (`cargo-vendor.txt`) that lists the names and versions of all crates in the vendor tarball. This macro **MUST** be called (for example, in the `%build` scriptlet), and the generated file **MUST** be added as a `%license` file in the appropriate package’s list of `%files`. An RPM generator parses this file and generates appropriate virtual `Provides` for all bundled crates, as is required for any bundled dependencies.
- Packages that build with vendored dependencies **MUST NOT** provide a Rust library interface (i.e. in `-devel` subpackages), because the resulting packages would have broken dependencies.

Typically, the `%prep` scriptlet will look like this when using vendored dependencies (assuming `Source1` is the vendor tarball, and it contains a top-level `vendor` directory):

```rpm
%prep
%autosetup -%{crate}-%{version} -p1 -a1
%cargo_prep -v vendor
```

The necessary spec file adaptations and the generation of the vendor tarball itself happen automatically when running rust2rpm in "vendor" mode.

## Rust crates

A large part of the process of packaging Rust crates can (and *should*) be automated by using [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm). It is designed to generate spec files that are compliant with both the general and the Rust Packaging Guidelines.

Additionally, due to some properties of packages for Rust crates (i.e. subpackages that correspond to crate features / optional dependencies), [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm) **MUST** be re-run for every new version of a crate to ensure that generated feature subpackages stays in sync with crate metadata.

### rust2rpm

The recommended way to write spec files for Rust crates is to use [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm), and apply any necessary modifications on top of the generated spec file.

There are a few common situations in which automatically generated spec files need manual changes:

- invalid `Summary` / `%description`: The heuristics for generating the `Summary` or `%description` for the package from the crate metadata can fail to produce valid values (i.e. `Summary` tag that is too long). In this case, the `Summary` needs to be shortened manually. This can also be overridden in the package-specific rust2rpm configuration file.
- unwanted dependencies / subpackages: Some crates provide non-default / optional features that are either unnecessary (i.e. only applicable to non-Linux systems), or have additional dependencies that are not packaged for Fedora. These features and unavailable optional dependencies **MUST** be removed from crate metadata - otherwise, the package will either fail to build, or produce subpackages with broken dependencies.
- nightly-only / unstable features: Some crates provide features that are only available on a nightly version of the Rust compiler, or features that are unstable and require an opt-in by passing environment variables. Features like these **SHOULD** be removed from crate metadata, since they either cannot work (Fedora ships only the stable Rust toolchain) or are not feasible to support.
- unwanted / unnecessary files ("bloat"): Some projects include files that are not required for the crate to function properly (files for CI settings, development / helper scripts, etc.). Files like these **SHOULD** be prevented from being installed (by adding / modifying the `package.include` or `package.exclude` settings in the crate metadata). It is recommended to submit changes like this to the upstream project.
- incompatible compiler flags: Some crates include custom settings for the `release` profile that are incompatible with RPM packaging. These settings **MUST** be removed from the `release` profile by patching `Cargo.toml`.

Crates that provide Rust bindings for C libraries usually require some additional changes (if possible):

- linking against system libraries: This often requires making some dependencies non-optional and / or modifying `build.rs` scripts to unconditionally link against system libraries instead of building and statically linking a bundled copy of the library.
- regenerating Rust bindings (and tests for them) at build-time: This too often requires making the `bindgen` dependency non-optional and / or modifying `build.rs` to cause regeneration of Rust bindings at build-time.

Note that patching `Cargo.toml` files (especially changing the set of optional dependencies and features) **MUST** be done by running `rust2rpm -p`, since changes like these affect spec file generation (i.e. the list of generated subpackages), which is only correctly taken into account if the patch is created *before* generation of the spec file.

It is recommended to track non-empty `rust2rpm.toml` configuration files in the package repository alongside the generated `.spec` file.

### Package naming

Packages for Rust crates from [crates.io](https://crates.io/) **MUST** use `rust-$crate` as the name of the source package (where `$crate` is the name of the project on [crates.io](https://crates.io/)).

This ensures that there are no name collisions between Rust crates published on [crates.io](https://crates.io/) and Rust crates packaged for Fedora.

When generating a package for a Rust crate that contains executable targets, the convention followed by [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm) is to generate a subpackage with a name that matches the crate name (i.e. the `rust-$crate` source package will have a `$crate` subpackage). If necessary, this subpackage can be renamed, for example, if the name does not match expectations, or if it would conflict with another already existing package.

### Package versioning

Projects that are built with cargo and / or published on [crates.io](https://crates.io/) follow Semantic Versioning (with small cargo-specific tweaks). Since SemVer strings can contain characters that are invalid in RPM version strings, they **MUST** be translated to be RPM-compatible.

For example, pre-releases are denoted by a `-<pre>` suffix in SemVer, but the `-` character is invalid in RPM Versions. This can be solved by replacing `-` with the `~` character, which denotes pre-releases in RPM version strings. This translation happens automatically for the `Version` tag when generating a spec file with [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm), and the "upstream" version is stored in a separate macro that can be used to refer to the "original" version string.

Additionally, some Rust crates carry extra "build" metadata in their versions (a ``<build>` suffix). This format is primarily used to carry information about the version of a bundled C library. This `<build>`` suffix **MUST** be removed from crate metadata with a patch, since it can interfere with RPM dependency / version resolution. This happens automatically when using rust2rpm version 25 or newer.

### Package sources

The canonical source of Rust crates is [crates.io](https://crates.io/). Projects from [crates.io](https://crates.io/) **MUST** be packaged from the sources that are published there (i.e. by using the `%{crates_source}` macro).

If the sources published on [crates.io](https://crates.io/) do not contain all files that are necessary for creating the package (for example, missing `.desktop` file or man pages), the upstream sources can be used as an *additional* source, but they **MUST NOT** be used for building the crate itself. It is recommended to file an issue with the upstream project about including these additional files in published crates.

Alternatively, if the project in question does not provide a Rust library interface, it can be packaged as a [Non-crate Rust project](#non-crate-rust-projects) using the upstream sources instead.

### Crate license

Most tooling support for determining licenses requires accurate metadata about licenses in crate metadata, including the `%cargo_license*` macros, and other third-party tools like `cargo-license` and `cargo-deny`.

For this reason, the license metadata for all Rust crates packaged for Fedora **MUST** match the license tag of the Fedora package itself. Any crates that set `package.license-file` in their metadata (which is reserved for non-standard / non-SPDX licenses) **MUST** be patched to set `package.license` in their metadata, and an accurate SPDX expression **MUST** be provided instead. Patches like this **SHOULD** be submitted upstream.

### Subpackages for crate features

Optional features / dependencies of Rust crates are translated into RPM subpackages to support resolving dependencies for features and optional dependencies of crates. The list of crate "features" (including any implicitly defined features for optional dependencies) **MUST** be kept in sync with the list of subpackages, i.e. for every feature `$foo` of the crate `$crate`, there must be a subpackage with name `rust-$crate+$foo-devel`, and vice-versa. This is required for RPM generators for `Provides` and `Requires` for these optional features / dependencies to work correctly.

If optional features that are *not* part of the default feature set are unused and would pull in additional (possibly unavailable) dependencies, the package **MAY** omit subpackages for these specific feature names. However, care needs to be taken that the features corresponding to the omitted subpackages are not "reachable" via subpackages that have *not* been omitted, since this would result in packages with unsatisfiable dependencies. Disabling optional features sometimes cannot be handled correctly simply by omitting subpackages for specific features. In these cases, the crate metadata in `Cargo.toml` needs to be patched accordingly instead.

Beware that the "default" feature is always implicitly defined by cargo, even if the crate metadata does not contain a `[features]` table or an explicitly defined "default" feature, so the subpackage for the "default" feature will be present in all packages for Rust crates with a library interface.

### RPM generators for Provides and Requires

The cargo-rpm-macros package includes RPM generators for automatically generating `Provides` and `Requires` for Rust crates that comply with the Packaging Guidelines (i.e. install their files into the correct location, `%{crate_instdir}`).

- the main `rust-$crate-devel` subpackage **MUST** provide `crate($crate) = %{version}`
- the `rust-$crate+$feature-devel` subpackages **MUST** provide `crate($crate/$feature) = %{version}` and require `crate($crate) = %{version}` (i.e. `rust-$crate-devel`)

Additionally, dependencies on external Rust crates must be as expected:

- the main `rust-$crate-devel` subpackage **MUST** require the virtual `Provides` for all non-optional crate dependencies
- the `rust-$crate+$feature-devel` subpackages **MUST** require the virtual `Provides` for the optional crate dependencies and features that are listed as the feature’s dependencies in crate metadata

### Packaging multiple versions

In most circumstances, the latest version of a crate **SHOULD** be packaged, and - if possible - packagers **SHOULD** port crates to use the latest available version of their dependencies, and submit these patches to upstream to limit divergence between the upstream project and the Fedora package.

However, there are two common scenarios in which it is often necessary to provide packages for multiple versions of a library crate simultaneously:

- It is not feasible to port a crate to the version of a crate dependency in Fedora due to large API changes between the required and the packaged version.
- The number of packages affected by a required SemVer-incompatible library update is very large.

In these cases, a "compat package" can be created for the older version (i.e. usually the current version), and the suffix-less package can be updated to the newer version. [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm) supports automatically creating "compat packages" with names that are compliant with the [Naming Guidelines for this case](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/#multiple) *and* compatible with the restrictions of Semantic Versioning by using the `rust2rpm --compat` flag.

All "compat packages" for Rust crates **MUST** follow the guidelines for Rust crates, and two additional rules apply when creating them:

- For crates that also includes an executable, only the package for the *latest* version can include this executable, and it **MUST NOT** be built and included in any older versions, to prevent both the name of the executable under `/usr/bin` and the name of the subpackage would conflict between the old and the new version of the package.
- The packager **SHOULD** check whether running tests in the old version of the crate would cause additional, potentially undesirable dependencies, for example, older versions of other dependencies that would require creating additional "compat packages" - in this case, tests **SHOULD** be disabled (i.e. by flipping the `check` bcond).

### The check bcond

The behaviour of some RPM macros depends on the presence and value of the `_with_check` macro, i.e. if `%bcond_without check` or `%bcond_with check` are used in the spec file - notably, the `%cargo_generate_buildrequires` macro only includes `dev-dependencies` (i.e. dependencies that are only used for compiling and / or running a project’s test suite with cargo) if the `check` bcond is enabled.

Additionally, packages for Rust crates that are generated by [rust2rpm](https://codeberg.org/rust2rpm/rust2rpm) use the value of this macro to determine if the `%check` scriptlet is run.

Packages for Rust crates **MUST** set this bcond to avoid unexpected behaviour of the `%cargo_*` macros, by either explicitly *enabling* or *disabling* tests.

### Running tests

Rust crates can have three different kinds of tests in their test suites:

- *"unit tests"*: These tests are included alongside library / application source code in the `src/` directory, and can reference private APIs (similar to "glass-box" tests).
- *"integration tests"*: These tests are usually separate files under the `tests/` directory, and they can only rely on public API of the tested crate (similar to "black-box" tests).
- *"doctests"*: These tests are automatically extracted from code blocks in Markdown documentation, which is often used as a mechanism to ensure that code snippets in documentation for public methods are correct and continue to compile.

By default, running `cargo test` (i.e. by calling the `%cargo_test` macro), all three kinds of tests are run. They can also be invoked separately (for example, because parts of the test suite or large data files are not included in published sources) by passing through filtering arguments to the underlying `cargo test` command:

- `%cargo_test -- --lib`: only run *"unit tests"* for the library interface
- `%cargo_test -- --bin foo`: only run *"unit tests"* for binary "foo"
- `%cargo_test -- --doc`: only run *"doctests"*
- `%cargo_test -- --test bar`: only run *"integration test"* "bar"

This can be combined with additional flags to skip tests with specific names (or that contain a specific string in their name) by passing the `--skip` argument through to the test harness (can be specified multiple times):

```
%cargo_test -- --lib -- --skip foo::bar::tests::test1
```

By default, cargo uses substring matching to match `--skip` arguments and actual names of tests, which can be turned off by using the `--exact` flag.

If any tests are skipped or disabled, the package **SHOULD** include comments that explain why this is the case, and include links to upstream issues, if available.

## Non-crate Rust projects

This section applies to Rust projects that are not packaged from sources on crates.io.

The most common cases are

- applications that do not provide a library interface,
- projects comprised of multiple crates (cargo workspaces) that may or may not be published (or useful) separately, and
- Python packages implemented in Rust ([covered below](#python-projects)).

Packages like this **MUST NOT** ship crate sources in `%{cargo_registry}`, i.e. they cannot ship `-devel` subpackages that contain crate sources or have subpackages that have virtual provides for `crate(...) = %{version}`.

### Package naming

Packages for non-crate Rust projects **MUST** be named according to the generic [Naming Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/), i.e. they **MUST NOT** use a `rust-` prefix for the source package name.

### Package sources

The generic guidelines for [referencing sources](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/) apply.

The `%{crates_source}` macro **SHOULD NOT** be used for packages like this, even when packaging a Rust crate that is also published on crates.io.

### RPM macros

Any `-a` and `-n` flags or `-f` arguments that are passed to `%cargo_generate_buildrequires` are applied to *all* workspace members during dependency resolution.

The `%cargo_install` macro **SHOULD NOT** be used for packages like this. Instead, use `install` or `cp` to copy built executables or shared libraries from `target/rpm/*` into the buildroot explicitly, as needed.

## Python projects

Python packages that use [setuptools\_rust](https://github.com/PyO3/setuptools-rust) or [maturin](https://github.com/PyO3/maturin) to build a "native" Python extension also need to apply the [generic rules](#generic-rules) for Rust packages in addition to following the [Python Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/).

Both [setuptools\_rust](https://github.com/PyO3/setuptools-rust) and [maturin](https://github.com/PyO3/maturin) build the native Python extension by calling cargo internally, so the basic setup for projects that build with cargo is required for packages like this as well.

This includes calling `%cargo_prep` in `%prep` to set up the build environment for cargo, and using `%cargo_generate_buildrequires` to dynamically generate the appropriate `BuildRequires` for Rust crate dependencies.

Additionally, `%cargo_license` and / or `%cargo_license_summary` **MUST** be used to determine the licenses that apply to the statically linked Python extension.

The packager also **MUST** ensure that the default [compiler flags](#compiler-flags) are passed to rustc, and that debuginfo is not stripped during the build process due to settings in the `setuptools-rust` or `maturin` configuration.

## Mixed Rust / C/C++ projects

Handling of projects that include both C/C++ and Rust code depends on how building the Rust code is integrated into the project’s build system.

Independent of the specific setup, the correct [compiler flags](#compiler-flags) **MUST** be passed to rustc, and the License tag of the package that contains the Rust component **MUST** take the licenses of statically linked crates into account.

### Building with cargo internally

Projects with build systems that call cargo internally to build Rust components **MUST** follow the same guidelines as other projects that build Rust code with cargo.

Packages **MUST** ensure that the cargo calls that are internal to the project’s build system do not pass flags or arguments that are incompatible with either the default [compiler flags](#compiler-flags) or cargo options that are set in the `%cargo_build` macro or configured by `%cargo_prep`.

### Building with meson directly

Recent versions of [meson](https://mesonbuild.com/Rust.html) have limited support for building crate dependencies without cargo. It is necessary to manually override crate sources with the local registry to use packaged crate dependencies.

## RPM macros

The process of building and installing Rust projects is almost entirely automated with several RPM macros:

- `%cargo_prep`: This macro **MUST** be called in the `%prep` scriptlet after sources have been unpacked. It sets up the build environment for cargo and injects a cargo configuration file, which sets the default compiler flags and configures the local crate registry as a replacement for [crates.io](https://crates.io/).
- `%cargo_generate_buildrequires`: This macro **MUST** be called in the `%generate_buildrequires` scriptlet, except when building with vendored dependencies. This is the mechanism that automatically generates dependencies on other Rust crates based on the metadata in `Cargo.toml`.
- `%cargo_build`: This macro **MUST** only be called in the `%build` scriptlet unless the build is handled in another way, i.e. "cargo build" is called internally by build scripts. It runs `cargo build` with the appropriate command line arguments. Calling this macro **MAY** be skipped if the crate is not supported on the current CPU architecture.
- `%cargo_install`: This macro **MUST** only be called in the `%install` scriptlet for crates that provide a library interface. It runs `cargo package` and installs the resulting directory tree into `%{buildroot}/%{crate_instdir}` (i.e. `%{buildroot}/%{cargo_registry}/%{crate}-%{version}/`). For crates that provide `bin` targets, it installs all built executables into `%{buildroot}/%{_bindir}`. If any built executables need to be installed in a different location, they can be moved after calling `%cargo_install`, or `%cargo_install` can be replaced with manual installation steps (copying from `target/rpm/*`). To prevent installation of executables by this macro, the `%cargo_install_bin` macro can be defined to `0`. To prevent installation of library sources by this macro, the `%cargo_install_lib` macro can be defined to `0`.
- `%cargo_test`: This macro **MUST** only be called in the `%check` scriptlet. It runs `cargo test` with the appropriate command line arguments. Calling this macro **MAY** be skipped if the crate is not supported on the current CPU architecture or if tests are disabled in general.
- `%cargo_license` / `%cargo_license_summary`: These macros **MUST** be called in the `%build` scriptlet after `%cargo_build` when building crates that include binary targets. They can be used to print the list of the licenses of the crates that are statically linked into any built executable or shared library (see [License tags](#license-tags)).
- `%cargo_vendor_manifest`: This macro **MUST** be called in the `%build` scriptlet after `%cargo_build` when building Rust projects with vendored dependencies. It writes a machine-readable list of all vendored dependencies to `cargo-vendor.txt`, which **MUST** be included as a `%license` file in the package that contains the statically linked executable(s).

All packages for Rust crates **MUST** set either `%bcond check 1` or `%bcond check 0`. The value of this macro affects whether `%cargo_generate_buildrequires` includes dependencies that are required for building and running tests.

Non-crate packages can either use the `%bcond check` *or* pass the `-t` flag to the `%cargo_generate_buildrequires` macro to include test-only dependencies in `BuildRequires` generation.

All `%cargo_*` macros (except `%cargo_prep` and `%cargo_vendor_manifest`) accept a set of optional flags / arguments that can be used to control the feature flags that are passed to cargo (usually to enable optional / non-default features):

- `-a`: Causes the `--all-features` flag to be passed to cargo, and the `%cargo_generate_buildrequires` macro to resolve dependencies with all optional features enabled.
- `-n`: Causes the `--no-default-features` flags to be passed to cargo, and the `%cargo_generate_buildrequires` macro to resolve dependencies with all default and optional features disabled.
- `-f foo,bar`: Causes the `--features foo,bar` argument to be passed to cargo, and the `%cargo_generate_buildrequires` macro to resolve dependencies with the additional features `foo` and `bar` enabled. This argument accepts a comma-separated list of feature names (or names of optional dependencies).

The `-a` and `-n` flags are mutually exclusive and cannot be passed together. The `-a` flag and `-f` arguments are also incompatible, since passing `-a` already enables all features. However, using the `-n` flag and specifically enabling *some* features with the `-f` argument is valid.

There are some common situations in which passing these flags or arguments is necessary:

- It can be necessary to enable additional features and / or optional dependencies to build and run the test suite of a crate. In this case, the required features **MUST** be enabled by passing the corresponding flags to all `%cargo_*` macros, unless the required optional dependencies are not packaged yet.
- Some applications support additional / non-default features by passing feature flags. If it is desirable to build applications with these features enabled, the required features need to be enabled by passing the corresponding flags to all `%cargo_*` macros (including `%cargo_license` and `%cargo_license_summary`).

Note that the `-n` flag should only be used in exceptional circumstances, for example when enabling a different backend than the one enabled by default, and **MUST NOT** be used to avoid missing dependencies that are part of the `"default"` feature set of a crate.

When passing any of the `-a` or `-n` flags or an `-f` argument to a `%cargo_build` and / or `%cargo_install` macro, the same flags MUST also be passed to `%cargo_license` and `%cargo_license_summary` (if present). Otherwise, the list of generated licenses and the generated license summary will not match what is used when the application or library is compiled.

## Templates

### Non-crate Rust project

```rpm
Name:           my-awesome-project
Version:        25.11.26
Release:        %autorelease
Summary:        My Awesome Rust Project

SourceLicense:  WTFPL
# FIXME: paste output of %%cargo_license_summary here
License:        %{shrink:
    WTFPL AND
    ...
}
# LICENSE.dependencies contains a full license breakdown

URL:            https://forge.example/me/my-awesome-project
Source:         %{url}/archive/v%{version}.tar.gz

BuildRequires:  cargo-rpm-macros

%description
My Awesome Rust Project.

%prep
%autosetup -p1
%cargo_prep

%generate_buildrequires
%cargo_generate_buildrequires -t

%build
%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies

%install
install -Dpm 0755 target/rpm/my-awesome-cli -t %{buildroot}%{_bindir}

%check
%cargo_test

%files
%license LICENSE
%license LICENSE.dependencies
%doc README.md
%{_bindir}/my-awesome-cli

%changelog
%autochangelog
```

### Python project

```rpm
Name:           python-rustypackage
Version:        25.11.26
Release:        %autorelease
Summary:        Rusty Python Package

License:        WTFPL
URL:            https://forge.example/me/python-rustypackage
Source:         %{url}/archive/v%{version}/rustypackage-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  cargo-rpm-macros

%global _description %{expand:
My Rusty Python Package.}

%description %_description

%package     -n python3-rustypackage
Summary:        %{summary}

# FIXME: paste output of %%cargo_license_summary here
License:        %{shrink:
    WTFPL AND
    ...
}
# LICENSE.dependencies contains a full license breakdown

%description -n python3-rustypackage %_description

%prep
%autosetup -n rustypackage-%{version} -p1
%cargo_prep

%generate_buildrequires
# maturin requires all dependencies to be available,
# even those for tests and features that are not enabled
%cargo_generate_buildrequires -a -t
%pyproject_buildrequires

%build
%pyproject_wheel
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies

%install
%pyproject_install
%pyproject_save_files -l rustypackage

%check
%pyproject_check_import
# %%pytest
# %%cargo_test

%files -n python3-rustypackage -f %{pyproject_files}
%doc README.md

%changelog
%autochangelog
```

Verify that project license file(s) **and** the `LICENSE.dependencies` file are included in built packages as expected (`rpm -qL -p <path to RPM>`) when using `%pyproject_save_files -l`.

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
