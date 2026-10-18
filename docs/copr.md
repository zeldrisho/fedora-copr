# COPR setup and publishing

This repository stages Fedora-submittable RPMs in the existing COPR project [`zeldrisho/packages`](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/). COPR uses the shared `.copr/Makefile` to prepare the SRPM; the publishing workflow is described below.

## Package entry

GitHub Actions creates or updates one SCM package entry per affected package using these settings:

| COPR field | Value |
|---|---|
| Clone URL | `https://github.com/zeldrisho/fedora-copr.git` |
| Committish | Validated push commit (`GITHUB_SHA`) |
| Subdirectory | `packages/<name>` |
| Spec file | `<name>.spec` |
| Build source | SCM |
| Build SRPM with | `make_srpm` |

The shared Makefile stages declared sources with `spectool`, then calls `rpmbuild -bs`. COPR's minimal SRPM environment may not include `spectool`; the Makefile installs `rpmdevtools` with DNF when needed. Source downloads happen during SRPM preparation. The resulting RPM build must work without internet access.

The workflow selects packages from changed package inputs; top-level package README changes alone do not trigger a build. Changes under `.copr/` select all packages for submission; CI, script, test, or root Makefile changes are validated but do not submit builds. `.copr/project.toml` records project metadata for maintainers; COPR SCM does not consume that file, so actual project/chroot settings must be configured in the COPR web UI.

## Project settings

Configure and verify the COPR project settings in the web UI:

- Chroots: Fedora 44 x86_64, Fedora 45 x86_64, and Fedora Rawhide x86_64.
- Disable internet access during binary builds.
- Enable Fedora branching.
- Disable AppStream if the packages do not provide application metadata.
- Enable fedora-review where available.
- Keep COPR's native webhook rebuilding disabled for the actionlint entry; GitHub Actions submits builds after validation.

Use the project's existing settings as authoritative; `.copr/project.toml` is documentation, not a configuration API.

## Enable automatic publishing

The `CI` workflow runs for relevant pull requests and qualifying pushes to `main`; documentation-only changes do not trigger it. It checks EVR increases, runs repository tests, verifies source-checksum manifests for all packages, and validates/lints package SRPMs. It does not build binary RPMs. After a successful `CI` run for a push to `main`, `COPR publish` selects changed package inputs, updates SCM recipes for the exact validated commit, and submits builds with `--nowait`. COPR's configured chroots build asynchronously; submission success does not mean the COPR builds succeeded. Monitor COPR results after submission.

To submit selected packages manually, run **Actions → COPR publish → Run workflow** on `main` and enter a comma-separated package list (for example, `herdr,yazi`). This runs validation before submitting the requested builds. The weekly/manual `Upstream check` workflow is separate and checks for newer releases; it does not publish packages. A documented changelog note alone is not sufficient to authorize an EVR reset; verify all prior builds were withdrawn and not downloaded or installed, then follow repository maintainer policy before such a reset.

The `Upstream check` workflow checks the latest stable GitHub release for actionlint, Herdr, and Yazi. It opens a review issue when the release tag is newer than the packaged version, using a Conventional Commit-style title such as `feat(yazi): update to 26.10.0`; it does not update specs or submit builds. Check the upstream repository and Fedora packaging constraints before acting on an issue.

Configure the repository's GitHub Actions secret once:

1. Open the COPR API configuration page while signed into the account that owns `zeldrisho/packages`.
2. Copy the generated COPR configuration, including its login and token.
3. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Name the secret `COPR_CONFIG` and paste the configuration. Treat it as a password; do not commit or print it.

The workflow does not create or modify the COPR project or its chroots; those remain configured in the COPR web UI. It manages package entries and builds for affected packages. Once the secret is configured and changes are merged to `main`, publishing and build submission are automatic. Review COPR build results to confirm completion; then install a resulting RPM in a clean Fedora environment and smoke-test the command.

A COPR build is staging, not Fedora package review or Fedora distribution approval. See the [COPR SCM documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html) for the current UI and build method.
