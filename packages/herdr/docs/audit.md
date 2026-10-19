# Herdr 0.9.5 source and build audit

- Upstream: <https://github.com/herdrdev/herdr>
- Version: 0.9.5; upstream documentation identifies this release as stable.
- Source: `https://github.com/herdrdev/herdr/archive/refs/tags/v0.9.5.tar.gz`
- Upstream application license: Apache-2.0 (`LICENSE`).
- Workspace: Cargo lockfile, path crate `crates/ghostty-vt`, patched vendored `portable-pty`.
- Native build: `crates/ghostty-vt/build.rs` runs Zig 0.16.0 and builds vendored `vendor/libghostty-vt` as a static library. The build script passes `-Demit-lib-vt`, `-Dsimd=true` by default, and target/optimization settings. A Rust build-script read is not, by itself, proof of which transitive source code is linked into the final executable.
- Cargo source bundle: `herdr-0.9.5-vendor.tar.gz`, generated with `cargo vendor` from the tagged lockfile. SHA-256: `b131b52f4d794ecc34abdababe76f3324a1f20b7c5657ef4bf5fb75fde695f93`.
- Zig dependency source bundle: `herdr-0.9.5-zig-deps.tar.gz`, containing Zig package-cache source archives (`p/`). SHA-256: `8e51c25894ec2b41ddff67c01d5831fc4e5689c1264cd4f3449e2148ad52f8f0`. It includes the pinned `iterm2_themes` dependency archive (upstream URL: `https://deps.files.ghostty.org/ghostty-themes-release-20260831-151010-752a9c0.tgz`; Zig cache key: `N-V-__8AAEFmBABuDGOKxAI6VMg41b9euMZ-z7HS9EcUdaor`).
- Upstream source archive SHA-256: `a2486b09a8153630f6a19e72606ba1c961a6194bce13c09cba67ccce5e4252de`.
- Cargo linked-license summary (generated using `cargo2rpm --path Cargo.toml license-summary`) includes 0BSD, Apache-2.0, BSL-1.0, BSD-2-Clause, ISC, LGPL-2.1-or-later, MIT, Unicode-3.0, Unlicense, and Zlib license alternatives. Recompute for any dependency changes.
- Upstream build settings: `HERDR_BUILD_CHANNEL=stable`; source pins Rust 1.96.1. The native build uses Zig 0.16.0.

## Source bundle contents and preliminary license findings

The Zig cache contains `translate_c`, Aro, `uucode`, Pixels, zlib, Wuffs, Highway, and the pinned `iterm2_themes` source archive. COPR build 11170443 failed in Fedora 44, Fedora 45, and Rawhide because Zig attempted to resolve `iterm2_themes` from the network, even though `emit_themes` is disabled for `-Demit-lib-vt`. The cache now includes that exact archive so dependency resolution can remain offline. The archive contains theme data and no filenames matching `license`, `copying`, or `readme`; its license/provenance still requires assessment as part of the outstanding complete source/license audit. Verify that no additional dependencies are downloaded in a clean, network-disabled build.

Preliminary notices indicate Pixels test/image data includes CC0-1.0; zlib has its own license and a separately licensed Boost-licensed contribution; `uucode` is MIT; Wuffs has MIT and Apache-2.0 notices; Highway has Apache-2.0 and BSD-3-Clause notices. These observations are not a completed inventory. Determine whether the relevant files/code are copied, compiled, linked, or otherwise included in the RPM, and assess license obligations for the source archives as a whole. Do not infer permissibility or the complete SPDX expression from filenames or an automated scanner.

The current spec extracts and installs uucode, Wuffs, and Highway license texts and includes BSD-3-Clause in `License:`. This has **not yet been validated against a final RPM**. The previous fedora-review scan reported 18,419 unknown files; that count is not evidence that those files are unlicensed, but leaves source review unresolved. Pixels/zlib scope, exact feature linkage, all bundled-code provides, license metadata, and license-file completeness remain review blockers. Record the file-level reasoning and final decisions here before declaring the package ready.

## Build and test status

Earlier COPR build [11168076](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11168076/) succeeded for Fedora 44, Fedora 45, and Rawhide on x86_64. Build [11170135](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11170135/) also succeeded. These builds predate current local cache/license edits and cannot establish the final spec's build or license correctness. Their fedora-review output used prebuilt RPMs and is not a Mock build or installed-package test.

Historical Fedora 44 installation of `0.9.5-1` passed `rpm -V`, `herdr --version`, Bash completion generation, server/workspace operations, and several pane operations. Interactive detach/reattach was not verified. These results do not validate the current source/spec.

The package intentionally supports x86_64 only; `ExclusiveArch` no longer claims aarch64 support. Outstanding: clean build of the exact final SRPM; offline build/test verification; inspection of all final RPMs, metadata and license files; and final interactive runtime checks. See [`review.md`](review.md) for the filing gates. Do not state that these checks passed until fresh evidence is recorded.
