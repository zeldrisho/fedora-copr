# Package development

This guide describes how to maintain packages in this repository. For local setup and commands, see the [toolchain guide](toolchain.md). Consult the [upstream packaging references](upstream/README.md) for Fedora guidance relevant to the package being changed.

## Repository layout

```text
.copr/                  Shared SRPM preparation and COPR project metadata
.github/workflows/      Pull-request validation and main-branch publishing
packages/<name>/        Fedora spec and package-specific sources/docs
scripts/                Repository validation helpers
tests/                  Python tests for repository helpers
docs/                   Development, toolchain, COPR, and upstream guides
```

GitHub Actions validates pull requests and publishes successful pushes to `main`. CI checks EVR increases, creates and lints SRPMs, and builds binary RPMs locally in Fedora; pull requests do not receive COPR credentials or submit builds. After a validated push to `main`, a separate job synchronizes SCM recipes and submits builds only for packages with changed build inputs. Changes to shared build/CI tooling select every package; package README-only changes select none. COPR's configured chroots remain authoritative for published builds.

Every package lives in `packages/<name>/` and uses `packages/<name>/<name>.spec`; the directory, spec basename, and RPM `Name:` must match. Keep specs Fedora-submittable and COPR-specific behavior in `.copr/Makefile`. Put package-specific sources and maintenance notes alongside the spec. Check [actionlint's package notes](../packages/actionlint/README.md) before changing its checked-in Go vendor archive.

## Updating a package

1. Review the upstream release, source integrity (including upstream signatures when available), Fedora-allowed licensing, dependencies, and Fedora compatibility. See the [upstream packaging references](upstream/README.md).
2. Update `Version`, source declarations, patches, build requirements, and package documentation as needed. Regenerate checked-in vendored sources when required and keep them synchronized with the spec.
3. Use explicit `Version` and `Release` fields with a maintained `%changelog`; this repository's COPR SRPM flow does not process `%autorelease` or `%autochangelog`.
4. Ensure all sources are available when creating the SRPM. Binary RPM builds must work offline; do not fetch sources or Go modules during build or test phases. Keep `%check` deterministic and offline. Document and narrowly skip tests that require network access or unavailable release metadata.
5. For build-relevant changes to an existing package, increment `Release` and add a changelog entry, except when correcting an initial release: keep `Release: 1` only if all prior COPR builds have been withdrawn and confirmed not downloaded or installed, then retain the exact `Initial release reset: all prior COPR builds withdrawn and confirmed not downloaded or installed` changelog marker. The EVR checker permits this reset only for the same `Version`. Do not bump for documentation-only changes or COPR configuration alone.
6. Run `make validate`, then build and review a binary RPM as described in the [toolchain guide](toolchain.md). Lint the SRPM and every binary RPM; inspect metadata, dependencies, provides, files, and license files; and smoke-test an installed command where practical. `make validate` does not perform binary RPM checks.

Pull-request CI checks that RPM considers the new Version-Release greater than the merge-base value. The checker permits a reset to Release 1 for the same Version only when the current spec contains the exact initial-release reset marker above and the base spec does not, so the marker authorizes a single reset, documenting that all earlier COPR builds were withdrawn and confirmed not downloaded or installed. Never reuse a version-release that has been published with different package contents.

## Build and publish

After merge, inspect the COPR build across its configured chroots; the local CI build does not replace those target builds. See [COPR setup](copr.md) for publishing details.
