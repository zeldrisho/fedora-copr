# Fedora packaging policy notes

This guide captures the practical Fedora packaging requirements relevant to this repository. It is a maintenance aid, not a replacement for the full [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/), any language-specific guidance, or the formal [package review process](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Review_Process/).

## Package review and maintainership

Fedora packages are maintained collectively. A reviewer identifies specific guideline issues; the packager addresses them and documents justified deviations. Packages submitted for Fedora must follow the review process, in addition to passing local checks and COPR builds. COPR is a staging facility, not Fedora approval or Fedora's canonical package source.

The guidelines use MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in the RFC 2119 sense. If a SHOULD-level rule cannot reasonably be followed, explain the reason in a spec comment. A MUST-level exception requires Packaging Committee approval; a spec comment alone is not permission to ignore it.

## Spec naming and metadata

- Store one spec as `packages/<name>/<name>.spec`.
- Make the package directory, spec filename, and the spec's `Name:` agree.
- Keep specs readable, using Fedora RPM macros and conditionals only.
- Use a concise summary (normally no more than 80 columns) without a trailing period; write a useful description without installation instructions.
- Do not add `Packager:`, `Vendor:`, `Copyright:`, `PreReq:`, or `BuildRoot:` tags. Avoid obsolete `Group:` and `%clean` sections.
- Avoid `Epoch:` unless it is the last practical option; an epoch is difficult to remove later.
- Keep package-specific COPR settings out of specs. Do not use rpkg template syntax.

## Version, release, and changelog

Use the upstream version and a Fedora-appropriate release. Keep release changes meaningful and do not bump it for COPR configuration alone. Fedora's recommended changelog approach is `%autochangelog`, which derives entries from Git commits; the commit subject should describe the user-relevant package change. A manual `%changelog` is also allowed. Changelog messages should explain upstream updates, fixes, or changes users will notice, not routine spec-file cleanup.

## License and source integrity

- Use an SPDX license expression accepted by Fedora and ensure it accurately represents the shipped code.
- Include upstream license text in the RPM with `%license`; do not confuse the repository's MIT license for tooling/docs with the license of each packaged application.
- Prefer authenticated HTTPS URLs in `URL:`, `Source:`, and `Patch:` tags.
- When upstream publishes signatures, Fedora recommends verifying them during `%prep` with `%{openpgpverify}`, before running potentially untrusted source code. Ship required public keyrings and signatures as specified by the guidelines.
- Keep source archives and patches identified in the spec and in the SRPM. Do not fetch software sources during `%build`, `%check`, or `%install`.

COPR source downloads happen when the SRPM is prepared. The resulting Fedora build must be offline-capable and must get all source inputs from the SRPM or repository. The packaging Makefile stages sources before calling `rpmbuild`; it is not a license to make build scripts depend on network access.

## Dependencies and building

- Declare all necessary build dependencies with `BuildRequires:` or supported language-specific dependency generators.
- Do not use architecture-specific (`%{?_isa}`) `BuildRequires:`; source RPM build requirements must not vary with the host architecture.
- Runtime dependencies must be correct and satisfiable from official Fedora repositories.
- Prefer Fedora's system libraries over bundled copies when upstream supports that. If bundling is unavoidable, document it with the appropriate `Provides: bundled(...)` and follow up with upstream.
- Let RPM generate library dependencies where possible; avoid redundant explicit `Requires:`.
- Honor Fedora compiler and hardening flags. Add tests to `%check` where practical and keep tests offline and deterministic.

For Go programs, use Fedora's Go RPM macros, and follow the current Fedora Go guidance on vendoring. When dependencies are vendored, use Go Vendor Tools to generate a normalized vendor archive, audit dependency licenses, install the license files, and record bundled module metadata. Never download Go modules during an isolated Fedora build. `actionlint` uses a checked-in vendor archive as `Source1`; the Go compiler reads that archive offline. The package skips a small number of tests that require either live network access or Git metadata absent from the release tarball.

## Files, paths, and ownership

- Install files under Fedora filesystem locations using RPM directory macros where practical.
- Do not package files under `/usr/local`, `/home`, or `/srv`; do not create new top-level directories without approval.
- Use `%{_libdir}` for binary libraries. Use `%{_libexecdir}/%{name}` for package-private helper programs when appropriate.
- Explicitly list installed files in `%files`; avoid broad globs such as `%{_bindir}/*` or `%{_datadir}/*`.
- Ensure every installed file and directory has proper ownership and permissions. Include relevant upstream documentation, but avoid documentation that adds runtime dependencies or affects program behavior.
- Mark configuration files with `%config(noreplace)` by default, unless preserving changed configuration would break upgrades; explain exceptions in the spec.
- Include man pages for command-line tools when available. For localized files, use `%find_lang` rather than broad locale-directory globs.

## Updating actionlint's Go vendor source

`packages/actionlint/actionlint-<version>-vendor.tar.bz2` is a generated source input and is checked into this monorepo so COPR and Fedora builds do not need the Go module network. `go-vendor-tools.toml` records the license detector configuration. The spec uses Go Vendor Tools to verify the combined SPDX license expression and install the upstream and vendored license texts; its generated `bundled(golang(...))` provides identify included modules.

When updating actionlint, install `go2rpm` if needed, obtain the matching upstream release archive, update `Version:` and the Go tag in the spec, then regenerate and review the vendor archive from `packages/actionlint/`:

```sh
spectool -g actionlint.spec
go_vendor_archive create --config go-vendor-tools.toml --write-config actionlint.spec
go_vendor_license --config go-vendor-tools.toml --path actionlint.spec \\
  report --prompt --autofill auto --write-config --update-spec
```

Review the generated license expression and changes to the vendor archive/config. Keep the archive and spec in sync, rerun `scripts/validate.py`, and run a full RPM build. Do not replace the checked-in vendor source with a build-time module download.

## Validation before proposing changes

Run `scripts/validate.py` after spec changes. It checks package/spec/Name agreement, expands the spec with `rpmspec -P`, creates the SRPM through the exact COPR Makefile target, and runs rpmlint against the spec and SRPM. A local full build should additionally test compilation, installation, package file lists, and `%check` in an isolated Fedora environment (for example, Mock). Passing COPR validation does not replace Fedora package review.

## Further reading

- [Fedora Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/)
- [Fedora Package Maintainers](https://docs.fedoraproject.org/en-US/package-maintainers/)
- [COPR user documentation](https://docs.copr.fedorainfracloud.org/user_documentation.html)
