%global _description %{expand:
Herdr is a terminal workspace manager for coding agents. It provides persistent
terminal workspaces, panes, and agent-aware workflows.}

Name:           herdr
Version:        0.9.5
Release:        1%{?dist}
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
    (Zlib OR Apache-2.0 OR MIT) AND ISC
}
URL:            https://github.com/herdrdev/herdr
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        herdr-%{version}-vendor.tar.gz
Source2:        herdr-%{version}-zig-deps.tar.gz

BuildRequires:  cargo-rpm-macros
BuildRequires:  cargo
BuildRequires:  rust >= 1.96.1
BuildRequires:  zig = 0.16.0
BuildRequires:  gcc
BuildRequires:  cmake
# The unit tests create and inspect Git repositories and worktrees.
BuildRequires:  git-core

ExclusiveArch:  x86_64 aarch64

%description %_description

%prep
%autosetup -n %{name}-%{version} -a1 -N
mkdir -p zig-global-cache
# Includes the exact Zig package archives used by the Linux libghostty-vt build.
tar -xzf %{SOURCE2} -C zig-global-cache
# Clean tool-generated state and initialize Cargo's offline vendor configuration.
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
install -Dpm 0755 target/rpm/herdr %{buildroot}%{_bindir}/herdr
target/rpm/herdr completion bash > herdr.bash
target/rpm/herdr completion zsh > _herdr
target/rpm/herdr completion fish > herdr.fish
install -Dpm 0644 herdr.bash %{buildroot}%{bash_completions_dir}/herdr
install -Dpm 0644 _herdr %{buildroot}%{zsh_completions_dir}/_herdr
install -Dpm 0644 herdr.fish %{buildroot}%{fish_completions_dir}/herdr.fish

%check
export HERDR_BUILD_CHANNEL=stable
export ZIG_GLOBAL_CACHE_DIR="$PWD/zig-global-cache"
# The integration tests start live Herdr servers, which do not come up inside the
# Mock build environment (the server socket never appears), so run the unit tests.
%cargo_test -- --bins
./target/rpm/herdr --version | grep -F '%{version}'
./target/rpm/herdr completion bash >/dev/null

%files
%license LICENSE
%license vendor/libghostty-vt/LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%doc README.md
%{_bindir}/herdr
%{bash_completions_dir}/herdr
%{zsh_completions_dir}/_herdr
%{fish_completions_dir}/herdr.fish

%changelog
* Sat Oct 17 2026 Zeldris Ho <zeldrisho@proton.me> - 0.9.5-1
- Initial package
