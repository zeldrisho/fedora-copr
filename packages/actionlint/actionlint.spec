Name:           actionlint
Version:        1.7.12
Release:        1%{?dist}
Summary:        Static checker for GitHub Actions workflows

# Provisional: the full linked-dependency license audit is still outstanding.
License:        MIT AND BSD-3-Clause AND Apache-2.0
URL:            https://github.com/rhysd/actionlint
Source0:        https://github.com/rhysd/actionlint/archive/refs/tags/v%{version}.tar.gz
# Generated from go.mod and go.sum by prepare-sources.sh.
Source1:        %{name}-%{version}-deps.tar.gz

ExclusiveArch:  x86_64 aarch64
BuildRequires:  go-rpm-macros
BuildRequires:  golang >= 1.25
BuildRequires:  gcc
BuildRequires:  rubygem-ronn-ng
Recommends:     ShellCheck
Recommends:     python3-pyflakes

%description
actionlint checks GitHub Actions workflows for errors in syntax, expressions,
action inputs, and other common mistakes.

%prep
%autosetup -n %{name}-%{version} -a 1

%build
%global gomodulesmode GO111MODULE=on
export GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local GOFLAGS=-mod=vendor
export GO_LDFLAGS="-X github.com/rhysd/actionlint.version=%{version}"
%gobuild -o actionlint ./cmd/actionlint
ronn --roff man/actionlint.1.ronn

%install
install -Dpm 0755 actionlint %{buildroot}%{_bindir}/actionlint
install -Dpm 0644 man/actionlint.1 %{buildroot}%{_mandir}/man1/actionlint.1
# Preserve dependency notices until their full license expressions are audited.
mkdir -p dependency-licenses
find vendor -type f \( -iname 'license*' -o -iname 'copying*' -o -iname 'copyleft*' -o -iname 'copyright*' -o -iname 'legal*' -o -iname 'notice*' -o -iname 'authors*' -o -iname 'contributors*' -o -iname 'patents*' \) -exec cp --parents -t dependency-licenses {} +
# Fail closed if the known linked dependencies' license notices disappear.
for notice in vendor/golang.org/x/sync/LICENSE vendor/go.yaml.in/yaml/v4/LICENSE vendor/go.yaml.in/yaml/v4/NOTICE; do
    test -s "dependency-licenses/$notice"
done

%check
export GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local GOFLAGS=-mod=vendor
./actionlint -version | grep -F '%{version}'
./actionlint -shellcheck= -pyflakes= testdata/ok/allow_any_outputs.yaml
if ./actionlint -shellcheck= -pyflakes= testdata/err/one_error.yaml; then
    echo 'Expected invalid workflow to fail' >&2
    exit 1
fi
# Maintenance generators assume a Git checkout or live GitHub responses.
# Keep the core tests and other generator tests; do not require network access.
go list ./... > test-packages.txt
grep -vE '/scripts/(check-checks|generate-popular-actions)$' test-packages.txt > selected-test-packages.txt
# These tests contact GitHub for a successful response and HTTP 404 handling.
xargs -r go test -skip '^TestFetchURL$|^TestFetchError$/^not_found$' < selected-test-packages.txt

%files
%license LICENSE.txt dependency-licenses
%doc README.md docs
%{_bindir}/actionlint
%{_mandir}/man1/actionlint.1*

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 1.7.12-1
- Initial package
