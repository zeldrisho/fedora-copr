# Fedora package submission

Repository-specific checklist for submitting a package to the official Fedora repositories. Follow current Fedora policy and account procedures linked in [Fedora references](references.md). Keep package status and evidence in `packages/<name>/docs/review.md`; use the [review template](templates/review.md) as needed.

## Prepare

- Confirm the package is eligible, its name is available, and no active or retired package/review requires coordination. Search Fedora Packages, dist-git, and package reviews; record dated results and limitations in the package review record.
- Confirm Fedora account, packager-group, sponsorship, Bugzilla identity, contributor agreement, and SSH-key requirements using current Fedora onboarding guidance. Never store credentials here.
- Validate the repository and test suite:

  ```sh
  scripts/validate.py
  python3 -m unittest discover -s tests -v
  ```

- Build and retain the matching SRPM with `make srpm PACKAGE=herdr` (replace `herdr` with the package name). Check the exact spec, sources, checksums, and NVR. Do not reuse a published NVR for different RPM contents.
- Obtain clean-chroot build evidence using COPR or Mock. Follow `docs/toolchain.md` for build and RPM inspection commands. Record target, exact artifact identity, logs, lint results, and limitations.
- Review licensing against source contents and current Fedora policy; automated scans are supporting evidence, not a legal determination. Record the audit and unresolved questions.

## File and follow up

- Publish the exact matching spec and SRPM at public, directly downloadable HTTPS URLs; prefer immutable/versioned URLs. Include the SRPM URL in Bugzilla.
- Open a Fedora Package Review request and link build evidence. Set `FE-NEEDSPONSOR` in **Blocks** if sponsorship is needed. Follow current Fedora instructions for review feedback, sponsorship, repository request, source import, and builds.
- Record actual review status and follow-up in the package-specific review record. COPR publication is not Fedora review approval.
