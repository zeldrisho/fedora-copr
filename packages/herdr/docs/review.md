# Herdr Fedora package review preparation

This is a maintainer preparation record, not an official Fedora review or approval. It is **not ready to file**: the complete source/license audit, a build of the corrected `0.9.5-3` artifacts, and final installed-package and account checks remain outstanding. Do not present this record as a completed review request until the blockers below are resolved.

## Package and artifact identity

- Package: `herdr` (`packages/herdr/herdr.spec`)
- Current spec NVR: `herdr-0.9.5-3` (not yet binary-built or published)
- Upstream: <https://github.com/herdrdev/herdr>, tag `v0.9.5`
- Upstream archive SHA-256: `a2486b09a8153630f6a19e72606ba1c961a6194bce13c09cba67ccce5e4252de`
- Cargo vendor archive SHA-256: `b131b52f4d794ecc34abdababe76f3324a1f20b7c5657ef4bf5fb75fde695f93`
- Submitted `herdr-0.9.5-3.fc44.src.rpm` SHA-256: `bf9ec248849168c32bb7a3c620ed11be362321c7132720be1a54a043e7a16257` (local retained artifact: `/tmp/herdr-final-srpm/herdr-0.9.5-3.fc44.src.rpm`)
- Zig source cache archive SHA-256: `8e51c25894ec2b41ddff67c01d5831fc4e5689c1264cd4f3449e2148ad52f8f0` (verified against `docs/checksums.sha256`)
- The two local dependency archives are deliberate source inputs without individual upstream URLs. Their provenance and regeneration procedure are documented in `../README.md` and `audit.md`.

`0.9.5-2` was built in COPR build 11170844. The spec now declares x86_64 only. The license correction is non-user-facing and does not itself warrant a Release bump. Release is `3` solely to avoid reusing the already-published `0.9.5-2` NVR for a different RPM payload. A matching `0.9.5-3` SRPM was built locally and submitted to COPR build [11171377](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11171377/) for Rawhide with network disabled. Await its result before relying on the corrected payload.

## Evidence gathered

- COPR build [11170844](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11170844/) succeeded on Rawhide x86_64 in the reported 52 minutes. Its build task records `enable_net: false`; the build log shows unit tests completing and the version/completion smoke checks passing. This supports offline build/test behavior for the submitted `0.9.5-2` SRPM. It does not cover Fedora 44/45, and it does not validate the corrected `0.9.5-3` spec.
- The build's fedora-review was invoked with `--prebuilt`; it is not an independent mock rebuild or installed-package test. The report's installation checks are invalid: its own attachment reports that neither `herdr` nor `herdr-debuginfo` was installed.
- Downloaded the build's SRPM and three binary RPMs to `/tmp/herdr-11170844/fedora-rawhide-x86_64/`. Inspected NVR, License metadata, payload paths, and subpackage identities. Main RPM includes the executable, manual, README, and three completions; debuginfo and debugsource RPMs were also produced.
- Re-ran rpmlint on the current spec and all four downloaded RPMs plus the SRPM: 0 errors; two unique warnings repeated for spec/SRPM, both local Source1/Source2 URLs. The old fedora-review attachment additionally reports 18,419 unknown files; this remains an unresolved license-review signal, not a license conclusion.
- `scripts/validate.py` passes after the `0.9.5-3` license-file fix. A retained SRPM was generated at `/tmp/herdr-final-srpm/herdr-0.9.5-3.fc44.src.rpm`; it was submitted to COPR as build 11171377 for a network-disabled Rawhide binary build. Await build completion, then inspect all outputs and lint them.
- COPR build [11170135](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11170135/) succeeded, but it predates the current local Zig cache/license changes. Its generated review used `--prebuilt`; it is not a clean Mock build, installed-RPM check, or evidence for the current spec.
- Earlier COPR builds [11168076](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11168076/) passed for Fedora 44, Fedora 45, and Rawhide on x86_64, but likewise do not validate the current contents.
- Fedora 44 testing of installed `0.9.5-1` confirmed `rpm -V`, version output, Bash completion, server start/stop, workspace CRUD, and several pane operations. This is useful historical evidence only. Interactive detach/reattach was not verified; it does not test the current SRPM.
- Review of the `0.9.5-2` RPM found a packaging defect: `%license LICENSE` and `%license vendor/libghostty-vt/LICENSE` mapped two different texts to the same `/usr/share/licenses/herdr/LICENSE` path. The resulting RPM retained Ghostty's MIT text and lost Herdr's upstream Apache-2.0 text. The `0.9.5-3` spec now stages Ghostty's notice as `LICENSE.ghostty-vt` so both are installed. This corrected RPM has not yet been built or inspected.

## Blockers before filing

- [ ] Complete the source-level license audit for all content in the upstream, Cargo vendor, and Zig archives. Specifically assess the `Pixels` CC0 data and zlib source/contrib licensing, enabled Ghostty features and linked code, native bundle declarations, and required license texts. Scanner output alone is not a license determination. Record evidence and a justified SPDX expression in `audit.md`.
- [ ] Build `0.9.5-3` and inspect the final binary RPM: License metadata, distinct upstream/Ghostty license files, linked/bundled native components and Provides, and every subpackage including debuginfo/debugsource.
- [ ] Obtain matching clean builds for all intended Fedora chroots. Rawhide `0.9.5-2` demonstrated a network-disabled successful build/test; the submitted `0.9.5-3` Rawhide build is pending.
- [x] Architecture scope is x86_64 only. The spec no longer claims aarch64 support; no aarch64 build is required for this review.
- [ ] Run rpmlint on the final spec, SRPM, and every binary RPM; retain the complete, unmodified output and explain intentional warnings. For `0.9.5-2`, current local rerun found 0 errors and only the two expected local-source URL warnings; this is not evidence for `0.9.5-3`.
- [ ] Install the final RPM in a clean Fedora environment. Recheck integrity, version, generated shell completions, server/workspace/pane behavior, and interactive detach/reattach. Record the environment and limitations.
- [ ] Refresh the duplicate/retired package and open-review search immediately before filing; the prior checks are time-sensitive. Confirm Fedora account/Bugzilla linkage and whether sponsorship is needed.
- [ ] Publish the exact matching spec and SRPM at public, directly downloadable HTTPS URLs and fill in those URLs and final build-log links below.

## Bugzilla draft (complete only after blockers clear)

**Summary:** `Review Request: herdr - terminal workspace manager for AI coding agents`

**Description:**

> This is a review request for Herdr, a terminal workspace manager for coding agents. The package builds the upstream v0.9.5 source with Fedora Rust and Zig toolchains and installs the executable, manual page, and Bash/Zsh/Fish completions.
>
> Spec: **[public HTTPS URL to exact submitted spec]**
>
> SRPM: **[public HTTPS URL to exact submitted SRPM]**
>
> Build logs/results: **[public URL(s)]**
>
> License/source audit and package test notes: **[public URL or concise summary]**
>
> **[If sponsorship is needed: I am seeking a Fedora packager sponsor.]**

In Bugzilla, set `FE-NEEDSPONSOR` in **Blocks** when applicable (not Depends On). Submit with the Fedora Package Review product/component and use the account linked to the Fedora account. This draft is not an assertion of review approval; only the reviewer can grant it.
