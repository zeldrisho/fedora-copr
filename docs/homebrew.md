# Homebrew

The `homebrew` RPM provides a `brew` launcher and a read-only seed. On first use, the launcher offers to initialize a separate installation at `/home/linuxbrew/.linuxbrew`, owned by the user who runs it. No dedicated `linuxbrew` account is created. This has not yet been verified on all COPR targets.

## Installation and use

Install the RPM, then run `brew` as your regular user in a terminal:

```sh
brew --version
brew install hello
brew update
```

The first invocation asks for confirmation before using `sudo` to create the prefix and initialize it for your user. Setup downloads Git metadata from GitHub; Homebrew may also download portable Ruby, metadata, bottles, and other dependencies when run. RPM installation and builds do not need network access. A non-interactive first invocation fails with instructions to run it in a terminal.

The initializing user owns and manages the installation, as in the [upstream Linux installation](https://docs.brew.sh/Homebrew-on-Linux). Other users may run installed executables but do not automatically have permission to manage the prefix. To add Homebrew executables to your PATH, follow the upstream guide, for example:

```sh
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
```

Packages and their files are managed by Homebrew, not RPM. Do not invoke Homebrew with sudo: the prefix owner can execute code as root when it is invoked that way. Anyone able to write to the prefix can affect all users running software from it. Homebrew expects normal development tools; install Fedora's `development-tools` group if building formulae from source.

The launcher refuses to initialize if `/home/linuxbrew` already exists; it will not adopt or overwrite an existing installation, including one made by the upstream installer. A root-owned marker in `/var/lib/homebrew` distinguishes installations initialized by this RPM. If setup fails, the launcher removes the directory it created so initialization can be retried. An interrupted process that cannot run its cleanup may leave a partial installation; inspect it and remove `/home/linuxbrew` only after confirming it contains no data you need.

`brew update` updates the writable copy independently of RPM. Upgrading or removing the RPM changes only the seed and launcher; it does not update or remove the live installation, formulae, or initialization marker. Back up any wanted data and remove `/home/linuxbrew` and `/var/lib/homebrew/rpm-initialized` manually if you no longer need them. No automatic update services or privileged proxy are installed.

## Sources and build

- [Upstream Linux installation](https://docs.brew.sh/Homebrew-on-Linux) uses the same prefix and requires a writable installation and system build tools. The GitHub tag archive is checksum-verified during SRPM preparation; first-run setup fetches Git metadata separately because the archive has none. Setup checks that the fetched tag matches the seed and needs network access, but does not run the upstream installer.
- [Upstream installer](https://github.com/Homebrew/install/) makes the installing user own the writable prefix. This RPM similarly assigns the prefix to the first user, but provides an explicit first-run prompt and keeps the RPM seed separate.
- [Secureblue's Homebrew RPM](https://github.com/secureblue/homebrew) uses an RPM-owned seed and a separate writable copy. This package adapts that design, but uses an interactive first-run launcher and a user-owned prefix rather than a dedicated owner, tmpfiles, automatic updates, or a proxy. No Secureblue code is copied. The upstream seed includes vendored components and their notices; the complete license expression still needs auditing.
- [Fedora filesystem and ownership guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_filesystem_layout) motivate keeping RPM-owned files separate from the mutable prefix. Fedora's [build-time networking rule](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_build_time_network_access) is followed during RPM builds. The RPM stores the seed as the original compressed source archive, avoiding processing its test binaries and scripts as RPM executables. Runtime requirements are declared explicitly and need verification across targets.
