%global _description %{expand:
Yazi is a terminal file manager written in Rust, based on non-blocking
async I/O.}
%global ssh_config_commit e1012e9f13c6073f559b14206df2ede35720e884

Name:           yazi
Version:        25.5.28
Release:        1%{?dist}
Summary:        Blazing fast terminal file manager
# Cargo licenses are from the cargo license-summary macro. The final terms additionally
# include syntax-source licenses and the GPL-3.0-only SSH grammar license.
License:        %{shrink:
    (MIT OR Apache-2.0) AND NCSA AND
    (MIT OR Apache-2.0) AND Unicode-3.0 AND
    (0BSD OR MIT OR Apache-2.0) AND
    Apache-2.0 AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND
    (Apache-2.0 WITH LLVM-exception) AND
    (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND
    BSD-2-Clause AND (BSD-2-Clause OR Apache-2.0 OR MIT) AND BSD-3-Clause AND
    BSL-1.0 AND CC0-1.0 AND (CC0-1.0 OR Apache-2.0) AND ISC AND MIT AND
    (MIT OR Apache-2.0) AND (MIT OR Apache-2.0 OR CC0-1.0) AND
    (MIT OR Apache-2.0 OR Zlib) AND (MIT OR Zlib OR Apache-2.0) AND MPL-2.0 AND
    (Unlicense OR MIT) AND Zlib AND (Zlib OR Apache-2.0 OR MIT) AND
    CC-BY-SA-3.0 AND BSD-2-Clause-Views AND WTFPL AND GPL-3.0-only AND
    LicenseRef-Fedora-UltraPermissive
}
URL:            https://github.com/sxyazi/yazi
Source0:        %{url}/archive/refs/tags/v%{version}/yazi-%{version}.tar.gz
Source1:        yazi-%{version}-vendor.tar.gz
Source2:        https://github.com/robballou/sublimetext-sshconfig/archive/%{ssh_config_commit}.tar.gz#/yazi-ssh-config-%{ssh_config_commit}.tar.gz
Source3:        yazi-ssh-config-LICENSE.md
Source4:        yazi-%{version}-syntax-sources.tar.gz
Patch0:         yazi-disable-vendored-lua.patch

BuildRequires:  cargo-rpm-macros
BuildRequires:  lua-devel
BuildRequires:  oniguruma-devel

%description %_description

%prep
%autosetup -n yazi-%{version} -p1 -a1
/usr/lib/rpm/rpmuncompress -x %{SOURCE2}
mkdir -p syntax-sources
/usr/bin/tar -xzf %{SOURCE4} -C syntax-sources
cp syntax-sources/syntax-sources/LICENSE.syntaxes LICENSE.syntaxes
# The vendor archive contains target-specific upstream crate source archives.
# Remove prebuilt objects and libraries before any build, as Fedora requires.
find vendor -type f \( -name '*.a' -o -name '*.lib' -o -name '*.o' -o -name '*.so' -o -name '*.dll' -o -name '*.exe' \) -delete
# Some crates mark Rust source files executable; remove that bit so RPM does
# not mistake crate-level #![...] attributes in debug sources for shebangs.
find vendor -type f -name '*.rs' -exec chmod a-x {} +
%cargo_prep -v vendor

%build
export RUSTONIG_SYSTEM_LIBONIG=1
export RUSTONIG_DYNAMIC_LIBONIG=1
%cargo_build
%cargo_license_summary
%{cargo_license} > LICENSE.dependencies
%cargo_vendor_manifest

%install
install -Dpm 0755 target/rpm/yazi -t %{buildroot}%{_bindir}
install -Dpm 0755 target/rpm/ya -t %{buildroot}%{_bindir}
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_licensedir}/%{name}/LICENSE.ssh-config
install -Dpm 0644 LICENSE.syntaxes %{buildroot}%{_licensedir}/%{name}/LICENSE.syntaxes
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_docdir}/%{name}/syntax-sources.tar.gz

%check
export RUSTONIG_SYSTEM_LIBONIG=1
export RUSTONIG_DYNAMIC_LIBONIG=1
%cargo_test

%files
%license LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%license %{_licensedir}/%{name}/LICENSE.ssh-config
%license %{_licensedir}/%{name}/LICENSE.syntaxes
%doc README.md
%doc %{_docdir}/%{name}/syntax-sources.tar.gz
%{_bindir}/yazi
%{_bindir}/ya

%changelog
* Sat Oct 17 2026 Zeldris <zeldrisho@proton.me> - 25.5.28-1
- Initial package with offline dependencies, curated syntax sources, and notices
