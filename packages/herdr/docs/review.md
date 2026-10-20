# Herdr Fedora package review preparation

Maintainer tracking record, not an official Fedora review or approval. Fedora Package Review request [2555980](https://bugzilla.redhat.com/show_bug.cgi?id=2555980) is filed and currently NEW. It blocks on sponsor tracker 177841. The current candidate `herdr-0.9.5-4` succeeded across all configured x86_64 chroots.

## Package and current candidate

- Spec: `packages/herdr/herdr.spec`
- Upstream: <https://github.com/herdrdev/herdr>, tag `v0.9.5`
- Current NVR: `herdr-0.9.5-4`
- Retained SRPM: `$HOME/rpmbuild/SRPMS/herdr-0.9.5-4.fc44.src.rpm`
- SRPM SHA-256: `9a3ab3387adb66fac135c6324e6e65084494e0ae3c364a00e95592a61e39df44`
- Candidate COPR build: [11171729](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11171729/)
- Result: succeeded on Fedora 44, Fedora 45, and Rawhide, x86_64.
- Rawhide Fedora Review report: [review.txt](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11171729-herdr/fedora-review/review.txt)
- Rawhide builder log: [builder-live.log.gz](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11171729-herdr/builder-live.log.gz)
- Retained Rawhide report, logs, and RPMs: `dist/review/herdr/fedora-rawhide-x86_64/` (ignored by Git).
- COPR elapsed time: approximately 52 minutes, consistent with the COPR task timestamps.

On 2026-10-19, `scripts/validate.py`, all 19 repository unit tests, and both package source checksum manifests passed. SRPM validation reported no rpmlint errors or warnings. The Rawhide Fedora Review attachment reports two expected local-source `invalid-url` warnings for Source1/Source2 and zero rpmlint errors. The binary package itself and debuginfo had no rpmlint errors/warnings in that report. COPR confirms the three target builds succeeded.

## Bugzilla request and Fedora Review findings

- Bug [2555980](https://bugzilla.redhat.com/show_bug.cgi?id=2555980): `Review Request: herdr - Terminal workspace manager for AI coding agents`.
- Filed 2026-10-20 by Fedora account `zeldrisho`; status NEW, component Package Review, blocks sponsor tracker [177841](https://bugzilla.redhat.com/show_bug.cgi?id=177841).

The automated Fedora Review report runs with `--prebuilt`; its `Reviewer should test that the package builds in mock` item remains for the human reviewer, but the actual COPR binary build succeeded independently in all three configured chroots. The Rawhide builder log records `enable_net: False`, 3,657 tests passed (12 ignored), and the version/completion smoke checks. The report's installed-package checks are not runtime evidence: its attachment says neither `herdr` nor `herdr-debuginfo` was installed. RPM inspection confirms the Release 4 main package has distinct `/usr/share/licenses/herdr/LICENSE` and `LICENSE.ghostty-vt` entries, along with the dependency and Zig license files. The binary RPM and debuginfo rpmlint checks show zero errors/warnings; source/spec check reports two local archive `invalid-url` warnings.

Historical build [11171377](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11171377/) covered Rawhide only. It was submitted for Rawhide only, not because Fedora 44/45 failed or were disabled. Fedora 44 testing of `0.9.5-1` is historical and does not establish current runtime behavior.

- [ ] Complete the source-level license audit for the upstream, Cargo vendor, and Zig archives. Specifically assess the `Pixels` CC0 data, zlib source/contrib licensing, enabled Ghostty features and linked code, native bundle declarations, and required license texts. Record evidence and justify the SPDX expression in `audit.md`; scanner output alone is insufficient.
- [ ] Install the final RPM in a clean Fedora environment. Check integrity, version, shell completions, server/workspace/pane behavior, and interactive detach/reattach; record environment and follow up in Bugzilla.
- [ ] Monitor sponsorship/review feedback and update this record as checks are completed.
