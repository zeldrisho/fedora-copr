# Fedora packages from COPR

Community Fedora RPMs for actionlint, Herdr, and Yazi, published in [`zeldrisho/packages`](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/). These are not official Fedora packages; check COPR for availability.

## Install

Enable the repository, then install the packages you want:

```sh
sudo dnf copr enable zeldrisho/packages
sudo dnf install actionlint
sudo dnf install yazi
sudo dnf install herdr
```

## Development

See the [package development guide](docs/development.md) and [COPR publishing guide](docs/copr.md) for maintainer information.

## License

Repository-authored documentation and packaging infrastructure are licensed under [MIT](LICENSE). Packaged applications and bundled upstream materials retain their own licenses; see each package's spec and included license or notice files.
