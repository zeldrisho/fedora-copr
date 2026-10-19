%global _description %{expand:
Yazi is a terminal file manager written in Rust, based on non-blocking
async I/O.}
%global ssh_config_commit e1012e9f13c6073f559b14206df2ede35720e884
%global yazi_commit 8dd895c695a5950330c2623eb43debf323b60654

Name:           yazi
Version:        26.9.1
Release:        4%{?dist}
Summary:        Blazing fast terminal file manager
# Include syntax-source licenses and the GPL-3.0-only SSH grammar license.
License:        %{shrink:
    ((MIT OR Apache-2.0) AND Unicode-3.0) AND
    (0BSD OR MIT OR Apache-2.0) AND Apache-2.0 AND
    (Apache-2.0 AND ISC) AND (Apache-2.0 OR ISC OR MIT) AND
    (Apache-2.0 OR MIT) AND
    (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND
    (BSD-2-Clause OR Apache-2.0 OR MIT) AND BSD-3-Clause AND
    (BSD-3-Clause OR Apache-2.0) AND BSL-1.0 AND BlueOak-1.0.0 AND
    CC0-1.0 AND CDLA-Permissive-2.0 AND ISC AND MIT AND
    (MIT OR Apache-2.0) AND (MIT OR Apache-2.0 OR BSD-1-Clause) AND
    (MIT OR Apache-2.0 OR LGPL-2.1-or-later) AND
    (MIT OR Apache-2.0 OR Zlib) AND (MIT OR Zlib OR Apache-2.0) AND
    MPL-2.0 AND Unicode-3.0 AND (Unlicense OR MIT) AND Zlib AND
    (Zlib OR Apache-2.0 OR MIT) AND BSD-2-Clause-Views AND WTFPL AND
    GPL-3.0-only AND
    LicenseRef-Fedora-UltraPermissive
}
URL:            https://github.com/sxyazi/yazi
Source0:        %{url}/archive/refs/tags/v%{version}/yazi-%{version}.tar.gz
Source1:        yazi-%{version}-vendor.tar.gz
Source2:        https://github.com/robballou/sublimetext-sshconfig/archive/%{ssh_config_commit}.tar.gz#/yazi-ssh-config-%{ssh_config_commit}.tar.gz
Source3:        yazi-ssh-config-LICENSE.md
Source4:        yazi-%{version}-syntax-sources.tar.gz
Source5:        yazi.1
Source6:        ya.1
Source7:        yazi-ssh-config-NOTICE.md
Patch0:         yazi-disable-vendored-lua.patch
Patch1:         yazi-lua54-f44.patch
Patch2:         yazi-lua54-api.patch
Patch3:         yazi-git-sha.patch

BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  rust >= 1.95.0
BuildRequires:  lua-devel
BuildRequires:  oniguruma-devel

Requires:       file
Recommends:     7zip
Recommends:     ffmpeg-free
Recommends:     fd-find
Recommends:     fzf
Recommends:     ImageMagick
Recommends:     jq
Recommends:     poppler-utils
Recommends:     ripgrep
Recommends:     zoxide

%description %_description

%prep
%autosetup -n yazi-%{version} -p1 -a1 -N
%patch -P0 -p1
%patch -P3 -p1
%if 0%{?fedora} < 45
%patch -P1 -p1
%patch -P2 -p1
%endif
/usr/lib/rpm/rpmuncompress -x %{SOURCE2}
mkdir -p syntax-sources
/usr/bin/tar -xzf %{SOURCE4} -C syntax-sources
cp syntax-sources/syntax-sources/LICENSE.syntaxes LICENSE.syntaxes
# Remove prebuilt objects and libraries from vendored crates before building.
find vendor -type f \( -name '*.a' -o -name '*.lib' -o -name '*.o' -o -name '*.so' -o -name '*.dll' -o -name '*.exe' \) -delete
find vendor -type f -name '*.rs' -exec chmod a-x {} +
%cargo_prep -v vendor
# Use the vendored source for the forked ratatui Git dependency.
cat >> .cargo/config.toml <<'EOF'
[source."git+https://github.com/yazi-rs/ratatui.git?branch=fix_buffer_diff_wide_cells"]
git = "https://github.com/yazi-rs/ratatui.git"
branch = "fix_buffer_diff_wide_cells"
replace-with = "vendored-sources"
EOF

%build
export YAZI_GEN_COMPLETIONS=1
export VERGEN_GIT_SHA=%{yazi_commit}
export JEMALLOC_SYS_WITH_LG_PAGE=14
export RUSTONIG_SYSTEM_LIBONIG=1
export RUSTONIG_DYNAMIC_LIBONIG=1
%cargo_build
%cargo_license_summary
%{cargo_license} > LICENSE.dependencies
%cargo_vendor_manifest

%install
install -Dpm 0755 target/rpm/yazi -t %{buildroot}%{_bindir}
install -Dpm 0755 target/rpm/ya -t %{buildroot}%{_bindir}
install -Dpm 0644 yazi-boot/completions/yazi.bash %{buildroot}%{bash_completions_dir}/yazi.bash
install -Dpm 0644 yazi-cli/completions/ya.bash %{buildroot}%{bash_completions_dir}/ya.bash
install -Dpm 0644 yazi-boot/completions/yazi.fish %{buildroot}%{fish_completions_dir}/yazi.fish
install -Dpm 0644 yazi-cli/completions/ya.fish %{buildroot}%{fish_completions_dir}/ya.fish
install -Dpm 0644 yazi-boot/completions/_yazi %{buildroot}%{zsh_completions_dir}/_yazi
install -Dpm 0644 yazi-cli/completions/_ya %{buildroot}%{zsh_completions_dir}/_ya
install -Dpm 0644 %{SOURCE5} %{buildroot}%{_mandir}/man1/yazi.1
install -Dpm 0644 %{SOURCE6} %{buildroot}%{_mandir}/man1/ya.1
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_licensedir}/%{name}/LICENSE.ssh-config
install -Dpm 0644 %{SOURCE7} %{buildroot}%{_licensedir}/%{name}/NOTICE.ssh-config
install -Dpm 0644 LICENSE.syntaxes %{buildroot}%{_licensedir}/%{name}/LICENSE.syntaxes
install -Dpm 0644 %{SOURCE4} %{buildroot}%{_docdir}/%{name}/syntax-sources.tar.gz

%check
./target/rpm/yazi --version | grep -F '%{version}'
./target/rpm/ya --version | grep -F '%{version}'

%files
%license LICENSE
%license LICENSE.dependencies
%license cargo-vendor.txt
%license %{_licensedir}/%{name}/LICENSE.ssh-config
%license %{_licensedir}/%{name}/NOTICE.ssh-config
%license %{_licensedir}/%{name}/LICENSE.syntaxes
%doc README.md
%doc %{_docdir}/%{name}/syntax-sources.tar.gz
%{_bindir}/yazi
%{_bindir}/ya
%{bash_completions_dir}/yazi.bash
%{bash_completions_dir}/ya.bash
%{fish_completions_dir}/yazi.fish
%{fish_completions_dir}/ya.fish
%{zsh_completions_dir}/_yazi
%{zsh_completions_dir}/_ya
%{_mandir}/man1/yazi.1*
%{_mandir}/man1/ya.1*

%changelog
* Mon Oct 19 2026 Zeldris Ho <zeldrisho@proton.me> - 26.9.1-4
- Restore the MIT-licensed Strace grammar in the syntax database

* Mon Oct 19 2026 Zeldris Ho <zeldrisho@proton.me> - 26.9.1-3
- Remove licenses found only in unlinked source files from the binary expression

* Mon Oct 19 2026 Zeldris Ho <zeldrisho@proton.me> - 26.9.1-2
- Remove syntax grammars without verified redistribution grants or source provenance

* Sat Oct 17 2026 Zeldris Ho <zeldrisho@proton.me> - 26.9.1-1
- Initial package
