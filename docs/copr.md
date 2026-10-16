# COPR setup and publishing

This repository stages Fedora-submittable RPMs in the existing COPR project [`zeldrisho/packages`](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/). GitHub Actions validates changes and, after a successful push to `main`, uses the COPR API to create or update the SCM package entry and submit a build. COPR uses the shared `.copr/Makefile` to prepare the SRPM.

## Package entry

GitHub Actions creates or updates the actionlint SCM package entry using these settings:

| COPR field | Value |
|---|---|
| Clone URL | `https://github.com/zeldrisho/fedora-copr.git` |
| Committish | `main` |
| Subdirectory | `packages/actionlint` |
| Spec file | `actionlint.spec` |
| Build source | SCM |
| Build SRPM with | `make_srpm` |

The shared Makefile stages declared sources with `spectool`, then calls `rpmbuild -bs`. Source downloads happen during SRPM preparation. The RPM build must work without internet access.

For another package, substitute `packages/<name>` and `<name>.spec`. `.copr/project.toml` records project metadata for maintainers; COPR SCM does not consume that file, so actual project/chroot settings must be configured in the COPR web UI.

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

The `CI` workflow runs validation for pull requests and pushes to `main`. After validation passes on `main`, it idempotently creates or updates the package SCM recipe and submits the COPR build. It disables COPR's native webhook rebuild for that entry so one Git push does not submit duplicate builds.

Configure the repository's GitHub Actions secret once:

1. Open the COPR API configuration page while signed into the account that owns `zeldrisho/packages`.
2. Copy the generated COPR configuration, including its login and token.
3. In GitHub, open **Settings → Secrets and variables → Actions → New repository secret**.
4. Name the secret `COPR_CONFIG` and paste the configuration. Treat it as a password; do not commit or print it.

The workflow does not create or modify the COPR project or its chroots; those remain configured in the COPR web UI. It manages only the `actionlint` package entry and build. Once the secret is configured and changes are merged to `main`, publishing and build submission are automatic. Review workflow and COPR logs to confirm build completion; then install a resulting RPM in a clean Fedora environment and smoke-test the command.

A COPR build is staging, not Fedora package review or Fedora distribution approval. See the [COPR SCM documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html) for the current UI and build method.
