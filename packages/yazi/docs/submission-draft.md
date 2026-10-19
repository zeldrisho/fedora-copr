# Fedora Bugzilla package review draft: yazi

**Status:** Draft for maintainer review. Not filed. The Release 3 SRPM is local only; publish the exact artifact at a public, directly downloadable HTTPS URL before filing.

## Suggested Bugzilla short description

Review Request: yazi - Blazing fast terminal file manager

## Suggested description

Review Request: yazi - Blazing fast terminal file manager

Yazi is a terminal file manager written in Rust, based on non-blocking async I/O.

Upstream: https://github.com/sxyazi/yazi/releases/tag/v26.9.1

Spec URL: [publish the exact Release 3 spec at an immutable, public HTTPS URL]

SRPM URL: [publish yazi-26.9.1-3.fc44.src.rpm at a public, directly downloadable HTTPS URL]

Build evidence: Release 2 (26.9.1-2) previously built on COPR for Fedora Rawhide x86_64. Release 3 (26.9.1-3) passed repository validation and was built as an SRPM. COPR build 11171273 was submitted from that SRPM and is currently running; no Release 3 chroot result is available yet. Do not present the Release 2 build as evidence for Release 3.

Licensing disclosure: The binary links `notify` 8.2.0, whose Cargo metadata and license file identify CC0-1.0. Fedora's allowed-license policy contains a grandfathering rule for certain existing package uses before 2022-08-01. Fedora's existing `rust-notify` package does not, by itself, establish that this new Yazi package qualifies. The maintainer requests reviewer guidance and, if needed, referral to Fedora Legal. The focused inquiry is drafted but has not been submitted. No Fedora Legal determination, upstream relicense, or replacement watcher backend is currently available. Release 3's spec includes CC0-1.0 in the `License:` expression and does not claim that the grandfathering exception applies to Yazi.

The matching SRPM contains the spec and source archives. The package audit and review notes are maintained at the upstream packaging repository; they are not substitutes for the artifacts linked above.

## Before filing

- Replace the Spec and SRPM placeholders with public, immutable, directly downloadable URLs for matching Release 3 artifacts.
- Confirm Fedora account, packager status, Bugzilla account association, and whether sponsorship is requested. If sponsorship is needed, set `FE-NEEDSPONSOR` in the Bugzilla `Blocks` field per Fedora's submission guide.
- Recheck duplicate/open/retired-package status and record results in `review.md`.
- Check COPR build 11171273 and accurately report its final per-chroot results; do not imply that COPR success resolves licensing eligibility.
- Confirm that submitting the review with the CC0 question outstanding is intentional and keep the issue plainly disclosed.
