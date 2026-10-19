# Fedora package review notes: yazi

This is a preparation record, not evidence of Fedora review approval. The package has not yet been submitted. Evidence below was checked on 2026-10-19.

## Request

- Review bug: Not filed.
- Fedora account: Not recorded; confirm the maintainer's account and sponsorship needs before filing.
- Sponsorship requested: Not determined.
- Package summary: Terminal file manager written in Rust.
- Upstream: [Yazi v26.9.1](https://github.com/sxyazi/yazi/releases/tag/v26.9.1).
- Duplicate check: The maintainer previously confirmed there is no existing Fedora Yazi package or review; recheck before filing.

## Artifacts and build evidence

- COPR build [11168077](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11168077/) succeeded for Fedora 44, Fedora 45, and Rawhide, x86_64: `yazi-26.9.1-1`.
- Public [SRPM](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/srpm-builds/11168077/yazi-26.9.1-1.src.rpm) and [built Rawhide spec](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11168077-yazi/yazi.spec).
- [Rawhide review and lint output](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11168077-yazi/fedora-review/review.txt): binary/SRPM lint reports 0 errors and 2 warnings, both for non-URL source bundles (Source1 and Source4). Debuginfo lint reports 0 errors and 0 warnings, with filters applied. Checked upstream source checksums match. Missing-man-page warnings are gone.
- The review ran with `--prebuilt`; its Mock-build warning does not mean the COPR build failed. The installed-package section says the packages were not installed despite the passing checklist label; that section is not runtime evidence.
- Installed Fedora 44 RPM `yazi-26.9.1-1.fc44.x86_64` passes `rpm -V`. Both `yazi --version` and `ya --version` report `26.9.1` and commit `8dd895c695a5950330c2623eb43debf323b60654`.
- The installed RPM includes both manual pages, generated completions, syntax sources, and dependency/syntax license files. Requirements include `file`, system Lua 5.4, and Oniguruma; bundled-crate provides, file list, and license-file list were inspected. Installed lint has no Yazi warnings (`rpmlint -i herdr yazi`: 0 errors, 1 Herdr warning, 7 filtered).
- Yazi starts and quits with `q` successfully in a 100x24 pseudo-terminal with a temporary isolated home/config/cache/state directory. This is a host startup smoke test, not a clean-chroot or preview/integration test. A non-terminal invocation failed with an ioctl error; a PTY without dimensions also failed, so terminal dimensions must be supplied for automated TUI checks.
- `scripts/validate.py` passes for all three packages; 19 Python tests pass. Earlier local `%check` evidence reported zero upstream tests, so it should not be interpreted as functional coverage.

## Outstanding work

- Investigate the review's missing C/C++ compiler BuildRequires finding against native Cargo dependencies; add an explicit compiler requirement if needed rather than relying on a transitive dependency.
- Reconcile licensecheck findings (24,509 unknown-license files) with the source-level audit and linked-license report. Scanner counts alone are not license violations or legal approval.
- Review source-bundle provenance/regeneration notes in `../README.md`; local generated archives intentionally do not have download URLs.
- Justify check-local `%define rustflags_codegen_units 16`, and assess the documentation/data-size flags (789,451 documentation bytes and 1,054,720 bytes in `/usr/share`) before deciding whether a subpackage is useful.
- Independently inspect all binary subpackages and debug artifacts, verify build/test networking constraints, and test interactive previews, syntax highlighting, navigation, and optional integrations in clean Fedora environments. A successful x86_64 build does not validate other architectures.
- File the Fedora review request only after the manual review checks are complete; add its URL/status here.

Do not reuse `26.9.1-1` for changes to installed files or dependencies: it is now published and installed. COPR success is not official Fedora Rawhide inclusion.
