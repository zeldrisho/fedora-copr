# actionlint packaging

## Status

Packit PR and main publishing jobs are enabled; the revised recipe still needs target builds.

## Sources and build

`packages/actionlint/prepare-sources.sh` verifies the upstream tag archive and vendors the Go modules selected by `go.mod`, with downloads checked against `go.sum`. The RPM build and tests use the vendored modules offline and disable automatic Go toolchain downloads. Following Fedora's Go guidelines, the spec enables modules mode for `%gobuild`; its default GOPATH mode caused COPR build 11321022 to fail resolving actionlint's own module. The source release requires Go 1.25 or newer. The man page is generated from the source manual using Fedora's `rubygem-ronn-ng`. ShellCheck and pyflakes are optional integrations and recommended dependencies.

## Updates and limitations

- The recipe has not yet been verified in COPR. Check Fedora 44, Fedora 45, and Rawhide on `x86_64` and `aarch64` before publishing. Tests for optional external checkers may be skipped when those tools are absent from the build environment. Two upstream maintenance-generator test packages are excluded: `check-checks` expects a Git checkout and `generate-popular-actions` expects GitHub responses. The core tests and other generator tests still run, except `generate-webhook-events`'s `TestFetchURL` and `TestFetchError/not_found`, which contact GitHub; the latter failed offline in COPR build 11321842.
- The provisional license expression includes upstream's MIT license, BSD-3-Clause for `golang.org/x/sync` v0.20.0, and Apache-2.0 for `go.yaml.in/yaml/v4` v4.0.0-rc.3, both imported by actionlint. The YAML module also includes MIT-licensed libyaml-derived files and a NOTICE. An inspection of root license files for all modules pinned in `go.mod` found MIT, BSD-3-Clause and Apache-2.0; that is not a file-level or linked-binary audit. Vendored notices are retained, but review the actual binary's dependencies, nested notices, and complete expression before redistribution.
- Review new releases for Go version requirements, dependency licenses, and changes to source layout or build flags.

## References

- [Upstream installation and source builds](https://github.com/rhysd/actionlint/blob/v1.7.12/docs/install.md)
- [Upstream release build configuration](https://github.com/rhysd/actionlint/blob/v1.7.12/.goreleaser.yaml)
- [Nixpkgs actionlint package](https://github.com/NixOS/nixpkgs/blob/master/pkgs/by-name/ac/actionlint/package.nix) — Go build, version metadata, man page, and optional integrations.
- [Fedora Go packaging guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Golang/) — vendoring and compiler flags; the [licensing guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) require metadata and notices for binary RPM contents.
- [Upstream Go module pins](https://github.com/rhysd/actionlint/blob/v1.7.12/go.mod), [sync imports](https://github.com/rhysd/actionlint/blob/v1.7.12/linter.go), and [sync license](https://github.com/golang/sync/blob/v0.20.0/LICENSE) establish the BSD-3-Clause addition. [Actionlint imports YAML](https://github.com/rhysd/actionlint/blob/v1.7.12/action_metadata.go); the [YAML NOTICE](https://github.com/yaml/go-yaml/blob/v4.0.0-rc.3/NOTICE) identifies Apache-2.0 and MIT portions. The [Homebrew formula](https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/a/actionlint.rb) is another build reference, not a complete linked-license audit.
- [Fedora rubygem-ronn-ng package](https://packages.fedoraproject.org/pkgs/rubygem-ronn-ng/rubygem-ronn-ng/) — man page generator availability.
