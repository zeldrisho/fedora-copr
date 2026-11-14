# Upstream npm native binaries lack build IDs and debug information.
%undefine _missing_build_ids_terminate_build
%global _build_id_links none

Name:           vite-plus
Version:        1.6.0
Release:        1%{?dist}
Summary:        Unified toolchain for web development

# Provisional: bundled Rust and JavaScript dependency licenses need review.
License:        MIT
URL:            https://github.com/voidzero-dev/vite-plus
Source0:        https://github.com/voidzero-dev/vite-plus/archive/refs/tags/v%{version}.tar.gz
Source1:        %{name}-%{version}-git-sources.tar.gz
Source2:        sync-workspace.sh
# License texts for the upstream npm native components.
Source3:        https://github.com/rufl/zigpty/archive/refs/tags/v0.2.1.tar.gz#/zigpty-0.2.1.tar.gz
Source4:        https://github.com/yuku-toolchain/yuku/archive/refs/tags/v0.19.0.tar.gz#/yuku-0.19.0.tar.gz
Source6:        checksums.sha256

ExclusiveArch:  x86_64 aarch64
BuildRequires:  nodejs24
# Fedora's small-ICU Node crashes in Intl.Segmenter without the full data.
BuildRequires:  nodejs24-full-i18n
BuildRequires:  nodejs24-npm
BuildRequires:  rustup
BuildRequires:  cargo-rpm-macros
BuildRequires:  git-core
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  pkgconf-pkg-config
BuildRequires:  sqlite-devel
BuildRequires:  python3
Requires:       nodejs24
Requires:       nodejs24-full-i18n

%description
Vite+ provides the vp command for web development, including Vite, Vitest,
Rolldown, linting, formatting, package management, and task execution.

%prep
(cd %{_sourcedir} && sha256sum -c %{SOURCE6})
%autosetup -n vite-plus-%{version}
# Extract only notices, not Yuku's intentionally invalid TypeScript fixtures.
tar -xOzf %{SOURCE3} zigpty-0.2.1/LICENSE > LICENSE-ZIGPTY
tar -xOzf %{SOURCE4} yuku-0.19.0/LICENSE > LICENSE-YUKU
mkdir -p git-sources
tar -xzf %{SOURCE1} -C git-sources
for archive in git-sources/rolldown-*.tar.gz git-sources/vite-*.tar.gz git-sources/oxc-node-*.tar.gz; do
    tar -xzf "$archive" -C .
done

%build
%set_build_flags
# COPR build networking must be explicitly enabled: pnpm dependencies, Rust
# toolchain components and Cargo dependencies are downloaded during the build.
export HOME="$PWD/build-home"
mkdir -p "$HOME" "$PWD/build-bin"
ln -s /usr/bin/node-24 "$PWD/build-bin/node"
ln -s /usr/bin/npm-24 "$PWD/build-bin/npm"
ln -s /usr/bin/rustup-init "$PWD/build-bin/rustup"
ln -s /usr/bin/rustup-init "$PWD/build-bin/cargo"
ln -s /usr/bin/rustup-init "$PWD/build-bin/rustc"
export RUSTFLAGS="$RUSTFLAGS --cfg tokio_unstable"
export PATH="$PWD/build-bin:$PATH"
export RUSTUP_HOME="$HOME/rustup" CARGO_HOME="$HOME/cargo"
rust_toolchain=$(python3 -c 'import tomllib; print(tomllib.load(open("rust-toolchain.toml", "rb"))["toolchain"]["channel"])')
case "$rust_toolchain" in nightly-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]) ;; *) echo 'Unexpected Rust toolchain' >&2; exit 1 ;; esac
rustup toolchain install "$rust_toolchain" --profile minimal --component rust-src
export PATH="$CARGO_HOME/bin:$PATH"
pnpm_package=$(node -p 'const p = require("./package.json").packageManager; if (!/^pnpm@[0-9]+\.[0-9]+\.[0-9]+$/.test(p)) throw Error("Unsupported packageManager"); p')
npm install --prefix "$PWD/build-tools" --ignore-scripts --no-audit --no-fund "$pnpm_package"
export PATH="$PWD/build-tools/node_modules/.bin:$PATH"
export LIBSQLITE3_SYS_USE_PKG_CONFIG=1
# Fail early if the Node ICU data required by build-time formatting is absent.
node -e 'if ([...new Intl.Segmenter("en").segment("test")].length !== 4) process.exit(1)'
# The sync helper uses the verified source snapshots and checks both lockfiles.
bash %{SOURCE2} "$PWD"
pnpm build
cargo build --release --locked -p vp_global_cli
# Production deploy omits some patched build dependencies. Keep patch failures
# fatal, but allow patches whose dependencies are absent from this subset.
printf '\nallowUnusedPatches: true\n' >> pnpm-workspace.yaml
# Deploy source-built workspace packages and their production dependencies.
pnpm --filter=vite-plus deploy --prod --legacy "$PWD/runtime/node_modules/vite-plus"
# pnpm retains upstream's lockfile-pinned native binaries for this target.

%install
install -d %{buildroot}%{_bindir}
install -Dpm 0755 target/release/vp %{buildroot}%{_libexecdir}/%{name}/bin/vp
ln -s ../libexec/%{name}/bin/vp %{buildroot}%{_bindir}/vp
ln -s vp %{buildroot}%{_bindir}/vpr
ln -s vp %{buildroot}%{_bindir}/vpx
cp -a runtime/node_modules %{buildroot}%{_libexecdir}/%{name}/
# Retain only the target glibc Zigpty binary from its multi-platform archive.
case '%{_arch}' in
    x86_64) zigpty_arch=x64 ;;
    aarch64) zigpty_arch=arm64 ;;
    *) exit 1 ;;
esac
zigpty_dir=$(find %{buildroot}%{_libexecdir}/%{name}/node_modules -type d -path '*/node_modules/zigpty/prebuilds' -print -quit)
test -n "$zigpty_dir" && test -s "$zigpty_dir/zigpty.linux-$zigpty_arch.node"
find "$zigpty_dir" -type f ! -name "zigpty.linux-$zigpty_arch.node" -delete
touch %{buildroot}%{_libexecdir}/%{name}/bin/.vp-setup-complete
install -d %{buildroot}%{_datadir}/bash-completion/completions \
    %{buildroot}%{_datadir}/fish/vendor_completions.d \
    %{buildroot}%{_datadir}/zsh/site-functions
PATH="%{buildroot}%{_libexecdir}/%{name}/bin:$PATH" VP_NODE_MANAGER=no VP_COMPLETE=bash vp > %{buildroot}%{_datadir}/bash-completion/completions/vp
PATH="%{buildroot}%{_libexecdir}/%{name}/bin:$PATH" VP_NODE_MANAGER=no VP_COMPLETE=fish vp > %{buildroot}%{_datadir}/fish/vendor_completions.d/vp.fish
PATH="%{buildroot}%{_libexecdir}/%{name}/bin:$PATH" VP_NODE_MANAGER=no VP_COMPLETE=zsh vp > %{buildroot}%{_datadir}/zsh/site-functions/_vp

%check
export HOME="$PWD/check-home" VP_NODE_MANAGER=no
mkdir -p "$HOME"
/usr/bin/node-24 -e 'if ([...new Intl.Segmenter("en").segment("test")].length !== 4) process.exit(1)'
%{buildroot}%{_libexecdir}/%{name}/bin/vp --version
esbuild_js=$(find %{buildroot}%{_libexecdir}/%{name}/node_modules -type f -path '*/node_modules/esbuild/lib/main.js' -print -quit)
test -n "$esbuild_js"
/usr/bin/node-24 -e 'const e = require(process.argv[1]); if (e.version !== "0.28.2" || !e.transformSync("let x: number = 42", {loader: "ts"}).code.includes("42")) process.exit(1)' "$esbuild_js"
zigpty_js=$(find %{buildroot}%{_libexecdir}/%{name}/node_modules -type f -path '*/node_modules/zigpty/dist/index.mjs' -print -quit)
test -n "$zigpty_js"
/usr/bin/node-24 --input-type=module - "$zigpty_js" <<'NODE'
import { pathToFileURL } from 'node:url';
const pty = await import(pathToFileURL(process.argv[2]));
if (!pty.hasNative || !pty.open()) throw Error('Zigpty native PTY unavailable');
NODE
yuku_js=$(find %{buildroot}%{_libexecdir}/%{name}/node_modules -type f -path '*/node_modules/yuku-parser/index.js' -print -quit)
test -n "$yuku_js"
/usr/bin/node-24 --input-type=module - "$yuku_js" <<'NODE'
import { pathToFileURL } from 'node:url';
const parser = await import(pathToFileURL(process.argv[2]));
const result = parser.parse('const answer = 42;');
if (result.program.type !== 'Program' || result.program.body.length !== 1 || result.diagnostics.length) throw Error('Yuku parsing failed');
NODE
for completion in %{buildroot}%{_datadir}/bash-completion/completions/vp \
    %{buildroot}%{_datadir}/fish/vendor_completions.d/vp.fish \
    %{buildroot}%{_datadir}/zsh/site-functions/_vp; do
    test -s "$completion"
    if grep -F '%{buildroot}' "$completion"; then
        echo "Buildroot leaked into $completion" >&2
        exit 1
    fi
done

%files
%license LICENSE LICENSE-ZIGPTY LICENSE-YUKU
%doc README.md
%{_bindir}/vp
%{_bindir}/vpr
%{_bindir}/vpx
%{_libexecdir}/%{name}
%{_datadir}/bash-completion/completions/vp
%{_datadir}/fish/vendor_completions.d/vp.fish
%{_datadir}/zsh/site-functions/_vp

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 1.6.0-1
- Initial package
