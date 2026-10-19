# actionlint Fedora review record

**Current review:** [Bug 2554709](https://bugzilla.redhat.com/show_bug.cgi?id=2554709), identified by the contributor as the replacement review for actionlint 1.7.12-2. The contributor reported closing [Bug 2554537](https://bugzilla.redhat.com/show_bug.cgi?id=2554537) as a duplicate. Current Bugzilla status, replacement sponsorship field, and artifact contents have not been independently verified.

## Current artifacts

- Spec: https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/srpm-builds/11165663/actionlint.spec
- SRPM: https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/srpm-builds/11165663/actionlint-1.7.12-2.src.rpm

These are contributor-provided URLs. Historical build and audit evidence below is for **1.7.12-1**, not these replacement artifacts; obtain matching build evidence before presenting the current package as built or tested. See [audit.md](audit.md) for source, license, and installation audit scope.

## Historical evidence (1.7.12-1 only)

COPR build [11162667](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11162667-actionlint/builder-live.log.gz) built 1.7.12-1 on Rawhide; `%check` and Go Vendor Tools license-expression verification passed. The build's Fedora Review report is [here](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11162667-actionlint/fedora-review/review.txt). It used `--prebuilt`, leaves manual checks open, and does not establish reviewer approval or installed-package testing. Its Mock-test marker is failed despite the separate successful COPR builder log.

Local Fedora 44 preparation for 1.7.12-1 passed repository validation, 13 helper tests, host build, smoke checks, and rpmlint (0 errors; two `invalid-url Source1` warnings). A private-root install smoke test used `--nodeps --noscripts`; it was not a dependency-resolving installation. The historical audit reviewed the main and module license texts, notices, and installed license payload. Full details and limits are in [audit.md](audit.md).

## Before relying on the current review

- Verify Bugzilla status and the replacement review's sponsorship field.
- Verify the current spec and SRPM URLs identify matching 1.7.12-2 artifacts.
- Obtain matching clean build, lint, and runtime evidence; do not transfer 1.7.12-1 results to 1.7.12-2.
- Confirm account and sponsorship status with the contributor.
