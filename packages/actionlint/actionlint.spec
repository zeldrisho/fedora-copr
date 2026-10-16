%bcond check 1

# https://github.com/rhysd/actionlint
%global goipath github.com/rhysd/actionlint
Version:        1.7.12
%global tag     v%{version}
%gometa -L -f

Name:           actionlint
Release:        1%{?dist}
Summary:        Static checker for GitHub Actions workflow files

License:        Apache-2.0 AND BSD-3-Clause AND MIT
URL:            %{gourl}
Source0:        %{gosource}
# Checked-in generated source keeps Fedora builds offline.
Source1:        %{archivename}-vendor.tar.bz2
Source2:        go-vendor-tools.toml

BuildRequires:  go-vendor-tools
BuildRequires:  make
BuildRequires:  rubygem-ronn-ng

%description
Actionlint is a static checker for GitHub Actions workflow files. It checks
workflow syntax, expression types, action inputs and outputs, and detects
common security and configuration mistakes.

%prep
%goprep -p1
tar -xf %{S:1}

%generate_buildrequires
%go_vendor_license_buildrequires -c %{S:2}

%build
%global gomodulesmode GO111MODULE=on
export GO_LDFLAGS="${GO_LDFLAGS:-${LDFLAGS:-}} -X %{goipath}.version=%{version}"
%gobuild -o %{gobuilddir}/bin/actionlint %{goipath}/cmd/actionlint
%make_build man

%install
%go_vendor_license_install -c %{S:2}
install -Dpm0755 %{gobuilddir}/bin/actionlint %{buildroot}%{_bindir}/actionlint
install -Dpm0644 man/actionlint.1 %{buildroot}%{_mandir}/man1/actionlint.1

%check
%go_vendor_license_check -c %{S:2}
%if %{with check}
# Exclude the generator utility whose tests require Git metadata omitted from the release archive.
# Skip tests that fetch live HTTP resources; Fedora builds run offline.
%gotest -skip '^(TestDetectErrorBadRequest|TestFetchError|TestFetchRemoteYAML|TestWriteOutdatedActionAsJSONL|TestDetectNewRelease|TestDetectNoRelease/no_new_version\.json|TestCouldNotFetch|TestFetchURL)$' . ./cmd/actionlint ./scripts/generate-availability ./scripts/generate-popular-actions ./scripts/generate-webhook-events
%endif

%files -f %{go_vendor_license_filelist}
%doc README.md
%{_bindir}/actionlint
%{_mandir}/man1/actionlint.1*

%changelog
* Fri Oct 16 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 1.7.12-1
- Start at the initial release; earlier COPR builds failed before publishing
- Skip network-dependent tests in offline Fedora builds
