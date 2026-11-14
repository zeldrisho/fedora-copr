# Package updates

The scheduled or manually dispatched `.github/workflows/livecheck.yml` discovers update support from specs and checksum files and proposes PRs for newer stable versions. Run `python3 .github/scripts/livecheck.py --check <package>` after adding a package or changing its version/source layout. `--discover` lists eligible packages offline and reports why others need manual work. Pi and Vite+ are excluded until their builds are fixed. After validation, restore their commented Packit jobs in `.packit.yaml` and remove their exclusions from `.github/workflows/livecheck.yml`. See their package notes for blockers and coordinated inputs.

The [Homebrew livecheck guidance](https://docs.brew.sh/Brew-Livecheck) is a useful reference, not a requirement for this repository.

## Detection and source layout

Detection prefers npm's `latest` dist-tag for npm `Source0` URLs, including scoped packages. Otherwise it infers a GitHub repository from `Source0` or the spec's `URL` and checks the latest published non-prerelease release. Repositories without releases fall back to the first 100 tags and the highest recognized stable numeric version. Versions can have one or more numeric components, including calendar versions; `v` and simple release-name prefixes are accepted, while prerelease suffixes are rejected.

The updater requires an HTTPS `Source0` containing `%{version}`, literal numeric `Version` and `Release`, and exactly one `source.sha256` or `checksums.sha256`. It expands `%{name}` and `%{version}` in remote sources and supports RPM `#/filename` aliases. Manifest filenames must map unambiguously to remote sources, and every versioned remote source must be checksummed. It downloads and hashes all inputs before changing files; unsupported macros and layouts fail closed.

For recipes that cannot safely update this way, add `# livecheck: manual REASON` to the spec. Livecheck opens a proposal PR containing `livecheck-update.txt` instead of changing the spec. Complete the update and remove that file before merging.

## Review and recovery

The deterministic updater changes the spec version, release, changelog and applicable checksums; Pi may propose additional package-local changes. PRs include an advisory comparison of selected dependency manifests, build files and license/notice files in old and new `Source0` archives. It hashes files without extraction but does not inspect auxiliary sources, patch applicability, package requirements, provenance or the full diff. Unsupported or oversized archives and errors are reported as unavailable and require manual review.

Review all updates and applicable Packit builds; nothing merges automatically. Existing `automation/update-<package>-<version>` branches are never overwritten: delete a stale branch to retry. If PR creation fails after the push, recover the branch manually. See [validation guidance](development.md#testing-and-validation) and [Packit](packit.md) for build troubleshooting.

## Pi review and permissions

Livecheck calls `.github/workflows/pi.yml` for each discovered package. When an update exists, Pi reads release notes since the packaged version, updates coordinated inputs, runs practical checks and writes the PR body. A manual-update marker stays in place if Pi cannot safely complete the proposal. A failed Pi run creates no PR.

Set the Actions variable `PI_MODEL` to a Pi model identifier and the secret `AI_GATEWAY_API_KEY` to its AI Gateway API key. Pi runs without a repository write token; a separate job publishes its package-local patch after `.github/scripts/verify-update.py` checks staged paths. Pi runs commands with network access, so untrusted upstream content can still cause disclosure or unsafe changes. Review its output and do not use a privileged key. Pi fetches release notes and upstream files through shell commands such as `gh api`, `git`, or `vp view`, using the read-only `GITHUB_TOKEN` supplied to that step.

The publishing workflow uses GitHub Actions' `GITHUB_TOKEN` to create branches and PRs. Enable **Allow GitHub Actions to create and approve pull requests** in repository Settings → Actions → General → Workflow permissions; the workflow does not approve PRs. Workflows triggered by these PRs require approval. Verify that Packit receives the event or request `/packit build` manually; Packit also requires its GitHub App.
