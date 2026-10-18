# Herdr package notes

This package builds Herdr 0.9.5 from the upstream tag archive. It uses Fedora's Rust and Zig compilers and installs the Linux executable plus Bash, Zsh, and Fish completions.

## Offline build inputs

Herdr's Rust workspace uses Cargo dependencies plus the upstream path-patched `portable-pty`. `herdr-0.9.5-vendor.tar.gz` contains the Cargo registry sources produced by `cargo vendor` from the tagged source and lockfile. The spec unpacks this source and configures `%cargo_prep` to use it; the package build must not contact crates.io.

The upstream `crates/ghostty-vt/build.rs` invokes Zig 0.16.0. On Linux x86_64, the target build uses the vendored Ghostty sources and selected Zig packages including `uucode`, `translate_c`/Aro, Highway, simdutf, and Wuffs. `herdr-0.9.5-zig-deps.tar.gz` contains Zig's package-cache archives (`p/`) resolved by running the upstream build once. The spec extracts them into a dedicated `ZIG_GLOBAL_CACHE_DIR`; Zig can resolve the sources without network access. Do not replace this with cached compiled outputs: the archive contains source archives, and the binary is rebuilt by RPM.

To refresh source bundles for a new release:

1. Download the tagged source archive and inspect its Cargo lockfile, path dependencies, and Zig `build.zig.zon`.
2. Run `cargo vendor cargo-vendor` from the source tree and archive the resulting directory as `herdr-<version>-vendor.tar.gz`.
3. Start with an empty `p/` package-cache directory in `ZIG_GLOBAL_CACHE_DIR` and build the Linux target using the required Fedora Zig version. This source-preparation build may access the network to resolve packages; it populates `p/` with the resolved source archives. Archive that directory as `herdr-<version>-zig-deps.tar.gz`.
4. Rebuild from a clean source tree with networking disabled, using only the two archives. Verify no new package-cache downloads occur. Refresh `cargo-vendor.txt`, linked-dependency license reporting, source license inventory, and the spec's `License:` expression.
5. Review the bundled Ghostty/Zig dependency licenses and any changes to linked crate licenses; retain their license files in `%license` as needed.

Both archives are source inputs, not prebuilt program code. The Zig cache was populated by a Linux x86_64 `-Demit-lib-vt` build; the Fedora target architectures must each be validated before being considered supported.

## Behavior and support

The RPM smoke checks version output and Bash completion generation. Herdr is an interactive workspace manager, so test server startup, workspace creation, detach/reattach, and terminal panes manually after installation. Agent integrations and plugins are optional; the RPM does not install agent software or fetch integrations at build time.

Upstream 0.9.5 pins Rust 1.96.1 and requires Zig 0.16.0. Keep these explicit until the package is confirmed against the configured Fedora chroots. `ExclusiveArch` reflects upstream's current Linux Zig target mapping; add other architectures only after a successful build and smoke test.

The `%check` phase runs unit tests serially because Herdr tests modify process-wide signal dispositions. Test builds disable RPM-profile LTO and set Fedora's Rust codegen-unit flag to 16 to reduce test-harness compilation time; the release binary retains Fedora's normal build flags. `procps-ng` is a build dependency because a Linux unit test invokes `ps`.
