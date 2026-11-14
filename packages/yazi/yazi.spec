Name:           yazi
Version:        26.9.1
Release:        1%{?dist}
Summary:        Asynchronous terminal file manager

# Bundled Rust dependencies and Lua have not yet been audited for licensing.
License:        MIT
URL:            https://github.com/sxyazi/yazi
Source0:        https://github.com/sxyazi/yazi/archive/refs/tags/v%{version}.tar.gz
# Generated from Cargo.lock by prepare-sources.sh.
Source1:        %{name}-%{version}-deps.tar.gz

ExclusiveArch:  x86_64 aarch64
BuildRequires:  cargo >= 1.95.0
BuildRequires:  rust >= 1.95.0
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  make
Requires:       file
# Use command providers: Fedora's ffmpeg-free and 7zip supply these tools.
Recommends:     /usr/bin/ffmpeg
Recommends:     /usr/bin/ffprobe
Recommends:     /usr/bin/7z
Recommends:     jq
Recommends:     poppler-utils
Recommends:     fd-find
Recommends:     ripgrep
Recommends:     fzf
Recommends:     zoxide
Recommends:     resvg
Recommends:     ImageMagick
Recommends:     git

%description
Yazi is an asynchronous terminal file manager written in Rust.

%prep
%autosetup -n %{name}-%{version} -a 1
# Yazi enables Lua 5.5; fail closed if the vendored header is missing or ambiguous.
# Lua's copyright and permission notice is at the end of the header.
shopt -s nullglob
lua_headers=(cargo-vendor/lua-src-*/lua-5.5.*/lua.h)
if [ "${#lua_headers[@]}" -ne 1 ]; then
    echo "Expected exactly one vendored Lua 5.5 header, found ${#lua_headers[@]}" >&2
    exit 1
fi
cp "${lua_headers[0]}" LICENSE-LUA
shopt -u nullglob

%build
%set_build_flags
# Oniguruma's bundled C sources need pre-C23 semantics with recent GCC.
export CFLAGS="$CFLAGS -std=gnu17"
export YAZI_GEN_COMPLETIONS=1
export JEMALLOC_SYS_WITH_LG_PAGE=14
export CARGO_PROFILE_RELEASE_STRIP=false
cargo build --release --locked --offline --jobs %{_smp_build_ncpus}

%install
install -Dpm 0755 -t %{buildroot}%{_bindir} target/release/yazi target/release/ya
install -Dpm 0644 -t %{buildroot}%{_datadir}/bash-completion/completions yazi-boot/completions/yazi.bash yazi-cli/completions/ya.bash
install -Dpm 0644 -t %{buildroot}%{_datadir}/fish/vendor_completions.d yazi-boot/completions/yazi.fish yazi-cli/completions/ya.fish
install -Dpm 0644 -t %{buildroot}%{_datadir}/zsh/site-functions yazi-boot/completions/_yazi yazi-cli/completions/_ya

%check
%set_build_flags
export CFLAGS="$CFLAGS -std=gnu17"
export JEMALLOC_SYS_WITH_LG_PAGE=14
target/release/yazi --version
target/release/ya --version
cargo test --locked --offline --jobs %{_smp_build_ncpus}

%files
%license LICENSE LICENSE-ICONS LICENSE-LUA
%doc README.md
%{_bindir}/yazi
%{_bindir}/ya
%{_datadir}/bash-completion/completions/yazi.bash
%{_datadir}/bash-completion/completions/ya.bash
%{_datadir}/fish/vendor_completions.d/yazi.fish
%{_datadir}/fish/vendor_completions.d/ya.fish
%{_datadir}/zsh/site-functions/_yazi
%{_datadir}/zsh/site-functions/_ya

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 26.9.1-1
- Initial package
