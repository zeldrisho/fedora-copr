# Fedora package review notes: yazi

This is a preparation record, not evidence of Fedora review approval. The package has not yet been submitted. Evidence below was checked on 2026-10-19.

## Request

- Review bug: Not filed.
- Fedora account: Not recorded; confirm the maintainer's account and sponsorship needs before filing.
- Sponsorship requested: Not determined.
- Package summary: Terminal file manager written in Rust.
- Upstream: [Yazi v26.9.1](https://github.com/sxyazi/yazi/releases/tag/v26.9.1).
- Duplicate check: A current Fedora dist-git check returned 404 for `rpms/yazi`; Fedora Bugzilla Package Review API returned zero Yazi matches. Recheck before filing.

## Artifacts and build evidence

- COPR build [11168077](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11168077/) succeeded for Fedora 44, Fedora 45, and Rawhide, x86_64: `yazi-26.9.1-1`.
- Public [SRPM](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/srpm-builds/11168077/yazi-26.9.1-1.src.rpm) and [built Rawhide spec](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11168077-yazi/yazi.spec).
- [Rawhide review and lint output](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11168077-yazi/fedora-review/review.txt): binary/SRPM lint reports 0 errors and 2 warnings, both for non-URL source bundles (Source1 and Source4). Debuginfo lint reports 0 errors and 0 warnings, with filters applied. Checked upstream source checksums match. Missing-man-page warnings are gone.
- The review ran with `--prebuilt`; its Mock-build warning does not mean the COPR build failed. The installed-package section says the packages were not installed despite the passing checklist label; that section is not runtime evidence.
- Installed Fedora 44 RPM `yazi-26.9.1-1.fc44.x86_64` passes `rpm -V`. Both `yazi --version` and `ya --version` report `26.9.1` and commit `8dd895c695a5950330c2623eb43debf323b60654`.
- The installed RPM includes both manual pages, generated completions, syntax sources, and dependency/syntax license files. Requirements include `file`, system Lua 5.4, and Oniguruma; bundled-crate provides, file list, and license-file list were inspected. Installed lint has no Yazi warnings (`rpmlint -i herdr yazi`: 0 errors, 1 Herdr warning, 7 filtered).
- Yazi starts and quits with `q` successfully in a 100x24 pseudo-terminal with a temporary isolated home/config/cache/state directory. A subsequent Fedora 44 installed-RPM PTY check listed a temporary fixture, entered a subdirectory with `j`/Enter, returned with Escape, and quit with `q` (terminal output included the fixture). These are navigation/startup checks only, not evidence for syntax highlighting, previews, or the currently building RPM. A non-terminal invocation failed with an ioctl error; a PTY without dimensions also failed, so terminal dimensions must be supplied for automated TUI checks.
- Latest Rawhide builder log: [build 11168077](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11168077-yazi/builder-live.log.gz). Cargo's optimized package build took 62m31s; `%check` then took 12m46s while discovering zero tests. This is a long clean compile of the large optimized Rust workspace, which includes a native jemalloc build. Replacing the empty test run with inexpensive version smoke checks avoids its redundant test-target compile; the main build duration should be remeasured after that change.
- `scripts/validate.py` passes for all three packages; 19 Python tests pass. Earlier local `%check` evidence reported zero upstream tests, so it should not be interpreted as functional coverage.

## Outstanding work

- Follow-up COPR check: build [11170142](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11170142/) was still running at the time of the check; review its artifacts when complete. Fedora dist-git returned 404 for `rpms/yazi`, and the Fedora Bugzilla Package Review query returned zero Yazi matches. The public Fedora account profile alone does not establish packager-group membership or sponsorship status; maintainer confirmation remains necessary.

- [x] Added explicit `gcc` BuildRequires for native C compilation in bundled dependencies (including jemalloc); no C++ sources are built for this package. Rebuild the SRPM and binary RPM and refresh review evidence before filing.
- [x] Replaced the no-coverage `%cargo_test` with executable version smoke checks in `%check`: the latest Rawhide log shows the upstream harness discovers zero tests for either target and spent 12m46 compiling test targets that execute zero tests.
- Reconcile licensecheck findings (24,509 unknown-license files) with the source-level audit and linked-license report. Scanner counts alone are not license violations or legal approval. The audit flags retained syntax directories lacking an obvious top-level license file for explicit source-pin/notice review; this is triage, not a finding that those works are unlicensed.
- Review source-bundle provenance/regeneration notes in `../README.md`; local generated archives intentionally do not have download URLs.
- Assess the documentation/data-size flags (789,451 documentation bytes and 1,054,720 bytes in `/usr/share`) before deciding whether a subpackage is useful.
- Independently inspect all binary subpackages and debug artifacts, verify build/test networking constraints, and test interactive previews, syntax highlighting, navigation, and optional integrations in clean Fedora environments. A successful x86_64 build does not validate other architectures.
- File the Fedora review request only after the manual review checks are complete; add its URL/status here.

Do not reuse `26.9.1-1` for changes to installed files or dependencies: it is now published and installed. COPR success is not official Fedora Rawhide inclusion.
