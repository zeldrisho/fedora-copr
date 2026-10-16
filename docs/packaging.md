# Fedora packaging policy notes

This guide captures practical Fedora packaging requirements relevant to this repository. It is a maintenance aid, not a replacement for the full [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/), language-specific guidance, or the formal [package review process](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Review_Process/).

## Package review and maintainership

Fedora packages are maintained collectively. A reviewer identifies guideline issues; the packager addresses them and documents justified deviations. Packages submitted to Fedora must follow the review process, in addition to passing local checks and COPR builds. COPR is a staging facility, not Fedora approval or Fedora's canonical package source.

The guidelines use MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in the RFC 2119 sense. If a SHOULD-level rule cannot reasonably be followed, explain why in a spec comment. A MUST-level exception requires Packaging Committee approval; a comment alone is not permission to ignore it.

## Spec naming and metadata

- Store one spec as `packages/<name>/<name>.spec`.
- Make the package directory, spec filename, and spec `Name:` agree.
- Keep specs readable and use Fedora RPM macros and conditionals appropriately.
- Use a concise summary (normally no more than 80 columns) without a trailing period; write a useful description without installation instructions.
- Do not add `Packager:`, `Vendor:`, `Copyright:`, `PreReq:`, or `BuildRoot:` tags. Avoid obsolete `Group:` and `%clean` sections.
- Avoid `Epoch:` unless it is the last practical option; it is difficult to remove later.
- Keep package-specific COPR settings out of specs. Do not use rpkg template syntax.

## Version, release, and changelog

Use the upstream version and a Fedora-appropriate explicit release. This repository's COPR SCM source method creates SRPMs with `rpmbuild -bs`, not Fedora dist-git rpmautospec processing. Therefore use `Release: N%{?dist}` and maintain `%changelog` entries rather than relying on `%autorelease` and `%autochangelog`; see the [release process](release.md). Keep release changes meaningful and do not bump for COPR configuration alone. Changelog entries should explain user-visible updates, fixes, or changes, not routine spec cleanup.

## License and source integrity

- Use an SPDX license expression accepted by Fedora and ensure it accurately represents shipped code.
- Include upstream license text in the RPM with `%license`; do not confuse this repository's MIT license for tooling/docs with the packaged application's license.
- Prefer authenticated HTTPS URLs in `URL:`, `Source:`, and `Patch:` tags.
- When upstream publishes signatures, Fedora recommends verifying them during `%prep` with `%{openpgpverify}` before running potentially untrusted source code. Ship required public keyrings and signatures as specified by the guidelines.
- Keep source archives and patches identified in the spec and SRPM. Do not fetch software sources during `%build`, `%check`, or `%install`.

COPR source downloads happen while preparing the SRPM. The resulting Fedora build must be offline-capable and get all source inputs from the SRPM or repository. The packaging Makefile stages sources before calling `rpmbuild`; it is not permission for build scripts to depend on network access.

## Dependencies and building

- Declare necessary build dependencies with `BuildRequires:` or supported language-specific dependency generators.
- Do not use architecture-specific (`%{?_isa}`) `BuildRequires:`; source RPM build requirements must not vary with the host architecture.
- Runtime dependencies must be correct and satisfiable from official Fedora repositories.
- Prefer Fedora system libraries over bundled copies when upstream supports this. If bundling is unavoidable, document it with the appropriate `Provides: bundled(...)` and follow up with upstream.
- Let RPM generate library dependencies where possible; avoid redundant explicit `Requires:`.
- Honor Fedora compiler and hardening flags. Add tests to `%check` where practical and keep tests offline and deterministic.

For Go programs, use Fedora's Go RPM macros and follow current Fedora Go guidance on vendoring. When dependencies are vendored, use Go Vendor Tools to generate a normalized vendor archive, audit dependency licenses, install license files, and record bundled module metadata. Never download Go modules during an isolated Fedora build. Actionlint uses a checked-in vendor archive as `Source1`; the Go compiler reads it offline. A small number of tests are skipped because they need live network access or Git metadata absent from the release archive.

## Files, paths, and ownership

- Install files under Fedora filesystem locations using RPM directory macros where practical.
- Do not package files under `/usr/local`, `/home`, or `/srv`; do not create new top-level directories without approval.
- Use `%{_libdir}` for binary libraries. Use `%{_libexecdir}/%{name}` for package-private helper programs when appropriate.
- Explicitly list installed files in `%files`; avoid broad globs such as `%{_bindir}/*` or `%{_datadir}/*`.
- Ensure every installed file and directory has proper ownership and permissions. Include relevant upstream documentation without adding runtime dependencies or affecting behavior.
- Mark configuration files `%config(noreplace)` by default, unless preserving changed configuration would break upgrades; explain exceptions in the spec.
- Include man pages for command-line tools when available. For localized files, use `%find_lang` rather than broad locale-directory globs.

## Updating actionlint's Go vendor source

`packages/actionlint/actionlint-<version>-vendor.tar.bz2` is generated source checked into this monorepo so COPR and Fedora builds do not need the Go module network. `go-vendor-tools.toml` records the license detector configuration. The spec uses Go Vendor Tools to verify the combined SPDX license expression and install upstream and vendored license texts; its generated `bundled(golang(...))` provides identify included modules.

For vendor archive regeneration commands and actionlint-specific maintenance notes, see [`packages/actionlint/README.md`](../packages/actionlint/README.md). Keep the vendor archive and spec in sync, review generated license metadata, rerun `make validate`, and run a full RPM build. Do not replace the checked-in vendor source with a build-time module download.

## Validation before proposing changes

Run `make validate` after spec changes. It checks package/spec/Name agreement, expands the spec with `rpmspec -P`, creates an SRPM through the exact COPR Makefile target, and runs rpmlint against the spec and SRPM. Successful COPR binary builds should additionally verify compilation, installation, file lists, and `%check`. Passing COPR validation does not replace Fedora package review.

## Further reading

- [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/)
- [Fedora Package Maintainers](https://docs.fedoraproject.org/en-US/package-maintainers/)
- [COPR user documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html)
