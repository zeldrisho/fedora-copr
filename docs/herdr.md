# Herdr packaging

Herdr is a terminal workspace manager for coding agents. The `herdr` RPM provides the `herdr` command; see the [installation instructions](../README.md).

## Status

Packit PR and main publishing jobs are enabled. [PR #1](https://github.com/zeldrisho/fedora-copr/pull/1/checks) passed on Fedora 44, Fedora 45 and Rawhide on x86_64 and aarch64. RPM builds run without network access.

## Sources and build

`packages/herdr/prepare-sources.sh` runs in COPR's SRPM builder. It verifies the upstream archive, vendors locked Cargo dependencies and prefetches Zig dependencies. The RPM builds in PR #1 compiled offline from the resulting dependency archive. The one-line downstream patch explicitly selects Zig's baseline CPU for the vendored Ghostty library to avoid depending on builder-specific CPU features. Upstream already supplies a target triple; whether that makes the explicit baseline redundant has not been verified with Zig 0.16.0.

## Updates and limitations

- The SRPM builder and target chroots need Zig 0.16.0, and the latter need Rust/Cargo 1.96.1 or later. Recheck toolchain availability on updates.
- The spec includes the Apache-2.0 and statically linked Ghostty MIT notices, but other statically linked and vendored dependencies have not yet been audited.
- Test both the version command and an interactive session on each supported architecture before relying on the package.

## References

- [Vendored Ghostty license](https://github.com/herdrdev/herdr/blob/v0.9.5/vendor/libghostty-vt/LICENSE) — included separately to avoid a filename collision with Herdr's license.
- [Fedora licensing guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) — include applicable license texts in binary RPMs.

- [Fedora Rust Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/) — optional packaging guidance.
- [Homebrew Herdr formula](https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/h/herdr.rb) — dependency prefetch, completions and smoke test.
- [Upstream Herdr Nix package](https://github.com/herdrdev/herdr/blob/v0.9.5/nix/package.nix) — offline dependency setup.
