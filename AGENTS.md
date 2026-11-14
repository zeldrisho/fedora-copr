# Agent Instructions

## Toolchain

- Use `fd` to find files when available.
- Use `yq` to inspect YAML.
- Use Packit for builds; prefer `copr-cli` over raw HTTP requests for COPR operations.
- COPR log downloads use `wget`; progress and errors go to stderr. Inspect `/tmp/copr-download.log` if a download fails.

## Commands

| Task | Command |
| --- | --- |
| Check Packit paths | `python3 .packit/test-paths.py` |
| Check GitHub workflows | `actionlint` |
| Test helpers | `(for t in .github/scripts/test-*.py packages/*/test-*.py; do python3 "$t" \|\| exit "$?"; done)` |
| Test Vite+ source preparation | `bash packages/vite-plus/test-source-preparation.sh` |
| Check update support | `python3 .github/scripts/livecheck.py --check <package>` |
| Download COPR build logs | `copr-cli download-build <build-id> --logs --dest <directory> 2>/tmp/copr-download.log` |
| Request Packit PR builds | Comment `/packit build` on the PR |

## Rules

- Keep this a simple personal-use COPR, not an official Fedora submission. Ignore review suggestions that add maintenance without solving a concrete build, runtime, update, security, or redistribution problem. Fedora review conventions, exhaustive dependency-license audits, and cosmetic lint are not goals; retain applicable notices and respect COPR rules.
- Use Conventional Commits.
- Keep network access disabled for RPM builds by default; enable it for individual package builds when it makes implementation easier, and document the exception.
- Update package changelogs only for user-facing changes near release; do not add entries for unpublished package fixes.
- Do not push changes unless explicitly asked.
- Ask before installing tools or dependencies on the host.
- Adapt builds to the toolchain available on each Fedora release.
- Prefer upstream build instructions and existing packaging when useful; document important adaptations. Prebuilt dependencies are acceptable when rebuilding them adds disproportionate effort.
- Keep package changes focused; check existing issues and pull requests before duplicating work when practical.
- Recheck livecheck support when adding or changing a package; update detection/tests or document an explicit manual-update reason (see `docs/livecheck.md`).
- Review binary RPM `Requires` and `Recommends` when changing runtime dependencies; check for redundant or missing providers (see `docs/development.md`).
- Before concluding a Fedora dependency is unavailable, check alternative package names and providers; document any remaining uncertainty.
- Prefer offline functional package checks beyond version and help; document exceptions.
- Link patches to upstream issues or pull requests when available.
- Use the practical validation guidance in `docs/development.md`; report tests, target details, and significant gaps.
- Keep package specs and supporting files under `packages/<name>/`.
- Do not commit COPR credentials or webhook URLs.

## References

| Need | File |
| --- | --- |
| User installation guide | `README.md` |
| COPR setup and builds | `docs/packit.md` |
| Automated updates | `docs/livecheck.md` |
| Package notes and template | `docs/<package>.md`, `docs/template.md` |
| Packaging and validation | `docs/development.md` |
| Source RPM preparation | `.packit/prepare-sources.sh` |
| Packit PR builds | `.packit.yaml` |
