# Yazi packaging

Yazi is a terminal file manager. The `yazi` RPM provides `yazi` and `ya`; see the [installation instructions](../README.md).

## Status

Packit PR and main publishing jobs and livecheck are enabled. [PR #1](https://github.com/zeldrisho/fedora-copr/pull/1/checks) passed on Fedora 44, Fedora 45 and Rawhide on x86_64 and aarch64. Interactive behavior and subsequent dependency changes remain unverified.

## Sources and build

`packages/yazi/prepare-sources.sh` verifies the release archive and vendors the locked Cargo dependencies, including the Git-sourced ratatui fork, in the SRPM builder. The RPM build uses those sources offline. The package installs both `yazi` and `ya` and their Bash, Fish, and Zsh completions. `file` is required; preview and search tools are recommended dependencies and can be omitted with `--setopt=install_weak_deps=False`. The archive and video recommendations use executable providers: Fedora 44, 45 and Rawhide provide `7z`, `ffmpeg` and `ffprobe` through `7zip` and `ffmpeg-free`. Upstream also uses `resvg` for SVG previews; no `resvg` provider was found in the queried Fedora 44, 45 or Rawhide repositories. `librsvg2-tools` provides a different command and is not a drop-in replacement.

The build follows the existing COPR spec's GCC C17 workaround for Oniguruma and 16 KiB jemalloc page setting. PR #1 built with both settings on all six targets. The release declares Rust 1.95.0 as its minimum; locked dependencies may require a newer compiler.

Fedora's Rust guidelines recommend using packaged crates where possible. This personal COPR instead vendors the locked dependencies to support an offline RPM build, including upstream's Git fork. The spec uses `%set_build_flags` and `cargo-rpm-macros` as recommended; it deliberately does not use `%cargo_generate_buildrequires`, which Fedora's guidelines prohibit for vendored dependencies.

## Validation

The RPM `%check` runs both version commands and `cargo test --locked --offline`. PR #1 passed on all six targets before the current dependency changes; interactive behavior and those changes remain unverified. See [shared validation guidance](development.md#testing-and-validation).

## Updates and limitations

- Validate the updated dependency recommendations in a new RPM build and interactive session.
- The spec declares upstream's MIT license and includes the bundled Lua notice from its source header. Statically linked Rust crates and other vendored components have not been audited; their license notices and the complete RPM license expression must be checked before redistribution. Fedora's `%cargo_license_summary` and `%cargo_license` macros can help identify linked crates, but do not replace checking bundled native code or required license texts.
- The RPM does not yet provide the bundled-crate metadata described in Fedora's Rust guidelines. Evaluate `%cargo_vendor_manifest` and its generated `cargo-vendor.txt` against the Git-source replacement and target chroots before relying on vulnerability tracking.
- Updates must be reviewed for compiler requirements, dependency licensing, and changes to build flags or completions. The license-header lookup follows the vendored Lua 5.5 source and fails if it is missing or ambiguous; review it if Yazi changes Lua versions.

## References

- [Yazi installation and source builds](https://yazi-rs.github.io/docs/installation/) — build instructions and optional tools.
- [Yazi 26.9.1 Cargo manifest](https://github.com/sxyazi/yazi/blob/v26.9.1/Cargo.toml) — Rust version, Lua 5.5 feature and Git dependency.
- [lua-src 551.0.1 Lua header](https://docs.rs/crate/lua-src/551.0.1/source/lua-5.5.1/lua.h) — bundled Lua copyright and permission notice.
- [Existing Yazi COPR spec](https://github.com/lihaohong6/COPR/blob/master/yazi/yazi.spec) — completions, optional dependencies, and build workarounds.
- [Fedora Rust Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/) — build flags, vendored-crate metadata, and license macros.
- [Fedora Licensing Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) — license texts and binary RPM license fields.
