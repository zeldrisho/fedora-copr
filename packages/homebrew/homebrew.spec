Name:           homebrew
Version:        7.0.13
Release:        1%{?dist}
Summary:        The Homebrew package manager for Linux
# Upstream is BSD-2-Clause; vendored components include MIT. Further audit needed.
License:        BSD-2-Clause AND MIT
URL:            https://github.com/Homebrew/brew
Source0:        https://github.com/Homebrew/brew/archive/refs/tags/%{version}.tar.gz
Source1:        brew

BuildArch:      noarch
Requires:       bash coreutils curl file git-core gzip procps-ng sudo tar util-linux
# Homebrew expects a system compiler even when installing bottles.
Requires:       gcc

%description
Homebrew is a package manager for Linux and macOS. This package provides a
read-only seed and a first-run launcher for a separate, self-updating
installation owned by the user who initializes it.

%prep
%autosetup -n brew-%{version}

%build

%install
install -Dpm 0644 %{SOURCE0} %{buildroot}%{_datadir}/homebrew/seed.tar.gz
install -Dpm 0755 %{SOURCE1} %{buildroot}%{_bindir}/brew
printf '%%s\n' '%{version}' > %{buildroot}%{_datadir}/homebrew/version

%check
test -x bin/brew
bash -n %{SOURCE1}

%files
%license LICENSE.txt
%doc README.md
%{_datadir}/homebrew
%{_bindir}/brew

%changelog
