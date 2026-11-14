# Personal COPR packages

Recipes for [zeldrisho/packages](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/), targeting Fedora 44, Fedora 45, and Rawhide on x86_64 and
aarch64.

```sh
sudo dnf copr enable zeldrisho/packages
sudo dnf install <package>
```

Recipes: actionlint, gomi, herdr, homebrew, kotlin-toolchain, morphe, pi-coding-agent, rea, smali, vite-plus, and yazi. Some packages bootstrap or
download components at runtime; see the package notes in [`docs/`](docs/).

Packaging files are licensed under [MIT](LICENSE); packaged software has its own licenses.
