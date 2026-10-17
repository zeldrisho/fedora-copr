# Yazi package notes

This package builds the Yazi 26.9.1 workspace from the upstream source archive. The release's Rust crate requirements are not available as Fedora packages in the target repositories, so it uses the upstream Cargo registry sources in the checked-in vendor archive `yazi-26.9.1-vendor.tar.gz`. The SRPM is self-contained; Cargo does not access the network during the build or tests. Lua and Oniguruma are built against Fedora's system libraries (`lua-devel` and `oniguruma-devel`), not their upstream bundled copies. Fedora 44 builds against Lua 5.4; Fedora 45 and Rawhide build against Lua 5.5. The Fedora 44 patch substitutes copying strings for the upstream Lua 5.5 external-string optimization. The verified upstream tag commit is embedded via `VERGEN_GIT_SHA` so version output retains source provenance without requiring a Git checkout.

The upstream prebuilt syntax database contained grammars with no established redistribution license or unavailable source. The vendor archive now contains a filtered copy of the upstream database, preserving its 200 other compiled syntax definitions while omitting five grammars: hosts, LESS, LiveScript, Nginx, and Verilog. The GPL-3.0-only SSH grammar remains and its pinned source and license are included. The matching syntax source archive is installed as package documentation, and its notices are collected into `LICENSE.syntaxes`.

The vendor archive was generated from the tagged release source with `cargo vendor vendor`, then its `yazi-prebuilt` database was filtered with the checked-in Rust helper. When updating, check out the commit pinned by the new `yazi-prebuilt` crate and run the source archive helper (it initializes supported submodules and removes the five excluded trees), filter the upstream database with syntect 5.3.0, and refresh the vendor archive:

```sh
git clone --no-checkout https://github.com/yazi-rs/prebuilt.git /tmp/yazi-prebuilt
git -C /tmp/yazi-prebuilt checkout <yazi-prebuilt-commit>
python3 packages/yazi/scripts/create-syntax-source-archive.py \
  /tmp/yazi-prebuilt packages/yazi/yazi-<version>-syntax-sources.tar.gz \
  --ssh-license packages/yazi/yazi-ssh-config-LICENSE.md --version <version>
RUSTONIG_SYSTEM_LIBONIG=1 RUSTONIG_DYNAMIC_LIBONIG=1 \
  cargo run --locked --manifest-path packages/yazi/scripts/filter-syntax-database/Cargo.toml -- \
  /tmp/yazi-prebuilt/built/syntaxes /tmp/yazi-filtered-syntaxes.bin
(cd /tmp/yazi-source && cargo vendor vendor)
tar -czf /tmp/yazi-vendor-raw.tar.gz -C /tmp/yazi-source vendor
python3 packages/yazi/scripts/update-vendor-syntaxes.py \
  /tmp/yazi-vendor-raw.tar.gz /tmp/yazi-filtered-syntaxes.bin \
  packages/yazi/yazi-<version>-vendor.tar.gz
```

Review both archives and update their checksums in the audit. The filter helper validates that syntect 5.3.0 can load the resulting database. The SSH syntax source is pinned to commit `e1012e9f13c6073f559b14206df2ede35720e884`; its GPL-3.0 license text is from upstream commit `a47c765aa14d58236b5e5964bb687b5352450547`. `%prep` removes prebuilt object and library files from vendored crates before building; do not omit that cleanup.

## Build compatibility

Yazi 26.9.1 uses `mlua` 0.12 with the Lua 5.5 feature. Its `mlua-sys` supports system `lua.pc` files whose version falls in the selected Lua range. The spec disables upstream's vendored-Lua defaults and uses Fedora's system Lua. Fedora 45 and Rawhide use Lua 5.5; Fedora 44 uses Lua 5.4 and needs the conditional `lua54` feature patch plus the API fallback patch for `create_external_string`, which is only available with Lua 5.5. Keep both patches limited to Fedora 44 so newer targets use upstream's Lua 5.5 API.

## Updating

1. Select a tagged upstream release compatible with every configured COPR chroot.
2. Review its source, `Cargo.lock`, workspace members, upstream license, and Git/path dependencies. Prefer crates packaged by Fedora; do not allow Cargo to access the network during binary builds or tests.
3. Regenerate the vendor archive and build the package in the target Fedora chroots. Keep the `cargo-vendor.txt` manifest in `%license` so RPM generates bundled-crate provides.
4. Review `%cargo_license` output and update the binary package's `License:` expression to include all linked crates and included syntax data. The source archive and `LICENSE.syntaxes` track syntax inputs and notices; the five entries listed above are deliberately omitted because the package lacks a verified license or complete source for them. See the [audit record](docs/audit.md) for source pins and the Fedora `rust-bat` comparison.
5. Verify installed executable paths and names, RPM file/license metadata, and run both executables before publishing.

The package requires Fedora's `file` utility, which Yazi uses for file-type detection. Fedora's optional weak dependencies recommend `7zip`, `ffmpeg-free`, `fd-find`, `fzf`, `ImageMagick`, `jq`, `poppler-utils`, `ripgrep`, and `zoxide` for previews, search, and archive handling. These integrations remain optional; clipboard support also requires a compatible tool such as `wl-clipboard`, `xclip`, or `xsel`.

The package includes `yazi(1)` and `ya(1)` manual pages alongside the generated Bash, Fish, and Zsh completions.
