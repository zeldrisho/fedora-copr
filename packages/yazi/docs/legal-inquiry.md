# Fedora Legal inquiry: CC0-1.0 in Yazi's `notify` dependency

**Status:** Draft; not submitted. A Fedora Legal determination remains pending; Yazi Release 3 has been submitted to COPR for a technical build, which does not decide license eligibility.

## Question

Does a new Fedora application package, Yazi, qualify to include and link `notify` 8.2.0 under `CC0-1.0` based on the existence of Fedora's `rust-notify` package since at least Fedora 35, or does the CC0 grandfathering rule apply only to the existing package and its subsequent upstream versions?

Please clarify whether the answer depends on how the crate is packaged (for example, a dependency on a Fedora-built `rust-notify` package versus vendoring/bundling the crate into Yazi), and what evidence or packaging changes Fedora requires for an acceptable Yazi package.

## Facts and evidence

- Yazi 26.9.1 is being prepared as a new Fedora package; it has not been submitted for Fedora review.
- Yazi's Cargo dependency graph includes `notify` 8.2.0, which is linked into the Yazi binary.
- The crate's Cargo metadata and its license file identify `CC0-1.0`.
- Fedora's [current allowed-license guidance](../../../docs/references.md#licensing) describes grandfathering for certain existing package uses of `CC0-1.0` code before 2022-08-01 and subsequent upstream versions. Verify the live policy; this summary does not establish that a new application package qualifies. It does not establish that a new application package may rely on an older Fedora package's grandfathered status.
- Fedora Packages currently lists `rust-notify+default-devel` 8.2.0-5 in Fedora 44, 45, and Rawhide. The page describes it as library source for packages that use the `notify` crate's default feature. This establishes current Fedora packaging of the same crate/version, but does not by itself establish the grandfathering start date or that a new Yazi binary qualifies for the exception. The package page is https://packages.fedoraproject.org/pkgs/rust-notify/rust-notify+default-devel/index.html.
- Yazi's spec is `packages/yazi/yazi.spec` (Version 26.9.1, Release 3). At the last recorded check, its SRPM had been submitted to COPR as build 11171273; verify current build status before relying on it. A technical build does not determine Fedora license eligibility. The spec's `License:` expression includes `CC0-1.0` based on the linked dependency summary.

## Requested determination

Please determine whether the proposed Yazi package is eligible under Fedora's CC0-1.0 policy as described, including whether the `rust-notify` package's history affects the answer. If it is not eligible, please advise whether consuming a Fedora-built `rust-notify` package changes the analysis, or whether Yazi must instead use relicensed or replacement code.

## References to attach or verify before sending

- Fedora's current allowed-license entry for `CC0-1.0`, especially its grandfathering language: https://docs.fedoraproject.org/en-US/legal/allowed-licenses/.
- `notify` 8.2.0 Cargo metadata and `LICENSE-CC0` from the exact vendored source used by Yazi.
- Fedora's current `rust-notify` package page: https://packages.fedoraproject.org/pkgs/rust-notify/rust-notify+default-devel/index.html.
- Fedora package history establishing when `rust-notify` first appeared, if relevant to the inquiry; the current package page alone does not establish that date.
- The current Yazi spec and relevant excerpts from `packages/yazi/docs/audit.md` and `packages/yazi/docs/review.md`.

Do not describe this draft as a Fedora determination or imply that the exception applies to Yazi unless Fedora Legal confirms it.
