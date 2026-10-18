%bcond check 1

# https://github.com/rhysd/actionlint
%global goipath github.com/rhysd/actionlint
Version:        1.7.12
%global tag     v%{version}
%gometa -L -f

Name:           actionlint
Release:        2%{?dist}
Summary:        Static checker for GitHub Actions workflow files

License:        Apache-2.0 AND BSD-3-Clause AND MIT
URL:            %{gourl}
Source0:        %{gosource}
# Generated with Go Vendor Tools (go_vendor_archive create actionlint.spec).
# Checked-in archive keeps Fedora builds offline.
Source1:        %{archivename}-vendor.tar.bz2
Source2:        go-vendor-tools.toml

BuildRequires:  go-vendor-tools
BuildRequires:  rubygem-ronn-ng

# Optional integrations used by actionlint for embedded shell and Python checks.
Recommends:     ShellCheck
Recommends:     python3-pyflakes

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
export GO_LDFLAGS="${GO_LDFLAGS:-} -X %{goipath}.version=%{version}"
%gobuild -o %{gobuilddir}/bin/actionlint %{goipath}/cmd/actionlint
ronn --roff man/actionlint.1.ronn

%install
%go_vendor_license_install -c %{S:2}
install -Dpm0755 %{gobuilddir}/bin/actionlint %{buildroot}%{_bindir}/actionlint
install -Dpm0644 man/actionlint.1 %{buildroot}%{_mandir}/man1/actionlint.1

%check
%go_vendor_license_check -c %{S:2}
%if %{with check}
# Exclude scripts/check-checks: it maintains upstream docs/checks.md and needs shellcheck and pyflakes.
# Skip tests that fetch live HTTP resources; Fedora builds run offline.
# Isolate generator invocations because go test's -skip slash matching applies per subtest component.
%gotest -skip '^(TestDetectErrorBadRequest|TestFetchError|TestFetchRemoteYAML|TestWriteOutdatedActionAsJSONL|TestDetectNewRelease|TestCouldNotFetch|TestFetchURL)$' . ./cmd/actionlint ./scripts/generate-availability ./scripts/generate-webhook-events
%gotest -skip '^(TestDetectErrorBadRequest|TestFetchError|TestFetchRemoteYAML|TestWriteOutdatedActionAsJSONL|TestDetectNewRelease|TestCouldNotFetch|TestFetchURL|TestDetectNoRelease)$' ./scripts/generate-popular-actions
%gotest -run '^TestDetectNoRelease$' -skip '^TestDetectNoRelease$/^no_new_version\.json$' ./scripts/generate-popular-actions
%endif

%files -f %{go_vendor_license_filelist}
%doc README.md CHANGELOG.md docs
%{_bindir}/actionlint
%{_mandir}/man1/actionlint.1*

%changelog
* Fri Oct 16 2026 Zeldris Ho <zeldrisho@proton.me> - 1.7.12-2
- Install upstream documentation and changelog
- Generate only the roff man page
- Recommend ShellCheck and pyflakes for embedded script analysis

* Fri Oct 16 2026 Zeldris Ho <zeldrisho@proton.me> - 1.7.12-1
- Initial package
