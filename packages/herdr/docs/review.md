# Herdr Fedora package review preparation

This is a maintainer preparation record, not an official Fedora review or approval. It is **not yet ready to file**: the final source/license audit and matching clean build/RPM evidence are outstanding. Keep this status current; do not paste this record as a completed review request until the blockers below are resolved.

## Package and artifact identity

- Package: `herdr` (`packages/herdr/herdr.spec`)
- Current spec NVR: `herdr-0.9.5-2`
- Upstream: <https://github.com/herdrdev/herdr>, tag `v0.9.5`
- Upstream archive SHA-256: `a2486b09a8153630f6a19e72606ba1c961a6194bce13c09cba67ccce5e4252de`
- Cargo vendor archive SHA-256: `b131b52f4d794ecc34abdababe76f3324a1f20b7c5657ef4bf5fb75fde695f93`
- Zig source cache archive SHA-256: `9714eeb9b258e276e4b991d349a64641031b53f95ade7aa188cf06ccaaa8af1a`
- The two local dependency archives are deliberate source inputs without individual upstream URLs. Their provenance and regeneration procedure are documented in `../README.md` and `audit.md`.

**Do not submit `0.9.5-2` as a new or changed SRPM if those contents have already been published.** The spec now declares x86_64 only, matching the architecture with recorded builds. No Release bump was made for this review-preparation change. Before publishing, ensure the submitted NVR does not reuse a published build with different package contents.

## Evidence gathered

- `scripts/validate.py` passes for all three repository packages (run during this preparation). It validates SRPM generation and spec lint, not a current Herdr binary build or runtime behavior.
- COPR build [11170135](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11170135/) succeeded, but it predates the current local Zig cache/license changes. Its generated review used `--prebuilt`; it is not a clean Mock build, installed-RPM check, or evidence for the current spec.
- Earlier COPR builds [11168076](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11168076/) passed for Fedora 44, Fedora 45, and Rawhide on x86_64, but likewise do not validate the current contents.
- Fedora 44 testing of installed `0.9.5-1` confirmed `rpm -V`, version output, Bash completion, server start/stop, workspace CRUD, and several pane operations. This is useful historical evidence only. Interactive detach/reattach was not verified; it does not test the current SRPM.
- The old `fedora-review` output reports 0 rpmlint errors but includes warnings for missing man page (fixed in `0.9.5-2`) and local Source1/Source2 URLs, plus a large unknown-license scan count. It is stale for the current sources. Rpmlint and fedora-review must be rerun on the final artifacts.

## Blockers before filing

- [ ] Complete the source-level license audit for all content in the upstream, Cargo vendor, and Zig archives. Specifically assess the `Pixels` CC0 data and zlib source/contrib licensing, the enabled Ghostty features and linked code, and whether any included permissively licensed component's license text must be installed. Scanner output alone is not a license determination. Record file/source evidence and an appropriate SPDX expression in `audit.md`.
- [ ] Build the final spec and inspect its actual binary RPM: `License:` metadata, installed `%license` files, linked/bundled native components and Provides, and all subpackages including debuginfo/debugsource.
- [ ] Obtain a clean Rawhide build of the final matching SRPM; demonstrate network-disabled build/test phases. The current saved build/review evidence is not sufficient.
- [x] Architecture scope is x86_64 only. The spec no longer claims aarch64 support; no aarch64 build is required for this review.
- [ ] Run rpmlint on the final spec, SRPM, and every binary RPM; retain the complete, unmodified output and explain intentional warnings.
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
