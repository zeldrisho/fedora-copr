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

[MIT](LICENSE)
