# actionlint RPM package

This directory packages upstream [actionlint](https://github.com/rhysd/actionlint), a linter for GitHub Actions workflow files. The RPM installs the `actionlint` command and its man page.

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

Review the generated archive, SPDX expression, bundled module provides, and included license files. Then validate and build locally:

```sh
make -C ../.. validate
```

The package's `%check` skips tests that require live HTTP because Fedora builds run offline, and omits a generator test needing Git metadata unavailable in the upstream release archive. The remaining tests run offline. CI builds the binary RPM locally before merge; COPR build logs confirm the configured target chroots after publishing.
