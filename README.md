# Fedora packages from COPR

Community Fedora RPMs for actionlint, Herdr, and Yazi, published in [`zeldrisho/packages`](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/). These are not official Fedora packages; check COPR for availability.

## Install

Enable the repository, then install the packages you want:

```sh
sudo dnf copr enable zeldrisho/packages
sudo dnf install actionlint herdr yazi
```

## Development

See the [package development guide](docs/development.md) and [COPR publishing guide](docs/copr.md) for maintainer information.

## License

Repository-authored documentation and packaging infrastructure are licensed under [MIT](LICENSE). Local Fedora reference copies under [`docs/packaging-guidelines/`](docs/packaging-guidelines/README.md) and [`docs/package-maintainers/`](docs/package-maintainers/README.md) retain their upstream terms and attribution; each packaged application retains its own upstream license.
