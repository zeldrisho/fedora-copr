# Personal COPR packages

Recipes for [zeldrisho/packages](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/), targeting Fedora 44, Fedora 45, and Rawhide on x86_64 and aarch64.

## Installation

```sh
sudo dnf copr enable zeldrisho/packages
sudo dnf install <package>
```

Not every recipe has a current build in COPR, and availability varies by release and architecture. Check [COPR package build status](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/packages/) and the package notes before installing; a listed package is not necessarily available for every target. Some packages bootstrap or download components at runtime.

## Packages

| Spec | Description |
| --- | --- |
| [actionlint](packages/actionlint/actionlint.spec) | GitHub Actions workflow checker |
| [gomi](packages/gomi/gomi.spec) | Move files to the trash and restore them |
| [herdr](packages/herdr/herdr.spec) | Terminal workspace manager for coding agents |
| [homebrew](packages/homebrew/homebrew.spec) | Linux package manager |
| [kotlin-toolchain](packages/kotlin-toolchain/kotlin-toolchain.spec) | Kotlin build tool and distribution launcher |
| [morphe](packages/morphe/morphe.spec) | Android app patcher |
| [pi-coding-agent](packages/pi-coding-agent/pi-coding-agent.spec) | Extensible terminal coding agent |
| [rea](packages/rea/rea.spec) | Reverse engineering CLI and MCP server |
| [smali](packages/smali/smali.spec) | Android DEX assembler and disassembler |
| [vite-plus](packages/vite-plus/vite-plus.spec) | Web development toolchain |
| [yazi](packages/yazi/yazi.spec) | Terminal file manager |

See the [package notes](docs/) for setup and limitations, [Packit and COPR builds](docs/packit.md) for publishing, and [development](docs/development.md) for validation and maintenance.

## License

Packaging files are licensed under [MIT](LICENSE); packaged software has its own licenses.
