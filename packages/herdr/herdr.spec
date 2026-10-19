%global _description %{expand:
Herdr is a terminal workspace manager for coding agents. It provides persistent
terminal workspaces, panes, and agent-aware workflows.}

Name:           herdr
Version:        0.9.5
Release:        2%{?dist}
Summary:        Terminal workspace manager for AI coding agents
License:        %{shrink:
    ((MIT OR Apache-2.0) AND Unicode-3.0) AND
    0BSD AND (0BSD OR Apache-2.0) AND
    (0BSD OR MIT OR Apache-2.0) AND Apache-2.0 AND
    (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND
    (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND
    (BSD-2-Clause OR Apache-2.0) AND MIT AND (MIT OR Apache-2.0) AND
    (MIT OR Apache-2.0 OR LGPL-2.1-or-later) AND
    (MIT OR Zlib OR Apache-2.0) AND (Unlicense OR MIT) AND Zlib AND
    (Zlib OR Apache-2.0 OR MIT) AND ISC AND BSD-3-Clause
}
URL:            https://github.com/herdrdev/herdr
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        herdr-%{version}-vendor.tar.gz
Source2:        herdr-%{version}-zig-deps.tar.gz
Source3:        herdr.1
Patch0:         herdr-%{version}-test-sigpipe.patch

BuildRequires:  cargo-rpm-macros
BuildRequires:  cargo
BuildRequires:  rust >= 1.96.1
BuildRequires:  zig = 0.16.0
BuildRequires:  gcc
BuildRequires:  cmake
# The unit tests create and inspect Git repositories and worktrees.
BuildRequires:  git-core
# packager-only: BuildRequires
BuildRequires:  procps-ng

ExclusiveArch:  x86_64

%description %_description

%prep
%autosetup -n %{name}-%{version} -a1 -N
%autopatch -p1
mkdir -p zig-global-cache
tar -xzf %{SOURCE2} -C zig-global-cache
# Extract license texts for bundled Zig dependencies used by the Linux build.
tar -xOzf zig-global-cache/p/N-V-__8AAGmZhABbsPJLfbqrh6JTHsXhY6qCaLAQyx25e0XE.tar.gz N-V-__8AAGmZhABbsPJLfbqrh6JTHsXhY6qCaLAQyx25e0XE/LICENSE-BSD3 > LICENSE.highway
tar -xOzf zig-global-cache/p/uucode-0.2.0-ZZjBPlK5VADj7fdoq7G8LIHzD5o6FSkcBXXrRWr4jnrA.tar.gz uucode-0.2.0-ZZjBPlK5VADj7fdoq7G8LIHzD5o6FSkcBXXrRWr4jnrA/LICENSE.md > LICENSE.uucode
tar -xOzf zig-global-cache/p/N-V-__8AAP5JWgCGP_AD0teWpa4krRvE9VPZzvviGdbmN4jI.tar.gz N-V-__8AAP5JWgCGP_AD0teWpa4krRvE9VPZzvviGdbmN4jI/LICENSE-APACHE > LICENSE.wuffs-apache
tar -xOzf zig-global-cache/p/N-V-__8AAP5JWgCGP_AD0teWpa4krRvE9VPZzvviGdbmN4jI.tar.gz N-V-__8AAP5JWgCGP_AD0teWpa4krRvE9VPZzvviGdbmN4jI/LICENSE-MIT > LICENSE.wuffs-mit
rm -rf vendor/libghostty-vt/.zig-cache
%cargo_prep -v cargo-vendor

%build
export HERDR_BUILD_CHANNEL=stable
export ZIG_GLOBAL_CACHE_DIR="$PWD/zig-global-cache"
%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%cargo_vendor_manifest

%install
install -Dpm 0644 LICENSE.highway %{buildroot}%{_licensedir}/%{name}/LICENSE.highway
install -Dpm 0644 LICENSE.uucode %{buildroot}%{_licensedir}/%{name}/LICENSE.uucode
install -Dpm 0644 LICENSE.wuffs-apache %{buildroot}%{_licensedir}/%{name}/LICENSE.wuffs-apache
install -Dpm 0644 LICENSE.wuffs-mit %{buildroot}%{_licensedir}/%{name}/LICENSE.wuffs-mit
install -Dpm 0755 target/rpm/herdr %{buildroot}%{_bindir}/herdr
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_mandir}/man1/herdr.1
target/rpm/herdr completion bash > herdr.bash
target/rpm/herdr completion zsh > _herdr
target/rpm/herdr completion fish > herdr.fish
install -Dpm 0644 herdr.bash %{buildroot}%{bash_completions_dir}/herdr
install -Dpm 0644 _herdr %{buildroot}%{zsh_completions_dir}/_herdr
install -Dpm 0644 herdr.fish %{buildroot}%{fish_completions_dir}/herdr.fish

%check
export HERDR_BUILD_CHANNEL=stable
export ZIG_GLOBAL_CACHE_DIR="$PWD/zig-global-cache"
# Integration tests need a running server. Keep tests serial because they
# modify process-wide signal dispositions; the test-only patch also prevents
# CLI output helpers from enabling SIGPIPE's default action in the harness.
export CARGO_PROFILE_RPM_LTO=false
%define rustflags_codegen_units 16
%cargo_test -- --bins -- --test-threads=1
./target/rpm/herdr --version | grep -F '%{version}'
./target/rpm/herdr completion bash >/dev/null

%files
%license LICENSE
%license %{_licensedir}/%{name}/LICENSE.highway
%license %{_licensedir}/%{name}/LICENSE.uucode
%license %{_licensedir}/%{name}/LICENSE.wuffs-apache
%license %{_licensedir}/%{name}/LICENSE.wuffs-mit
%license vendor/libghostty-vt/LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%doc README.md
%{_bindir}/herdr
%{_mandir}/man1/herdr.1*
%{bash_completions_dir}/herdr
%{zsh_completions_dir}/_herdr
%{fish_completions_dir}/herdr.fish

%changelog
* Mon Oct 19 2026 Zeldris Ho <zeldrisho@proton.me> - 0.9.5-2
- Add a manual page

* Sat Oct 17 2026 Zeldris Ho <zeldrisho@proton.me> - 0.9.5-1
- Initial package
