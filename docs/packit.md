# Packit and COPR builds

The `zeldrisho/packages` project targets Fedora 44, Fedora 45 and Rawhide on `x86_64` and `aarch64`. See `.packit.yaml` for enabled jobs and package notes for blockers. Hosted checks have run, but verify the current configuration, source-builder tools, dependencies and target builds before relying on them. A successful build does not replace source and package review.

## Setup and source preparation

Install the [Packit GitHub App](https://packit.dev/docs/guide); Packit must also [approve the repository or namespace](https://packit.dev/docs/guide#2-approval). Builds must comply with COPR rules. Treat webhook URLs as secrets.

Packit's [monorepo configuration](https://packit.dev/posts/monorepos) resolves specs and SRPM actions relative to each package directory. Spec paths are filenames; archive actions invoke `../../.packit/prepare-sources.sh`, which returns an archive path relative to that directory. It downloads sources and invokes package-specific preparation scripts when present. Packit installs their tools using `srpm_build_deps`, which lists unversioned package names because COPR splits versioned requirements into separate install arguments. The source builder must therefore provide sufficiently recent tools; spec build requirements remain versioned. Run `python3 .packit/test-paths.py` to check paths without downloading sources; it requires `yq`.

RPM build jobs have networking disabled except for the Vite+, Morphe, Pi and REA builds, which download dependencies and toolchains. SRPM preparation may download sources and dependencies; package scripts verify upstream archives. See package notes for exceptions and unresolved blockers.

## Pull request builds

PR builds run automatically in Packit's own COPR projects; they do not publish to `zeldrisho/packages`. Packit and COPR side repositories are public. Custom side repositories are not covered by COPR's documented automatic cleanup of `:pr:` subdirectories; inspect and clean them separately. Do not delete the main project to remove a side repository.

Package `paths` in `.packit.yaml` identify package directories and shared Packit configuration; they do not filter service jobs by changed files ([upstream issue](https://github.com/packit/packit-service/issues/2006)). Automatic builds may therefore include unaffected packages. Job identifiers distinguish checks but do not guarantee parallel execution.

## Publishing from main

The COPR project allows `github.com/zeldrisho/fedora-copr` under **Packit allowed forge projects** and grants the `packit` account builder access. Admin access is unnecessary if you manage project chroots yourself. Main jobs use the project's enabled chroots; verify they match the intended targets. When a package cannot build on a release yet, pin `targets` on both its PR and main jobs, record the blocking dependency in `docs/<package>.md`, and add the remaining chroots back once it is available; rea is the current example. Keep any existing COPR SCM auto-rebuild disabled to avoid duplicate builds. See [Packit's custom project configuration](https://packit.dev/docs/configuration/upstream/copr_build#using-a-custom-copr-project).

A successful enabled main job publishes directly to the COPR. It runs after merge and can fail independently of a PR build; PR builds are not a gate unless branch protection requires their checks. Verify selection and results in Packit and COPR. Review branch protection when changing required checks.

## Troubleshooting

Consult the Packit dashboard and COPR SRPM and chroot logs; compare submission and start times when diagnosing queues. Download logs with:

```sh
copr-cli download-build <build-id> --logs --dest <directory> 2>/tmp/copr-download.log
```

Inspect `/tmp/copr-download.log` if the download fails. Packit also provides a [local reproduction guide](https://packit.dev/docs/reproduce-locally). See [COPR documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html) and [Packit build configuration](https://packit.dev/docs/configuration/upstream/copr_build).
