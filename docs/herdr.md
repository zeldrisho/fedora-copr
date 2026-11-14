# Herdr packaging

## Status

Packit PR and main publishing jobs are enabled; toolchain availability and target builds remain unverified. The RPM build is designed to run without network access.

## Sources and build

`packages/herdr/prepare-sources.sh` runs in COPR's SRPM builder. It verifies the upstream archive, vendors locked Cargo dependencies and prefetches Zig dependencies. The spec is intended to compile offline from the resulting dependency archive; this flow is not yet verified in COPR.

## Updates and limitations

- The source-build recipe is experimental. The SRPM builder and target chroots need Zig 0.16.0, and the latter need Rust/Cargo 1.96.1 or later. Availability and compatibility remain to be tested.
- The spec includes the Apache-2.0 and statically linked Ghostty MIT notices, but other statically linked and vendored dependencies have not yet been audited.
- Test both the version command and an interactive session on each supported architecture before relying on the package.

## References

- [Vendored Ghostty license](https://github.com/herdrdev/herdr/blob/v0.9.5/vendor/libghostty-vt/LICENSE) — included separately to avoid a filename collision with Herdr's license.
- [Fedora licensing guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) — include applicable license texts in binary RPMs.

- [Fedora Rust Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/) — optional packaging guidance.
- [Homebrew Herdr formula](https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/h/herdr.rb) — dependency prefetch, completions and smoke test.
- [Upstream Herdr Nix package](https://github.com/herdrdev/herdr/blob/v0.9.5/nix/package.nix) — offline dependency setup.
