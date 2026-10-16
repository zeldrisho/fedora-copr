# Fedora packages from COPR

This repository contains ordinary Fedora RPM specs and stages package builds in the [`zeldrisho/packages` COPR repository](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/). Browse the project page for packages currently available for your Fedora release.

## Install

Enable the COPR repository and install a package:

```sh
sudo dnf copr enable zeldrisho/packages
sudo dnf install <package-name>
```

For example, to install actionlint when a build is available for your Fedora release:

```sh
sudo dnf install actionlint
```

Check the COPR project page for current build status and release availability. Upgrade packages with `sudo dnf upgrade`; remove one with `sudo dnf remove <package-name>`. Disable the repository with:

```sh
sudo dnf copr disable zeldrisho/packages
```

## Repository and contribution guides

- [Development](docs/development.md): tools, validation, and SRPM creation.
- [Fedora packaging policy](docs/packaging.md): spec, source, dependency, and file conventions.
- [COPR setup](docs/copr.md): SCM package entry and project settings.
- [Release process](docs/release.md): updating, building, and verifying packages.
- [Actionlint package notes](packages/actionlint/README.md): vendored Go sources and upstream docs.

## License

Repository documentation and packaging infrastructure are licensed under [MIT](LICENSE). Each packaged application retains its own upstream license.
