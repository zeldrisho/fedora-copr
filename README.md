# Fedora packages from COPR

This repository publishes Fedora RPM packages through the [`zeldrisho/packages` COPR repository](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/). Browse the [COPR project page](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/) to see which packages are currently available and supported by your Fedora release.

## Install

Enable the COPR repository and install a package with DNF:

```sh
sudo dnf copr enable zeldrisho/packages
sudo dnf install <package-name>
```

Replace `<package-name>` with the RPM name shown on the project page. Check the project page for current build availability for your Fedora release.

## Update or remove

Upgrade packages from this COPR along with other system packages:

```sh
sudo dnf upgrade
```

Remove a package:

```sh
sudo dnf remove <package-name>
```

Disable this COPR repository if you no longer want to receive packages from it:

```sh
sudo dnf copr disable zeldrisho/packages
```

## License

[MIT](LICENSE).
