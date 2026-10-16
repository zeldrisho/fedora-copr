---
title: "Golang Packaging Guidelines"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/Golang/"
author:
published:
created: 2026-10-16
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
This document details best practices for packaging Golang packages.

The [previous version](https://docs.fedoraproject.org/en-US/packaging-guidelines/Golang_old/) of these Guidelines involved creating separate `-devel` packages containing the Go source code for each library dependency. As of [Changes/GolangPackagesVendoredByDefault](https://fedoraproject.org/wiki/Changes/GolangPackagesVendoredByDefault), new Go packages MUST be built with vendored dependencies, as outlined in the current version of the Guidelines.

## go2rpm

[go2rpm](https://gitlab.com/fedora/sigs/go/go2rpm) is a tool that automates many of these steps. It is advisable to try `go2rpm --name NAME --profile vendor IMPORT_PATH` first before attempting to write a SPEC by hand. go2rpm will generate a Guidelines-compliant spec file, download the upstream sources, create a vendor archive using `go_vendor_archive` from Go Vendor Tools and then use `go_vendor_license` to scan the upstream sources and vendored dependencies for license files, prompt the user for any licenses it could not detect, and then generate a cumulative SPDX expression.

## Import Path

In Golang, packages are referenced by full URLs listed in the project’s `go.mod` file.

```rpm-spec
%global goipath     github.com/kr/pretty
```

## Naming

New Golang library packages are no longer allowed, so all Golang packages are user-facing applications that MUST be named according to the standard [Naming Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/). In particular, vendored Go packages MUST NOT have a `golang-` prefix, unless that is part of the upstream name of the project.

This also applies to existing packages. When converting a package with a `golang-` prefix that was created under the old guidelines to use vendored dependencies, the package MUST go through the [package rename process](https://docs.fedoraproject.org/en-US/packaging-guidelines/#renaming-or-replacing-existing-packages). This guideline seeks to create a clear separation between packages created under the old approach and the new vendored method and to avoid cases where `-devel` subpackages are removed from existing `golang-` packages and then merged back to stable branches.

## Go Language Architectures

To compile on various architectures, golang and gcc-go compilers are available. The golang compiler currently supports x86, x86\_64, ppc64le, ppc64 (partially, see upstream issue#13192), s390x, armv7hl and aarch64.

Binaries SHOULD set ExclusiveArch so that we only attempt to build packages on those arches. This is now automatically added by the `%gometa` macro by leveraging the `%{golang_arches}` macro. Packagers can exclude `%ix86` (see [Changes/EncourageI686LeafRemoval](https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval)) by passing `-f` to the `%gometa` macro. The `-f` flag tells `%gometa` to set `ExclusiveArch: %{golang_arches_future}` instead of `ExclusiveArch: %{golang_arches}`. `%{golang_arches_future}` includes the same architectures as `{golang_arches}` sans `%ix86`.

## Go compiler flags

### Preserve compiler flags

Packages MUST preserve the Fedora golang compiler flags by using the `%gobuild` macro or by passing the appropriate `%gobuild_*flags` macros to an upstream build script.

```rpm-spec
# Using %gobuild
%gobuild -o %{gobuilddir}/bin/%{name} %{goipath}

# Using a simple upstream build script
%make_build BUILD_OPTS=%{gobuild_baseflags_shescaped}

# Using an upstream build script that provides separate options for ldflags
%make_build \
  BUILD_OPTS=%{gobuild_baseflags_shescaped} \
  GO_LDFLAGS=%{gobuild_ldflags_shescaped}
```

See the inline comments in [macros.go-compilers-golang](https://gitlab.com/fedora/sigs/go/go-rpm-macros/-/blob/main/rpm/macros.d/macros.go-compilers-golang?ref_type=heads) for more information on passing the compiler flags to an upstream build script.

It is recommended to use the `%gobuild` macro if possible. Some upstream build scripts may not provide a proper way to pass additional flags to the compiler or have other issues that can be a source of bugs. When using `%gobuild`, make sure to set the appropriate linker flags and build tags as described below.

### Passing additional flags

Go supports passing additional linker flags (for example, to enable `--version` functionality) and build tags for conditional compilation. When using an upstream build script, these may be set automatically. Otherwise, the packager should set them manually.

Make sure to consult the upstream build process and documentation to determine what linker flags you may need to include to properly encode the version into the binary for projects that provide a flag like `--version` or what build tags to select to enable additional optional features.

#### Linker flags

In some cases, it may be necessary to pass additional flags to the Go linker. This can be accomplished by setting the `$GO_LDFLAGS` environment variable which will then be read by the macros.

```rpm-spec
# The correct value to pass to -X differs between projects; this is an example.
export GO_LDFLAGS="-X %{goipath}/internal.Version=%{version}"
```

Packages MUST NOT set Go linker flags using the `$LDFLAGS` environment variable. This is supported for backwards compatibility, but it is deprecated.

#### Build tags

Go supports build tags to conditionally include or exclude code from the build. To pass build tags to the Go compiler, set `$GO_BUILDTAGS` to a space-separated list of tags.

```rpm-spec
# These tags are just examples. Each project has its own.
export GO_BUILDTAGS="systemd selinux"
```

Packages MUST NOT set Go tags using the `$BUILDTAGS` environment variable.

## Macro dependencies

Packages MUST have `BuildRequires: go-rpm-macros` to pull in the Go macros and compiler.

This is automated by the `%gometa` macro.

Packages that use the `%go_vendor_license_*` macros MUST have `BuildRequires: go-vendor-tools`.

## Vendored dependencies

Packages MUST vendor their Go module dependencies. Packagers SHOULD use the `go_vendor_archive` command from [Go Vendor Tools](https://fedora.gitlab.io/sigs/go/go-vendor-tools/) to generate a reproducible vendor archive. Packages that do not use Go Vendor Tools must include a script or other standardized, documented procedure to download sources with `go mod vendor` and reproducibly produce a tarball. Packagers SHOULD regenerate vendor archives themselves, even if upstreams include a vendor directory in their upstream sources. This allows for easier [security updates using Go Vendor Tools](https://fedora.gitlab.io/sigs/go/go-vendor-tools/scenarios/#security-updates).

Conventionally, `Source0` in the specfile is the primary archive, and `Source1` is the vendor archive, and the values are automatically filled in using the forge macros.

```rpm-spec
Source0:        %{gosource}
# %%archivename is the basename as the archive provided
# by %%gosource without the extension.
Source1:        %{archivename}-vendor.tar.bz2
# go-vendor-tools configuration generated by go2rpm
Source2:        go-vendor-tools.toml
```

Then, run `go_vendor_archive create <PACKAGE_NAME>.spec` to create a vendor tarball.

### Bundled provides

Packages MUST include `bundled(golang(IMPORT_PATH)) = VERSION` Provides for all vendored Go modules. This is handled automatically by [a dependency generator](https://gitlab.com/fedora/sigs/go/go-rpm-macros/-/blob/main/rpm/fileattrs/go_mod_vendor.attr?ref_type=heads). It runs on any `modules.txt` file in a license directory. Mark the `vendor/modules.txt` file with `%license` in `%files`, and then the generator will scan the file and create the `bundled()` Provides. `vendor/modules.txt` is included in `go_vendor_license_filelist` by default (see [Installing licenses](#installing-licenses)) so most packages will not need to do this manually.

```rpm-spec
# Only necessary to include explicitly when not using %%go_vendor_license_filelist
%license vendor/modules.txt
```

## Licensing

Packages must follow the [Fedora Licensing Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/). For vendored Go packages, this means that the license files of the main project as well as all of the vendored Go modules MUST be included in the package and marked with `%license`. Each vendored Go module MUST include a license file; Go modules that are missing license files MUST NOT be included in vendored archives until the licensing is clarified.

Additionally, the package’s `License:` tag MUST include a cumulative SPDX expression encompassing both the main package and the vendored Go modules.

## Licensing with Go Vendor Tools

[Go Vendor Tools](https://fedora.gitlab.io/sigs/go/go-vendor-tools/) provides the `go_vendor_license` command and macros to help determine the correct `License:` expression and install license files as mandated by the previous section.

Packagers MUST run `go_vendor_license report` (either directly, through go2rpm, or using the [%go\_vendor\_license\_check](https://fedora.gitlab.io/sigs/go/go-vendor-tools/man/rpm_macros/#go_vendor_license_check) macro in a *local* mock build) and double check its output before uploading sources to the lookaside cache. Any errors MUST be addressed. If any part of the output is wrong, `go_vendor_license` 's behavior can be modified in [the licensing section of the Go Vendor Tools config file](https://fedora.gitlab.io/sigs/go/go-vendor-tools/config/#licensing).

This document only outlines the standard usage of Go Vendor Tools needed to comply with the Guidelines — consult the [Go Vendor Tools documentation](https://fedora.gitlab.io/sigs/go/go-vendor-tools/) for details on advanced usage. Packagers can follow the scenarios documentation to [generate a new specfile with go2rpm](https://fedora.gitlab.io/sigs/go/go-vendor-tools/scenarios/#generate-go2rpm) or [update existing specfiles for new upstream versions](https://fedora.gitlab.io/sigs/go/go-vendor-tools/scenarios/#manual-update) to run `go_vendor_license` and make sure that the License is valid and automatically update it if necessary before running a full build.

|  | While Go Vendor tools provide facilities to scan for licenses and generate SPDX expressions, it is still the packager’s responsibility to perform a basic check of the output and ensure adherence to the Fedora Licensing Guidelines, including ensuring that all keys in the License tag are allowed licenses in Fedora, before uploading any sources to the lookaside cache.  If necessary, the license expression for individual files can be overridden in the config file, [as outlined in the scenarios documentation](https://fedora.gitlab.io/sigs/go/go-vendor-tools/scenarios/#manually-detecting-licenses). |
| --- | --- |

### go-vendor-tools.toml

Packages MUST include a `go-vendor-tools.toml` file to specify the license detector backend and other configuration options. See the [configuration reference](https://fedora.gitlab.io/sigs/go/go-vendor-tools/config/) for more information. The recommended approach is to use `go2rpm` that automatically creates a valid `go-vendor-tools.toml`. A minimal configuration looks like this:

```toml
[licensing]
detector = "askalono"
```

This file is used by the macros and is conventionally included in the specfile as `Source2:`, just below the upstream archive and the `go_vendor_archive` -generated tarball. In this document, `%{S:2}` (expands to the path to `Source2`) will be used to represent the path to the Go Vendor Tools config file.

### Installing go-vendor-tools

Packages that use the Go Vendor Tools macros MUST have `BuildRequires: go-vendor-tools` and use the [%go\_vendor\_license\_buildrequires](https://fedora.gitlab.io/sigs/go/go-vendor-tools/man/rpm_macros/#go_vendor_license_buildrequires) macro to generate requirements needed for the selected license detector backend.

```rpm-spec
BuildRequires:  go-vendor-tools
```

```rpm-spec
%generate_buildrequires
%go_vendor_license_buildrequires -c %{S:2}
```

### Installing licenses

Packagers SHOULD use the [%go\_vendor\_license\_install](https://fedora.gitlab.io/sigs/go/go-vendor-tools/man/rpm_macros/#go_vendor_license_install) macro to install license files of the main project and all vendored Go modules. By default, this macro will install the license files into main package’s license directory. The macro also copies the `vendor/modules.txt` file to the license directory to enable the Golang `bundled()` generator (see [Bundled provides](#bundled-provides)).

```rpm-spec
# Install into the main package's license directory
%go_vendor_license_install -c %{S:2}
```

Then, the macro will populate [%{go\_vendor\_license\_filelist}](https://fedora.gitlab.io/sigs/go/go-vendor-tools/man/rpm_macros/#go_vendor_license_filelist) with a list of files that can be passed to `%files -f`.

```rpm-spec
%files -f %{go_vendor_license_filelist}
```

### Checking licenses

As stated, packagers MUST check licenses using Go Vendor Tools before uploading sources to the lookaside cache. Any errors raised by `go_vendor_license` MUST be addressed.

As an additional measure, the [%go\_vendor\_license\_check macro](https://fedora.gitlab.io/sigs/go/go-vendor-tools/man/rpm_macros/#go_vendor_license_check) runs the same license scan as the `go_vendor_license report` command. Packages SHOULD use `go_vendor_license_check` in `%check` so the package build will fail if there are any license errors. Go Vendor Tools scans the upstream sources and vendored libraries for license files and generates a cumulative SPDX expression. Also, the macro checks that the expression in the package’s License tag is equivalent (regardless of order or possible expression simplification) to what `go_vendor_license report` expects.

```rpm-spec
# Scan licenses and verify that the License tag is equivalent to what
# go_vendor_license calculates.
%go_vendor_license_check -c %{S:2}

# The macro can also compare a license expression stored in a macro with
# go_vendor_license's output.
%go_vendor_license_check -c %{S:2} %{go_licenses}
```

### In case of missing licenses

`go_vendor_license` checks if any Go module is missing a license file. Again, Go modules that are missing license files MUST NOT be included in vendored archives until the situation is fixed upstream.

In some cases, `go mod vendor` may fail to download a project’s license file, even if it exists for the equivalent version in the upstream repository. This is usually because the license files have non-standard names or because the licenses are installed in a subdirectory instead of the root of the module. In the former case, `go_vendor_archive` MAY be configured using [post\_commands](https://fedora.gitlab.io/sigs/go/go-vendor-tools/config/#archive--post_commands) to download the license file from the upstream repository as a temporary measure, but packagers MUST report this to upstream and ask it to rename the license file to [a format supported by `go mod vendor`](https://github.com/golang/go/blob/ac94297758f3d83fca5ffa16cd179bb098bbd914/src/cmd/go/internal/modcmd/vendor.go#L398-L415). If the license file is included in a subdirectory of a module, the file should be copied to the root directory to satisfy the Go Vendor Tools license checker.

## Testing

You SHOULD run unit tests.

Some tests may be disabled, especially the following kinds of unit tests are incompatible with a secure build environment such as mock:

- tests that call a remote server or API over the Internet,
- tests that attempt to reconfigure the system,
- tests that rely on a specific app running on the system, like a database or syslog server.

If a test is broken for some other reason, you can disable it the same way. However, you SHOULD also report the problem upstream. Remember to trace in a comment why each check was disabled, with links to eventual upstream problem reports.

Tests can be run using [the %gocheck2 macro](https://fedora.gitlab.io/sigs/go/go-vendor-tools/man/rpm_macros/#gocheck2) which calls `go test` internally while preserving the Fedora build flags and providing additional options to skip certain tests.

Packages MUST NOT use the deprecated legacy `%gocheck` macro.

## Go modules mode

Packages SHOULD enable Go modules mode by including `%global gomodulesmode GO111MODULE=on` in the specfile to set the `GO111MODULE` environment variable. Customarily, this definition is included at the beginning of `%build` before the `%gobuild` invocation.

[Go modules](https://go.dev/ref/mod) are the system `go` uses to manage dependencies. Go modules mode replaces `$GOPATH` mode (the previous dependency management system). Go can be configured to use modules or `$GOPATH` mode by setting the [$GO111MODULE environment variable](https://go.dev/ref/mod#mod-commands) to `on`, `off`, or `auto`. `auto` is the upstream default. By default, `%gobuild` in Fedora sets `GO111MODULE=off` for compatibility with the legacy Golang Packaging Guidelines but this approach is not recommended for new packages built with vendored dependencies. Modules mode should be used so `%gobuild` will read modules metadata and include metadata about package dependencies in the binary and to make sure [Go embed](https://pkg.go.dev/embed) works properly.

## Macros

The RPM macros provided by `go-vendor-tools` are used to validate and install licenses. See [Go Vendor Tools RPM Macros docs](https://fedora.gitlab.io/sigs/go/go-vendor-tools/man/rpm_macros/) and [Licensing with Go Vendor Tools](#go-vendor-tools-licensing).

`go-rpm-macros` is primarily responsible for the `%gobuild` macro that calls `go build` with Fedora’s build flags.

`go-rpm-macros` also provides wrappers around the [Forge macros](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/) from the [forge-srpm-macros](https://git.sr.ht/~gotmax23/forge-srpm-macros/) package that makes it easier to specify the Source URL and unpack sources for Go projects hosted on common software forges like Github. These macros include `%gometa`, `%gosource`, and `%goprep`. Packagers can use these macros instead of specifying sources and calling `%autosetup` / `%setup` manually. See [the standalone docs](https://gitlab.com/fedora/sigs/go/go-rpm-macros/-/blob/main/doc/forge-wrappers.adoc?ref_type=heads) and example specfile in these guidelines for more information.

## Example

### go-vendor-tools configuration

These entries were generated automatically by go2rpm. All Go packages MUST have a go-vendor-tools.toml file committed to distgit alongside the specfile.

```toml
[archive]

[licensing]
detector = "askalono"

[[licensing.licenses]]
path = "vendor/github.com/google/shlex/COPYING"
sha256sum = "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
expression = "Apache-2.0"

[[licensing.licenses]]
path = "vendor/github.com/jwalton/gchalk/LICENSE-chalk"
sha256sum = "44e453533edb9f1c037cb260c58f66f1d9b2e7823a07407cd6d04320e3925fea"
expression = "MIT"

[[licensing.licenses]]
path = "vendor/github.com/jwalton/gchalk/pkg/ansistyles/LICENSE-ansi-styles"
sha256sum = "310f4b4de77142b34acc5a58de93558fde5dea75891c7822b4086f71372ec983"
expression = "MIT"

[[licensing.licenses]]
path = "vendor/github.com/jwalton/go-supportscolor/LICENSE"
sha256sum = "892282511d65ac08025fbabcd8af330d0aa94e459d81a818251ff5a934383816"
expression = "MIT"

[[licensing.licenses]]
path = "vendor/gopkg.in/yaml.v3/LICENSE"
sha256sum = "d18f6323b71b0b768bb5e9616e36da390fbd39369a81807cca352de4e4e6aa0b"
expression = "MIT AND (MIT AND Apache-2.0)"
```

### Specfile with forge macro wrappers

This is the default method used by go2rpm and is the current convention for Go packages.

```rpm-spec
# Generated by go2rpm 1.17.1 (with extra code comments added manually)
%bcond check 1

# https://github.com/noborus/ov
%global goipath         github.com/noborus/ov
Version:                0.43.0

%gometa -L -f

Name:           ov
Release:        %autorelease
Summary:        Feature-rich terminal-based text viewer

# Generated by go-vendor-tools
License:        Apache-2.0 AND BSD-3-Clause AND MIT AND MPL-2.0
URL:            %{gourl}
Source0:        %{gosource}
# Generated by go-vendor-tools
Source1:        %{archivename}-vendor.tar.bz2
# Go Vendor Tools configuration generated by go2rpm
Source2:        go-vendor-tools.toml

BuildRequires:  go-vendor-tools

%description
Feature-rich terminal-based text viewer. It is a so-called terminal pager.

%prep
# Unpack upstream sources (Source0) and apply patches if they exist.
# This also creates the %%{gobuilddir} directory used to store the binary built
# during %%build.
%goprep -p1
# Unpack the vendor archive in Source1.
tar -xf %{S:1}

%generate_buildrequires
# Install license scanner dependencies.
%go_vendor_license_buildrequires -c %{S:2}

%build
# Enable Go modules mode as required by the Guidelines.
%global gomodulesmode GO111MODULE=on
# Set version in binary. The exact value to pass to -X differs by project.
export GO_LDFLAGS="-X main.Version=%{version}"
# Build the binary
%gobuild -o %{gobuilddir}/bin/ov %{goipath}
# Generate shell completions
%{gobuilddir}/bin/%{name} --completion bash > %{name}.bash
%{gobuilddir}/bin/%{name} --completion fish > %{name}.fish
%{gobuilddir}/bin/%{name} --completion zsh  > %{name}.zsh

%install
# Install license files
%go_vendor_license_install -c %{S:2}

# Install binaries built during %%build
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/

# Install shell completions generated during %%build
install -Dpm 0644 ov.bash %{buildroot}%{bash_completions_dir}/ov
install -Dpm 0644 ov.fish %{buildroot}%{fish_completions_dir}/ov.fish
install -Dpm 0644 ov.zsh  %{buildroot}%{zsh_completions_dir}/_ov

%check
# Perform license check
%go_vendor_license_check -c %{S:2}
# Run Go unit tests
%if %{with check}
%gocheck2
%endif

%files -f %{go_vendor_license_filelist}
%doc README.md
%{_bindir}/ov
%{bash_completions_dir}/ov
%{fish_completions_dir}/ov.fish
%{zsh_completions_dir}/_ov

%changelog
%autochangelog
```

### Specfile with manual defintions

This above approach is used by default in go2rpm but Go packages can also be built without the forge macros. Be sure to include the manual dependency on `go-rpm-macros` and the appropriate ExclusiveArch invocation.

```rpm-spec
%bcond check 1

Name:           ov
Version:        0.43.0
Release:        %autorelease
Summary:        Feature-rich terminal-based text viewer
# Generated by go-vendor-tools
License:        Apache-2.0 AND BSD-3-Clause AND MIT AND MPL-2.0
URL:            https://github.com/noborus/ov
Source0:        %{url}/archive/v%{version}/ov-%{version}.tar.gz
# Generated by go-vendor-tools
Source1:        ov-%{version}-vendor.tar.bz2
Source2:        go-vendor-tools.toml

ExclusiveArch:  %{golang_arches_future}
BuildRequires:  go-rpm-macros
BuildRequires:  go-vendor-tools

%description
Feature-rich terminal-based text viewer. It is a so-called terminal pager.

%prep
# Unpack upstream sources (Source0) and apply patches if they exist.
%autosetup -p1
# Unpack the vendor archive in Source1.
tar -xf %{S:1}

%generate_buildrequires
# Install license scanner dependencies.
%go_vendor_license_buildrequires -c %{S:2}

%build
# Enable Go modules mode as required by the Guidelines.
%global gomodulesmode GO111MODULE=on
# Set version in binary. The exact value to pass to -X differs by project.
export GO_LDFLAGS="-X main.Version=%{version}"
# Build the binary
%gobuild -o ov .
# Generate shell completions
./ov --completion bash > ov.bash
./ov --completion fish > ov.fish
./ov --completion zsh  > ov.zsh

%install
# Install license files
%go_vendor_license_install -c %{S:2}

# Install binaries built during %%build
install -Dp ./ov -t %{buildroot}%{_bindir}

# Install shell completions generated during %%build
install -Dpm 0644 ov.bash %{buildroot}%{bash_completions_dir}/ov
install -Dpm 0644 ov.fish %{buildroot}%{fish_completions_dir}/ov.fish
install -Dpm 0644 ov.zsh  %{buildroot}%{zsh_completions_dir}/_ov

%check
# Perform license check
%go_vendor_license_check -c %{S:2}
# Run Go unit tests
%if %{with check}
%gocheck2
%endif

%files -f %{go_vendor_license_filelist}
%doc README.md
%{_bindir}/ov
%{bash_completions_dir}/ov
%{fish_completions_dir}/ov.fish
%{zsh_completions_dir}/_ov

%changelog
%autochangelog
```

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
