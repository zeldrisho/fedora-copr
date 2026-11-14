# Package updates

The scheduled or manually dispatched `.github/workflows/livecheck.yml` discovers update support from specs and checksum files and proposes PRs for newer stable versions. Run `python3 .github/scripts/livecheck.py --check <package>` after adding a package or changing its version/source layout. `--discover` lists eligible packages offline and reports why others need manual work. Vite+ and Morphe are excluded until their Packit builds are validated. Remove their exclusions from `.github/workflows/livecheck.yml` after a successful build. See their package notes for blockers and coordinated inputs.

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

Create a dedicated, single-purpose AI Gateway key with provider-enforced spending and model limits. Set Actions secret `AI_GATEWAY_API_KEY` and variable `PI_MODEL` to a Pi model identifier. Every eligible update uses the agent; disable the workflow itself to pause updates. The workflow intentionally installs the latest Pi without a version pin, accepting the risk of upstream tool and dependency changes.

Pi runs without a repository write token; a separate job validates the patch using a disposable index before applying it. Pi runs commands with network access and can read the gateway key, so prompt injection in upstream content can disclose it or cause unsafe changes. Spending limits reduce the impact, not the chance of disclosure. Review the actual diff and sources, not just the agent-written report. Pi fetches release notes and upstream files through shell commands such as `gh api`, `git`, or `vp view`, using the read-only `GITHUB_TOKEN` supplied to that step.

The publishing workflow uses GitHub Actions' `GITHUB_TOKEN` to create branches and PRs. Enable **Allow GitHub Actions to create and approve pull requests** in repository Settings → Actions → General → Workflow permissions; the workflow does not approve PRs. Workflows triggered by these PRs require approval. Verify that Packit receives the event; Packit also requires its GitHub App.
