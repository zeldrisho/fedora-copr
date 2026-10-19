# Fedora package review notes: yazi

Preparation record, not Fedora review approval. Review request not filed. Current package is Yazi 26.9.1 Release 3; review evidence below distinguishes the built Release 2 RPM from the unbuilt/unverified Release 3 state recorded during the last update (2026-10-19). Recheck COPR and Bugzilla before relying on status.

## Request and filing

- Summary: `Review Request: yazi - Blazing fast terminal file manager`
- Upstream: [Yazi v26.9.1](https://github.com/sxyazi/yazi/releases/tag/v26.9.1).
- Bug: not filed. Fedora account, packager membership, Bugzilla association, and sponsorship status must be confirmed.
- Duplicate search previously found no `rpms/yazi` dist-git repository and no Bugzilla Package Review API matches. Recheck immediately before filing.
- Publish immutable public HTTPS URLs for the exact matching Release 3 spec and SRPM. The local SRPM path is not a public review URL.
- If proceeding before the CC0 question is resolved, explicitly disclose it; see [legal-inquiry.md](legal-inquiry.md). That inquiry is a draft, not a Fedora determination.

## Build evidence

| Artifact | Evidence | Limits |
| --- | --- | --- |
| Release 2 (`26.9.1-2.fc46`) | COPR [11170512](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11170512/) succeeded on Rawhide x86_64 with network disabled. | Does not validate Release 3 or other chroots/architectures. |
| Release 2 review report | [Fedora Review output](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11170512-yazi/fedora-review/review.txt); run with `--prebuilt`. | No packages installed; its runtime/install markers are not runtime evidence. Rpmlint had zero errors and two local-archive `invalid-url` warnings. |
| Release 3 (`26.9.1-3`) | Repository validation and SRPM generation passed; retained SRPM was recorded at `$HOME/rpmbuild/SRPMS/yazi-26.9.1-3.fc44.src.rpm`. | COPR build 11171273 was recorded as submitted/running, with no result recorded. Verify its current status and obtain matching build evidence. |

The Release 2 license scanner reported 24,495 unknown/generated files; this is scanner output, not a licensing conclusion. Its 26 Cargo SPDX expressions matched that release's spec expression, which likewise does not establish eligibility. Release 3 removes NCSA and CC-BY-SA-3.0 based on source/linkage review; recheck the final build's license summary. The CC0-1.0 use in linked `notify` 8.2.0 remains an unresolved eligibility question. See [audit.md](audit.md) and [legal-inquiry.md](legal-inquiry.md).

## Remaining checks

- Obtain a Fedora Legal determination or keep the CC0 question clearly disclosed in any review request.
- Verify current COPR status, exact Release 3 artifacts, build logs, offline behavior, and lint results; do not transfer Release 2 evidence to Release 3.
- Inspect matching main, debuginfo, and debugsource RPMs: metadata, dependencies, bundled provides, files, and license payload.
- Resolve the large syntax-source documentation archive's placement/rationale and the spec's documentation-install method; then build and inspect any changed candidate.
- In a clean Fedora installation with isolated state and a sized PTY, test navigation, retained syntax highlighting, excluded-grammar fallback, previews, and optional integrations. Existing historical PTY checks cover only basic startup/navigation.
- Confirm account/sponsorship and duplicate-search results; publish matching immutable spec/SRPM URLs before filing.

Release 2 is published and must not be reused for different contents. COPR success is not Fedora review approval or official Fedora inclusion.
