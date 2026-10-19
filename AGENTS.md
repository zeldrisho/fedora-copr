# Agent Instructions

## Toolchain

- Use Fedora RPM tooling: `rpm-build`, `rpmdevtools`, `rpmlint`, GNU Make, and `copr-cli`.
- Use Python 3 for repository validation scripts.
- Prefer `copr-cli` for COPR status, build, and artifact operations; use HTTP only when the CLI cannot provide the information.

## Commands

| Task | Command |
| --- | --- |
| Validate all packages | `scripts/validate.py` |
| Build and retain an SRPM | `(cd packages/<name> && make -f ../../.copr/Makefile srpm spec=<name>.spec outdir="$HOME/rpmbuild/SRPMS")` |
| List COPR builds | `copr-cli list-builds zeldrisho/packages --output-format json` |
| Download a COPR review | `copr-cli download-build <build-id> -r <chroot> --review --dest dist/review/<name>` |
| Find files and directories | `fd '<pattern>' [path]` |

## Key conventions

- Keep `packages/<name>/<name>.spec`; directory, spec basename, and RPM `Name:` must match.
- Consult relevant repository and package-local guidance before package changes. For shared build, validation, or publishing changes, inspect the relevant `.copr/`, CI, and development files.
- For new packages, perform an initial local binary build and record elapsed time. For existing packages, choose local or COPR builds based on measured duration and maintenance needs; current Herdr and Yazi binary builds use COPR. Local SRPM creation and validation remain allowed.
- Keep specs Fedora-submittable and COPR-specific behavior in `.copr/Makefile`. Add spec comments only when useful to Fedora build systems or maintainers.
- Keep all SRPM sources available at SRPM creation; Fedora build chroots have no internet access. Do not fetch sources or dependencies during build/test.
- For new packages, assess eligibility, source acceptability, and licensing using current [Fedora references](docs/references.md), beginning with “What can be packaged.”
- Follow `docs/development.md` for EVR and changelog policy. Before local `copr-cli` submission, run `scripts/validate.py`; the web publish workflow runs CI first.
- Never reuse or lower a published NVR if the resulting RPM could differ. A build-only change may retain an NVR only when RPM identity is verified and the build service accepts it.
- Before changing checked-in source archives, read the package README, relevant audit notes, and spec `Source` entries. Update and verify `packages/<name>/docs/checksums.sha256` with `sha256sum --check`.
- Keep package-specific audit/review records, when needed, under `packages/<name>/docs/`.
- For Fedora review submissions, publish the matching SRPM at a public, directly downloadable URL and include it in Bugzilla.
- Fetch current Fedora guidance from its official site when needed; do not add local copies to the repository. Consult COPR documentation directly.

## External references

| Need | File |
| --- | --- |
| End-user installation | `README.md` |
| Development and packaging | `docs/development.md` |
| Toolchain and commands | `docs/toolchain.md` |
| COPR setup | `docs/copr.md` |
| Fedora guidance links | `docs/references.md` |
| Fedora submission procedure | `docs/submission.md` |
| Package-specific records | `packages/<name>/docs/` |
