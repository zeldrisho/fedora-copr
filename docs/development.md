# Package development and COPR staging

## Repository layout and Fedora policy

Each RPM is an independent Fedora spec at `packages/<name>/<name>.spec`. The package directory, spec filename, and `Name:` tag must agree. The initial repository may have no package directories.

Specs must remain plain Fedora-submittable RPM specs: no COPR-only conditionals or rpkg templates. COPR-specific integration belongs only in `.copr/Makefile`. Follow the [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/) and [Package Maintainers documentation](https://docs.fedoraproject.org/en-US/package-maintainers/) for package requirements and submission procedures.

The `.copr/Makefile` implements the `srpm` target expected by COPR's SCM + `make_srpm` method. COPR invokes it in the package subdirectory and passes `spec` and `outdir`. It uses `spectool -g -C "$(CURDIR)"` so downloaded sources are in the current directory, then calls `rpmbuild -bs` with `_sourcedir` set to that directory and `_srcrpmdir` set to the requested output directory.

Sources are downloaded while preparing the SRPM; the RPM build itself must not need network access. The same Makefile target is used locally and in CI. The validator (`scripts/validate.py`) parses each spec with `rpmspec -P`, checks naming agreement, builds an SRPM, and runs rpmlint against the spec and SRPM. An empty `packages/` passes validation.

For spec-writing policy, source integrity, dependencies, Go packaging, file layout, and validation expectations, see [Fedora packaging notes](fedora-packaging.md). The `actionlint` spec's Go dependency and license workflow is documented there as well.

## Local development

Install the tools on Fedora:

```sh
sudo dnf install rpm-build rpmdevtools rpmlint make python3 go go-rpm-macros go-vendor-tools go2rpm rubygem-ronn-ng
```

Run package validation from any directory:

```sh
./scripts/validate.py
```

To build one package SRPM manually, run the target from its package subdirectory:

```sh
cd packages/<name>
make -f ../../.copr/Makefile srpm spec=<name>.spec outdir=/tmp/srpms
```

## One-time COPR project setup

Configure COPR project **`zeldrisho/packages`** in the COPR web UI:

1. Select SCM as the source, using this GitHub repository. Use the repository `.copr/Makefile` for the `make srpm` method.
2. Configure the package subdirectory as `packages/<name>` and the spec file as `<name>.spec`.
3. Enable `fedora-44-x86_64`, `fedora-45-x86_64`, and `fedora-rawhide-x86_64`.
4. Enable **fedora-review**.
5. Turn off **internet access during builds**. Source acquisition happens when creating the SRPM, not inside the isolated package build.
6. Enable **follow Fedora branching**.
7. Turn **AppStream** off.
8. Configure and verify the GitHub webhook for the repository.

COPR's [user documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html) describes SCM and `make srpm`. These settings are staging configuration only; they must not introduce COPR behavior into Fedora specs.
