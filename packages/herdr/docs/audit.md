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

The Zig cache contains `translate_c`, Aro, `uucode`, Pixels, zlib, Wuffs, Highway, and the pinned `iterm2_themes` source archive. Earlier COPR builds failed because Zig attempted to resolve `iterm2_themes` from the network even though `emit_themes` is disabled for `-Demit-lib-vt`. The cache now includes that exact archive. Release 4's successful Rawhide COPR task records `enable_net: False`, supporting offline dependency resolution for that build. The archive contains theme data and no filenames matching `license`, `copying`, or `readme`; its license/provenance still requires assessment as part of the outstanding complete source/license audit.

Preliminary notices indicate Pixels test/image data includes CC0-1.0; zlib has its own license and a separately licensed Boost-licensed contribution; `uucode` is MIT; Wuffs has MIT and Apache-2.0 notices; Highway has Apache-2.0 and BSD-3-Clause notices. These observations are not a completed inventory. Determine whether the relevant files/code are copied, compiled, linked, or otherwise included in the RPM, and assess license obligations for the source archives as a whole. Do not infer permissibility or the complete SPDX expression from filenames or an automated scanner.

The `0.9.5-2` RPM from COPR build 11170844 was inspected. Release 4 Rawhide RPM from build 11171729 reports the spec's SPDX expression and installs the Herdr executable, manual page, README, Bash/Zsh/Fish completions, `LICENSE.dependencies`, `cargo-vendor.txt`, and separate Herdr, Ghostty, Highway, uucode, and Wuffs license texts. The upstream and Ghostty files now have distinct paths (`LICENSE` and `LICENSE.ghostty-vt`). The RPM also has Cargo `bundled(crate(...))` Provides. No `bundled(...)` Provides for the native Zig/Ghostty components were identified in RPM Provides; determine which native components are actually incorporated and whether Fedora requires declarations for them. Fedora 44, Fedora 45, and Rawhide builds succeeded; the Rawhide build log records `enable_net: False`, 3,657 tests passed (12 ignored), and version/completion checks passed. This build evidence does not resolve the outstanding source-level license assessment or installed-runtime checks.

Inspection of the `0.9.5-2` RPM found that `%license LICENSE` and `%license vendor/libghostty-vt/LICENSE` collided at `/usr/share/licenses/herdr/LICENSE`; Ghostty's MIT text displaced Herdr's Apache-2.0 text. The `0.9.5-3` spec stages both at distinct names, and Release 4 RPM inspection confirms both license paths are present. This non-user-facing license-content correction uses a new NVR because `0.9.5-2` was already published with different RPM contents.

The fedora-review license scan for `0.9.5-4` reported 18,419 unknown files and assorted recognized license texts. That count is not evidence that files are unlicensed, but the file/source-level audit is not complete. In particular, Pixels CC0 data, zlib and its separately licensed contribution, `iterm2_themes` theme content, enabled Ghostty features, native linked code, exact bundle declarations, and the complete SPDX expression still require evidence-based assessment. Do not treat the current expression as final or declare the package ready until these questions and all source notices are resolved.

## Build and test status

Historical COPR build [11170844](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11170844/) succeeded on Rawhide x86_64 for `0.9.5-2`. Its older build/review evidence does not replace Release 4 results. Its fedora-review invocation used `--prebuilt`, and its purported install check did not install the RPM.

The Release 4 build produced `herdr`, `herdr-debuginfo`, and `herdr-debugsource`. The Fedora Review attachment reports zero errors and two local Source1/Source2 `invalid-url` warnings for the main RPM/SRPM; binary and debuginfo checks have no rpmlint errors or warnings. The report's installed-package check did not install RPMs, so clean runtime testing remains outstanding.

Historical Fedora 44 installation of `0.9.5-1` passed `rpm -V`, `herdr --version`, Bash completion generation, server/workspace operations, and several pane operations. Interactive detach/reattach was not verified. These results do not validate the current source/spec.

The package intentionally supports x86_64 only; `ExclusiveArch` no longer claims aarch64 support. `scripts/validate.py` and repository unit tests passed for the Release 4 candidate. COPR build 11171729 succeeded on Fedora 44, Fedora 45, and Rawhide with network disabled; Rawhide RPM metadata and license-file paths were inspected. Outstanding: complete source-license and native-component audit; clean installed-package test including interactive detach/reattach; and account/duplicate-review checks. See [`review.md`](review.md) for filing gates. Do not mark these checks complete without fresh evidence.
