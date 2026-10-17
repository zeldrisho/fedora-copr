# Fedora package review notes: yazi

This is a preparation record, not evidence of Fedora review approval. The package has not yet been submitted.

## Request

- Review bug: Not filed.
- Fedora account: Not recorded; confirm the maintainer's account and sponsorship needs before filing.
- Sponsorship requested: Not determined.
- Package summary: Terminal file manager written in Rust.
- Upstream: [Yazi v25.5.28](https://github.com/sxyazi/yazi/releases/tag/v25.5.28).
- Duplicate check: The maintainer confirmed there is no existing Fedora Yazi package or review.

## Artifacts and build evidence

- Spec: `packages/yazi/yazi.spec` (no public URL yet).
- SRPM: `~/rpmbuild/SRPMS/yazi-25.5.28-1.fc44.src.rpm` (not publicly hosted).
- SRPM SHA-256: `3fc3db59c61196c8d6aaeb69dd0832e8d93f09a056095d4c1095b0618ef2b359`.
- Local binary RPM: `~/rpmbuild/RPMS/x86_64/yazi-25.5.28-1.fc44.x86_64.rpm`.
- Binary RPM SHA-256: `c19e01470717b0f92742eefe0d2bea7a3305a99bcf2f8752cfd888f0fb843fd9`.
- Source checksums: recorded in [`audit.md`](audit.md).
- Host build log: `~/rpmbuild/BUILD/yazi-review/fedora44-host-rebuild.log` (SHA-256 `22f8c037a3f89ac688c94dd55740f2090e1b80375f51f9010d95b426b55a1e91`).
- Clean-chroot build URL/log and target: Pending COPR CI. The completed local build was on Fedora 44 host and is not clean-chroot evidence.
- Automated report: `scripts/validate.py` passed for both repository packages. The SRPM/spec rpmlint run reported no errors or warnings after package-local filters. All 13 repository unit tests and `actionlint .github/workflows/ci.yml` passed.

The SRPM rebuilt successfully on Fedora 44 using the checked-in Cargo vendor archive. The Cargo build and `%check` phases completed. `%cargo_test` executed test harnesses reporting zero tests, so this is not evidence of Rust unit-test coverage. The filtered syntax database was independently checked with syntect 5.2.0: it retains 200 definitions, excludes the five audited grammars, and loads through syntect's runtime API.

## Packaging checks

- Build and `%check`: Fedora 44 host rebuild succeeded. `%check` completed; the two Rust test harnesses each reported zero tests. Clean-chroot verification remains pending.
- Lint: SRPM/spec validation had zero errors or warnings. Binary rpmlint had zero errors and two warnings, both `no-manual-page-for-binary` for `yazi` and `ya`.
- License expression and source-level licensing review: See [`audit.md`](audit.md). Fedora Legal explicitly approved the Sublime Text Packages permission under `LicenseRef-Fedora-UltraPermissive` in [license-data issue #516](https://gitlab.com/fedora/legal/fedora-license-data/-/work_items/516) and [MR !574](https://gitlab.com/fedora/legal/fedora-license-data/-/merge_requests/574). The audit covers the other included syntax sources and the five excluded grammars.
- Bundled dependency provides and installed license/notice files: `cargo-vendor.txt`, `LICENSE.dependencies`, `LICENSE.ssh-config`, and `LICENSE.syntaxes` are listed as RPM license files. The syntax-source archive is installed under `/usr/share/doc/yazi/`. The binary RPM declares runtime requirements on `liblua-5.4.so` and `libonig.so.5`.
- Installed-package/runtime checks: Installed on Fedora 44; `rpm -V yazi` reported no differences; `yazi --version` and `ya --version` reported 25.5.28.

## Outstanding work and follow-up

- Pending checks: Run the package through COPR CI and retain the clean-chroot build URL/log and target details. The local host build does not replace this evidence. Confirm the package's remaining source/license inventory in reviewer feedback.
- Reviewer feedback/status: Not submitted; no review bug exists yet.
- Next steps: Push the package changes and obtain COPR CI build evidence; then publish immutable matching spec/SRPM URLs and logs, file the Fedora package review request, and replace this record with the review URL, artifact links, and reviewer status.
