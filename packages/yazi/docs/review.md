# Fedora package review notes: yazi

Maintainer tracking record, not Fedora review approval. Fedora Package Review request [2555981](https://bugzilla.redhat.com/show_bug.cgi?id=2555981) is filed and currently NEW. It blocks on sponsor tracker 177841. Current candidate `yazi-26.9.1-4` succeeded across all configured x86_64 chroots.

## Request and current candidate

- Summary: `Review Request: yazi - Blazing fast terminal file manager`
- Upstream: [Yazi v26.9.1](https://github.com/sxyazi/yazi/releases/tag/v26.9.1).
- Bug [2555981](https://bugzilla.redhat.com/show_bug.cgi?id=2555981): `Review Request: yazi - Blazing fast terminal file manager`; filed 2026-10-20 by Fedora account `zeldrisho`, status NEW, blocks sponsor tracker [177841](https://bugzilla.redhat.com/show_bug.cgi?id=177841).
- Retained SRPM: `$HOME/rpmbuild/SRPMS/yazi-26.9.1-4.fc44.src.rpm`
- SRPM SHA-256: `adcacab44e2cab20619ea600228e15ff695ab7cc728358d295eb53c44859f77f`
- Candidate COPR build: [11171728](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11171728/)
- Result: succeeded on Fedora 44, Fedora 45, and Rawhide, x86_64.
- Rawhide Fedora Review report: [review.txt](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11171728-yazi/fedora-review/review.txt)
- Rawhide builder log: [builder-live.log.gz](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11171728-yazi/builder-live.log.gz)
- Retained Rawhide report, logs, and RPMs: `dist/review/yazi/fedora-rawhide-x86_64/` (ignored by Git).
- COPR elapsed time: approximately 49 minutes, consistent with COPR task timestamps.

Repository validation, all 19 unit tests, and source checksum checks passed on 2026-10-19. SRPM validation reported no rpmlint errors or warnings for Yazi's spec/SRPM. The Rawhide Fedora Review attachment reports two expected local-source `invalid-url` warnings and zero rpmlint errors; binary RPM/debuginfo checks have zero rpmlint errors/warnings. COPR confirms successful builds in all three configured chroots.

## Fedora Review findings and remaining checks

The automated Fedora Review report runs with `--prebuilt`; its `Reviewer should test that the package builds in mock` item remains for the human reviewer, while COPR independently confirms successful binary builds in Fedora 44, Fedora 45, and Rawhide. The Rawhide builder log records `enable_net: False` and both executable version checks passing. The report's installed-package checks are not runtime evidence: its attachment says neither Yazi nor debuginfo was installed. RPM inspection confirms Release 4 License metadata and the expected main package license payload. The main RPM/SRPM lint report has two expected local-archive `invalid-url` warnings and zero errors; debuginfo has zero warnings/errors. The report flags the syntax-source documentation size/placement for maintainer/reviewer assessment.

Historical build [11171273](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11171273/) covered Release 3, not the current candidate.

- [ ] Obtain Fedora Legal guidance on the CC0-1.0 eligibility question for linked `notify` 8.2.0 and ensure the open question is clearly disclosed in Bugzilla. See [audit.md](audit.md) and [legal-inquiry.md](legal-inquiry.md).
- [ ] Resolve the syntax-source documentation archive's placement/rationale and the spec's documentation-install method; rebuild if a packaging change is needed.
- [ ] In a clean Fedora installation with isolated state and a sized PTY, test navigation, retained syntax highlighting, excluded-grammar fallback, previews, and optional integrations. Record tested environment and limits.
- [ ] Follow up on the unresolved CC0 eligibility question, documentation placement, and installed runtime/syntax tests in Bugzilla; update the review record as these are resolved.

Release 4 is published and must not be reused for different contents. COPR success is not Fedora review approval or official Fedora inclusion.
