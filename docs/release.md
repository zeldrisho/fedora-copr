# Release process

## Updating a package

1. Check the upstream release and review its source archive, license, dependencies, and Fedora compatibility.
2. Update the package's `Version`, `Source` declarations, patches, build requirements, and package-specific documentation as needed.
3. Use a new `Release` for build-relevant changes to an unchanged upstream version. Add a meaningful `%changelog` entry. Do not change the release for COPR-only settings or documentation-only changes.
4. Regenerate any checked-in vendored sources when required; document the process in that package's README.
5. Run `make validate` to check the spec and SRPM.
6. Review the built RPM's metadata and files, then install it in a clean environment and smoke-test the application.
7. Commit and push the changes. Inspect the COPR build and logs for every configured target chroot.

## Release and changelog policy

COPR calls `rpmbuild -bs` through `.copr/Makefile`; this is not Fedora dist-git's rpmautospec processing pipeline. In this SCM flow `%autorelease` and `%autochangelog` may be left unexpanded or produce a generic changelog, so specs here use an explicit `Release:` and maintained `%changelog` entries. Verify the SRPM metadata when changing the source preparation flow; do not assume that a successful SRPM command generated an appropriate release history.

Increment `Release` when package bits change without an upstream version change. A changed NEVRA is necessary for clients to receive a rebuild as an update. Keep release numbers monotonic for the same version and avoid reusing a published version-release for different bits.

## Build gates

- `make validate` succeeds and rpmlint findings are reviewed.
- The SRPM contains all declared sources and the expected expanded package metadata.
- COPR binary builds pass for the intended Fedora release(s) and architecture(s).
- The installed package's files, license, and command behavior are checked.
- COPR chroot results are successful before relying on the build being available to users.

COPR is a staging service. Submission to Fedora requires following Fedora's package review and maintainership process independently.
