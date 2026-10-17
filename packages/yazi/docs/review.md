# Fedora package review notes: yazi

This is a preparation record, not evidence of Fedora review approval. The package has not yet been submitted.

## Request

- Review bug: Not filed.
- Fedora account: Not recorded; confirm the maintainer's account and sponsorship needs before filing.
- Sponsorship requested: Not determined.
- Package summary: Terminal file manager written in Rust.
- Upstream: [Yazi v26.9.1](https://github.com/sxyazi/yazi/releases/tag/v26.9.1).
- Duplicate check: The maintainer confirmed there is no existing Fedora Yazi package or review.

## Artifacts and build evidence

- Spec: `packages/yazi/yazi.spec` (no public URL yet).
- SRPM and Fedora 44 binary RPM: Built locally; `%check` completed (the upstream test harness reports zero tests). The installed device was upgraded to 26.9.1 and both executables report the expected version and pinned commit. The RPM predates the newly added man pages; rebuild to include them.
- Fedora 45 and Rawhide clean-chroot build logs: Pending; Fedora 44 clean-chroot build evidence is also pending.
- `scripts/validate.py`: Passed. Direct binary rpmlint reports missing-man-page warnings for `yazi` and `ya`; repository validation filters them.

## Outstanding work

- Rebuild the binary RPM to include `yazi(1)` and `ya(1)`, then confirm the missing-man-page rpmlint warnings are gone.
- Build in Fedora 44, Fedora 45, and Rawhide clean chroots.
- Inspect final RPM dependencies, bundled-crate provides, installed files, and license files; retain the clean-chroot logs.
- Retain clean-chroot build evidence, then file the Fedora review request and add its URL/status here.
