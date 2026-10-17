# actionlint RPM package

This directory packages upstream [actionlint](https://github.com/rhysd/actionlint), a linter for GitHub Actions workflow files. The RPM installs the `actionlint` command, its man page, and the upstream README, changelog, and documentation under the package documentation directory. Package-specific Fedora submission notes and source/installation audit are in [`docs/review.md`](docs/review.md) and [`docs/audit.md`](docs/audit.md); these records apply to the versions/builds they identify.

For usage, configuration, and the full list of lint checks, see the [upstream documentation](https://github.com/rhysd/actionlint/tree/v1.7.12/docs). The upstream [README](https://github.com/rhysd/actionlint/blob/v1.7.12/README.md) includes examples and a quick start.

## Offline Go dependencies

COPR/Fedora binary builds must not fetch Go modules. The spec therefore includes the upstream release archive plus the checked-in `actionlint-<version>-vendor.tar.bz2` source archive, generated with Go Vendor Tools. `go-vendor-tools.toml` contains the licensing configuration. Keep the archive, config, and spec synchronized when updating the upstream version.

To regenerate the archive for a new version, from this directory, after obtaining the matching upstream source archive and installing Go Vendor Tools:

```sh
spectool -g actionlint.spec
go_vendor_archive create --config go-vendor-tools.toml --write-config actionlint.spec
go_vendor_license --config go-vendor-tools.toml --path actionlint.spec \
  report --prompt --autofill auto --write-config --update-spec
```

Review the generated archive and license report; do not accept generated results without checking them. Resolve missing vendored-module licenses before distributing the archive, verify the cumulative SPDX expression against Fedora's allowed licenses, and confirm all relevant license files are installed. Check that `vendor/modules.txt` is included as a license file and that the built RPM has the expected `bundled(golang(...))` provides. Then validate and build locally:

```sh
make -C ../.. validate
```

Repository validation covers the spec and SRPM, not binary RPM linting or runtime behavior. Build and inspect the binary RPM, run `rpmlint` on it, and test the installed command as well.

The package's `%check` skips tests that require live HTTP because Fedora builds run offline, and omits `scripts/check-checks`, which maintains upstream's lint-check documentation and needs `shellcheck` and `pyflakes`. The remaining tests run offline. CI builds the binary RPM locally before merge; COPR build logs confirm the configured target chroots after publishing.
