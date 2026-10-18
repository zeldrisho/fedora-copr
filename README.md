# Fedora packages from COPR

This repository maintains Fedora RPM packaging for software published through the [`zeldrisho/packages` COPR repository](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/). These are community builds, not official Fedora packages. Check the COPR page for packages and availability for your Fedora release.

## Install

Enable the COPR repository and install a package (for example, `actionlint`):

```sh
sudo dnf copr enable zeldrisho/packages
sudo dnf install actionlint
```

Upgrade packages with `sudo dnf upgrade`, remove one with `sudo dnf remove <package-name>`, or disable the repository with:

```sh
sudo dnf copr disable zeldrisho/packages
```

## Development

See the [package development guide](docs/development.md) and [COPR publishing guide](docs/copr.md) for maintainer information.

## License

Repository-authored documentation and packaging infrastructure are licensed under [MIT](LICENSE). Local Fedora reference copies under [`docs/packaging-guidelines/`](docs/packaging-guidelines/README.md) and [`docs/package-maintainers/`](docs/package-maintainers/README.md) retain their upstream terms and attribution; each packaged application retains its own upstream license.
