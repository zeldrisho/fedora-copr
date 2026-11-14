# gomi packaging

## Status

Packit PR and main publishing jobs are enabled. [PR #1](https://github.com/zeldrisho/fedora-copr/pull/1/checks) passed on Fedora 44, Fedora 45 and Rawhide on x86_64 and aarch64.

## Sources and build

`packages/gomi/prepare-sources.sh` verifies the upstream tag archive and vendors the modules selected by `go.mod`, with downloads checked against `go.sum`. It normalizes the vendor archive's ordering and metadata. The RPM build and tests use the vendored modules offline and disable automatic Go toolchain downloads. The release requires Go 1.26 or newer; PR #1 built successfully on Fedora 44. The spec enables modules mode for Fedora's `%gobuild` macro, uses its compiler flags, and embeds the upstream version, rather than upstream's stripped binary flags. Tests and the trash smoke test use isolated HOME and XDG directories.

## Updates and limitations

- Upstream is MIT licensed. The complete vendored dependency license expression has **not** been audited; the spec retains discovered notices and `vendor/modules.txt` but its `License` tag is incomplete if dependencies have other licenses. Check applicable notices and correct the SPDX expression where necessary before redistribution. Fedora's Go guidelines recommend Go Vendor Tools for this audit.
- Review new releases for Go version requirements, dependency licenses, and changes to source layout or build flags. The scheduled updater can propose version and checksum changes, but dependency audits are manual.
- The package does not install an `rm` alias. Trash behavior and recovery should be verified before adopting one.

## References

- [Upstream README and installation](https://github.com/babarot/gomi/tree/v1.10.1)
- [Upstream Go module](https://github.com/babarot/gomi/blob/v1.10.1/go.mod) and [release build configuration](https://github.com/babarot/gomi/blob/v1.10.1/.goreleaser.yaml) — Go version, dependencies, build and version flags.
- [Homebrew gomi formula](https://github.com/Homebrew/homebrew-core/blob/master/Formula/g/gomi.rb) — source archive, build and smoke-test reference.
- [Fedora Go packaging guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Golang/) — vendoring, license audit and compiler flags.
- [Fedora golang package](https://packages.fedoraproject.org/pkgs/golang/golang/) — target compiler availability.
