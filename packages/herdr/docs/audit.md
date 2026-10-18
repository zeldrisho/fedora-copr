# Herdr 0.9.5 source and build audit

- Upstream: <https://github.com/herdrdev/herdr>
- Version: 0.9.5; upstream documentation at the release identifies this as stable.
- Source: `https://github.com/herdrdev/herdr/archive/refs/tags/v0.9.5.tar.gz`
- Upstream application license: Apache-2.0 (`LICENSE`).
- Workspace: Cargo lockfile, path crate `crates/ghostty-vt`, and patched vendored `portable-pty`.
- Native build: `crates/ghostty-vt/build.rs` runs Zig 0.16.0 and builds the vendored `vendor/libghostty-vt` static library.
- Zig source dependency bundle: `herdr-0.9.5-zig-deps.tar.gz`, containing `p/` source archives resolved during a Linux x86_64 build. SHA-256: `6641731b34b24d271f0b08a85f17011d4e467204cc34b96648b81cb45abcfc6a`. The clean-cache build succeeded with this package cache and no prior local Zig build cache.
- Cargo source bundle: `herdr-0.9.5-vendor.tar.gz`, generated with `cargo vendor` using the tagged Cargo.lock. SHA-256: `b131b52f4d794ecc34abdababe76f3324a1f20b7c5657ef4bf5fb75fde695f93`.
- Upstream archive: `herdr-0.9.5.tar.gz`, SHA-256: `a2486b09a8153630f6a19e72606ba1c961a6194bce13c09cba67ccce5e4252de`.
- Cargo linked-license summary: generated with `cargo2rpm --path Cargo.toml license-summary`; includes choices of 0BSD, Apache-2.0, BSL-1.0, BSD-2-Clause, ISC, LGPL-2.1-or-later, MIT, Unicode-3.0, Unlicense, and Zlib. The binary license expression in the spec combines these expressions and ISC for Ghostty/Wuffs build inputs. Revalidate after dependency changes.
- Upstream build settings: `HERDR_BUILD_CHANNEL=stable`; release source pins Rust 1.96.1.

This record does not replace RPM build validation. Verify both Fedora target architectures and Fedora 44, Fedora 45, and Rawhide before publication; review all files in both source bundles and re-run the build in a network-disabled chroot.
