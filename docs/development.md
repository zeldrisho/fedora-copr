# Development

## COPR configuration

The `zeldrisho/packages` project targets Fedora 44, Fedora 45, and Rawhide on `x86_64` and `aarch64` (six chroots). Package specs and supporting files live under `packages/<name>/`.

See [repository conventions](conventions.md) for layout, naming, packaging and commit conventions, and the [package notes template](template.md) for package documentation.

A package can provide a `prepare-sources.sh` script for additional source preparation. Package-specific scripts stay next to their specs under `packages/<name>/`; shared Packit helpers are in `.packit/`, and GitHub Actions helpers are in `.github/scripts/`. A separate root `scripts/` directory is unnecessary unless there are general-purpose scripts to put there. Treat webhook URLs as secrets.

## Pull request builds

`.packit.yaml` configures package builds. Install the [Packit GitHub App](https://packit.dev/docs/guide) for this repository. PR builds use Packit's own COPR projects; they do not publish to `zeldrisho/packages`. Enabled commit jobs publish to `zeldrisho/packages` after changes reach `main`. Enabled RPM build jobs have networking disabled. Pi, Vite+, Morphe and REA require network access when their builds are enabled: they resolve dependencies or toolchains during the RPM build. SRPM preparation downloads sources and dependencies: `.packit/prepare-sources.sh` uses the existing package scripts, with their tools installed by Packit's `srpm_build_deps` instead of running `dnf` in the scripts. Package scripts verify upstream archives during SRPM preparation; Morphe also checks them during the RPM build.

Packit's [monorepo configuration](https://packit.dev/posts/monorepos) resolves each spec and SRPM action relative to its package directory. Accordingly, spec paths are filenames and archive actions invoke `../../.packit/prepare-sources.sh`; the helper returns an archive path relative to that directory. Run `python3 .packit/test-paths.py` to check these conventions without downloading sources (requires `yq`).

Packit's `srpm_build_deps` lists unversioned package names because COPR splits versioned requirements into separate install arguments. Source preparation therefore relies on the source builder providing sufficiently recent tools; RPM build dependencies remain versioned in the specs.

Hosted Packit checks have run, but the current configuration and package contents still need verification. Check each enabled package on all six targets before relying on its checks, including source builder tool versions and dependency availability. A successful build does not replace review of sources or package contents. The upstream build and other distribution packaging references are in the package notes under `docs/`. This adaptation retains those recipes and the upstream source URLs, consistent with Fedora's [Source URL guidance](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/); it changes only how source-builder tools are supplied. See Packit's [monorepo configuration](https://packit.dev/posts/monorepos), [SRPM actions](https://packit.dev/docs/configuration/actions), and [COPR build configuration](https://packit.dev/docs/configuration/upstream/copr_build).

For a manual PR rebuild, use `/packit build` on the pull request. Installing the GitHub App is not sufficient: Packit must also [approve the repository or namespace](https://packit.dev/docs/guide#2-approval), and builds must comply with COPR rules. Packit and COPR side repositories are public; check every target before merging. Custom side repositories are not covered by COPR's documented automatic cleanup of `:pr:` subdirectories; inspect and clean them up separately. Do not delete the main project to remove a side repository.

See `.packit.yaml` for the active PR and main publishing jobs; successful main builds publish automatically. Pi and Vite+ builds and livecheck updates are temporarily disabled after COPR builds [11324034](https://copr.fedorainfracloud.org/coprs/build/11324034/) and [11324037](https://copr.fedorainfracloud.org/coprs/build/11324037/) failed. Restore their commented jobs and remove their exclusions in `.github/workflows/livecheck.yml` after fixing the builds. Other package-specific blockers are recorded in their notes. A complete dependency-license audit is not a prerequisite by itself.

Job identifiers distinguish package checks. Identifiers do not guarantee parallel execution; Packit and COPR scheduling still determine when builds start. For build failures, consult the Packit dashboard and COPR logs; Packit also provides a [local reproduction guide](https://packit.dev/docs/reproduce-locally). Compare submission and start times and SRPM and chroot logs to diagnose queueing.

## Package review and validation

This is a personal COPR, not a Fedora submission. Prefer simple, maintainable builds from source, with offline RPM builds when practical. Bundled dependencies and prebuilt components are acceptable when they save disproportionate effort; document important exceptions. Ignore review suggestions that impose official Fedora process or add complexity without a concrete benefit.

For new packages and updates, review:

- The version source and stability: upstream tags, releases and registry `latest` labels can differ. Verify the chosen version and immutable source URLs and hashes; a matching checksum detects changes but does not independently prove provenance. Review all pinned inputs, lockfiles and generated source bundles together.
- Build and runtime dependencies, optional features and conflicts, including alternative Fedora package names and providers on each target. Consult the language-specific guidance: Fedora's general preference for system libraries differs from its Go and Node.js vendoring guidance. Document bundled dependencies, prebuilt artifacts, runtime downloads and their security and licensing implications.
- Keep upstream license texts and applicable notices, and consider known redistribution or corresponding-source obligations and COPR rules. An exhaustive inventory of every dependency is not required.
- Package behavior and installed contents: executable names, completions, documentation, licenses, configuration, ownership and upgrade behavior. Check whether self-update or bootstrap downloads bypass RPM management, and document any intentional exceptions.
- Downstream patches: explain why each is needed, link an upstream issue or PR where available, and revisit it on updates. Do not assume a patch can be dropped without building and testing.

For validation, run applicable offline repository tests such as `python3 .packit/test-paths.py` and `for t in .github/scripts/test-*.py packages/*/test-*.py; do python3 "$t"; done`; package-specific notes list additional tests. Prefer a `%check` that exercises installed functionality and asserts a result or failure, beyond version or help output. Run upstream test suites where practical and document tests skipped because of network, interactive requirements or other constraints.

Request Packit builds for affected packages where practical, prioritizing the Fedora releases and architectures you use. Inspect RPM contents and test installation when useful; six-target builds and rpmlint are not mandatory for every change. For failures, download logs with `copr-cli download-build <build-id> --logs --dest <directory>`. Report the tests and targets actually checked and important gaps; an SRPM build alone is not a successful RPM build.

These practices draw on the [Homebrew formula cookbook](https://docs.brew.sh/Formula-Cookbook), its [livecheck guidance](https://docs.brew.sh/Brew-Livecheck) and [contributor instructions](https://github.com/Homebrew/homebrew-core/blob/main/AGENTS.md), adapted to Packit and a personal COPR. Homebrew's acceptance rules, `brew` validation commands and commit format are not requirements for this repository.

## Publishing from main

The `zeldrisho/packages` COPR project allows `github.com/zeldrisho/fedora-copr` under **Packit allowed forge projects** and grants the `packit` COPR account builder access. Admin access is not needed if you manage the project's chroots yourself. If main jobs are re-enabled, they use the project's enabled chroots; verify they match the six PR targets. Keep any existing COPR SCM auto-rebuild disabled to avoid duplicate builds; this repository no longer supplies a direct SCM build method.

A successful main build publishes directly to the repository; it is not gated by PR builds unless GitHub branch protection requires the appropriate checks. The main build runs after merge and can fail independently. Verify actual package selection and build results in Packit and COPR: changes to shared configuration may rebuild multiple packages. Packit's custom project permissions and forge allowlist are described in its [COPR build documentation](https://packit.dev/docs/configuration/upstream/copr_build#using-a-custom-copr-project).

## Version updates and migration cleanup

The scheduled or manually dispatched `.github/workflows/livecheck.yml` discovers update support from package specs and checksum files, then opens a PR for each newer stable version. There is no package-name allowlist. Run `python3 .github/scripts/livecheck.py --check <package>` after adding a package or changing its version/source layout; `--discover` lists eligible packages offline and reports why others need manual work.

Detection prefers npm's `latest` dist-tag for npm `Source0` URLs (including scoped packages). Otherwise it infers the GitHub repository from `Source0` or the spec's `URL` and checks the latest published, non-prerelease release. Repositories without GitHub Releases fall back to the first 100 tags, selecting the highest recognized stable numeric version. Versions can have one or more numeric components, including two- and four-part and calendar versions; `v` and simple release-name prefixes are accepted. Prerelease suffixes are rejected. Source URLs are expanded from the spec rather than constructed for a particular package or download host.

The updater accepts an HTTPS `Source0` containing `%{version}`, literal numeric `Version`/`Release` fields, and exactly one `source.sha256` or `checksums.sha256`. It supports `%{name}` and `%{version}` in remote sources and RPM `#/filename` aliases. A manifest's filenames must map unambiguously to remote `Source` URLs; every versioned remote source must be checksummed. All sources are downloaded and hashed before files change. Unknown macros/layouts fail closed instead of guessing.

All current packages support version and checksum update PRs, but the workflow excludes Pi and Vite+ until their builds are fixed. For a future recipe that cannot safely do so, add `# livecheck: manual REASON` to its spec; livecheck then opens a proposal PR containing `livecheck-update.txt` instead of changing the spec. Complete the update and remove that file before merging.

Among packages with supported update detection, Vite+ needs the most update attention: it has multiple source snapshots, native dependency pins and a network-enabled build. Pi resolves npm dependencies at build time and may need its native patch or pinned notice inputs updated. Herdr also needs attention when its Rust/Zig requirements or patch change; Yazi when its Rust or Lua layout changes. Smali's release-based detection can miss newer tags, and its generated Java sources and runtime must stay compatible. Homebrew's launcher/bootstrap behavior should be checked when upstream changes; its writable installation updates separately from RPM. Actionlint and gomi are usually straightforward version/checksum updates, subject to Go toolchain and build changes. All update PRs still need their relevant build results checked.

The deterministic updater changes the spec version, release, changelog, and applicable checksum file; Pi may propose additional package changes. Update PRs include an advisory comparison of selected dependency manifests, build files, and license/notice files in the old and new Source0 archives. The comparison hashes files without extracting them; it does not inspect auxiliary sources, patch applicability, package requirements, provenance, or the full source diff. Unsupported or oversized archives and other errors are reported as unavailable and require manual review. Run the repository helper tests with the glob loop above; CI runs the same set separately from RPM sources. Review each update and all Packit builds before merging; there is no automatic merge. Existing `automation/update-<package>-<version>` branches are never overwritten; delete a stale branch to retry that version. If PR creation fails after the push, recover the branch manually. Repository helper tests run in CI separately from RPM sources.

Livecheck calls `.github/workflows/pi.yml` for each discovered package. When an update exists, Pi reads the release notes for every version since the packaged one, updates coordinated package inputs, runs practical checks, and writes the PR body; the deterministic version and checksum changes still come from livecheck. A manual-update marker stays in place when Pi cannot complete the proposal safely. Set the Actions variable `PI_MODEL` to a Pi model identifier and the secret `AI_GATEWAY_API_KEY` to its AI Gateway API key. Pi runs without a repository token, and a separate job publishes its package-local patch after `.github/scripts/verify-update.py` confirms the staged files stay in that package. The model runs commands with network access through its own API key, so untrusted upstream content can still lead to disclosure or unsafe changes; review all output and do not use a privileged key. Pi has no browser tool, so it fetches release notes and upstream files with `gh api` and `git`, or `vp view PACKAGE [FIELD]` for npm upstreams, through its shell tool, using the read-only `GITHUB_TOKEN` supplied to that step. A failed Pi run creates no PR.

The workflow does not merge or repair builds. When a Packit build fails, its check links to the Packit job, whose API exposes the COPR build and logs for a follow-up agent session or manual repair. Fixing the PR then produces a new commit and rebuild. Control the staged update check with the helper tests above.

The update workflow uses GitHub Actions' built-in `GITHUB_TOKEN` to create branches and PRs. In repository Settings → Actions → General → Workflow permissions, enable **Allow GitHub Actions to create and approve pull requests**. The workflow itself does not approve PRs. GitHub Actions workflows triggered by these PRs require approval; verify that Packit receives the PR event and builds it, or trigger a build manually using `/packit build`. Packit itself still requires its own GitHub App.

Review branch protection and replace any required checks from the removed COPR workflow with appropriate Packit checks once builds are verified.

Kotlin Toolchain now packages only an upstream bootstrap wrapper, which downloads the separately licensed distribution at user runtime. RPM builds stay offline. Its Packit jobs remain disabled pending clarification of COPR's runtime-download policy. See [Kotlin Toolchain packaging notes](kotlin-toolchain.md).

Pi's Packit jobs are disabled pending a successful Fedora build; see [Pi packaging notes](pi-coding-agent.md).

Smali's Java build is experimental. The spec now requires Java 25 and defaults its launchers to that JDK, matching the build; the changed RPM and launchers still need Fedora build and installation tests. See [Smali packaging notes](smali.md).

## References

- [COPR user documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html) — builds, webhooks and allowed content.
- [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/) — optional guidance for RPM packaging.
- [Fedora Packaging Tutorial](https://docs.fedoraproject.org/en-US/package-maintainers/Packaging_Tutorial/) — an introduction to creating RPM packages.
- [Fedora package review](https://docs.fedoraproject.org/en-US/packaging-guidelines/ReviewGuidelines/) and [licensing](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) — review checklist and license metadata and texts.
- Fedora language guidance: [Go](https://docs.fedoraproject.org/en-US/packaging-guidelines/Golang/), [Rust](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/), [Node.js](https://docs.fedoraproject.org/en-US/packaging-guidelines/Node.js/) and [Java](https://docs.fedoraproject.org/en-US/packaging-guidelines/Java/).
- [Source URLs](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/), [versioning](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/), [scriptlets](https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/) and [dependency filtering](https://docs.fedoraproject.org/en-US/packaging-guidelines/AutoProvidesAndRequiresFiltering/) — guidance for those specific changes.
