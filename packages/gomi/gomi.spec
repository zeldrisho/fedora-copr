Name:           gomi
Version:        1.10.1
Release:        1%{?dist}
Summary:        Move files to the trash instead of deleting them

# Upstream is MIT; the full vendored dependency license expression is not audited.
License:        MIT
URL:            https://github.com/babarot/gomi
Source0:        https://github.com/babarot/gomi/archive/refs/tags/v%{version}.tar.gz
# Generated from go.mod and go.sum by prepare-sources.sh.
Source1:        %{name}-%{version}-deps.tar.gz

ExclusiveArch:  x86_64 aarch64
BuildRequires:  go-rpm-macros
BuildRequires:  golang >= 1.26
BuildRequires:  gcc

%description
gomi moves files to the trash and provides a terminal interface to browse and
restore them. It supports the XDG Trash specification on Linux.

%prep
%autosetup -n %{name}-%{version} -a 1

%build
%global gomodulesmode GO111MODULE=on
export GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local GOFLAGS=-mod=vendor
export GO_LDFLAGS="-X main.version=v%{version}"
%gobuild -o gomi .

%install
install -Dpm 0755 gomi %{buildroot}%{_bindir}/gomi
# Preserve dependency notices pending a complete license audit.
mkdir -p dependency-licenses
find vendor -type f \( -iname 'license*' -o -iname 'copying*' -o -iname 'notice*' -o -iname 'authors*' \) -exec cp --parents -t dependency-licenses {} +

%check
export GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local GOFLAGS=-mod=vendor
export HOME=$(mktemp -d)
trap 'rm -rf "$HOME"' EXIT
export XDG_CONFIG_HOME="$HOME/config" XDG_DATA_HOME="$HOME/data" XDG_CACHE_HOME="$HOME/cache"
./gomi --version | grep -F '%{version}'
mkdir -p "$XDG_CONFIG_HOME/gomi" "$XDG_DATA_HOME" "$XDG_CACHE_HOME"
printf 'core:\n  trash:\n    strategy: xdg\n' > "$XDG_CONFIG_HOME/gomi/config.yaml"
printf 'gomi smoke test\n' > "$HOME/example"
./gomi "$HOME/example"
test ! -e "$HOME/example"
grep -Fx 'gomi smoke test' "$XDG_DATA_HOME/Trash/files/example"
test -f "$XDG_DATA_HOME/Trash/info/example.trashinfo"
go test ./...

%files
%license LICENSE dependency-licenses vendor/modules.txt
%doc README.md
%{_bindir}/gomi

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 1.10.1-1
- Initial package
