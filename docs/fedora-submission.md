# Submit actionlint to Fedora

This is the submission checklist for Fedora contributor **zeldrisho**. The contributor submitted [Bug 2554537](https://bugzilla.redhat.com/show_bug.cgi?id=2554537) on 2026-10-17. The contributor confirmed `FE-NEEDSPONSOR` (tracker bug 177841) in its Blocks field at 04:32 UTC. Track reviewer feedback; packager access has not been established. See the supplied upstream copies of [Joining the Package Maintainers](upstream/joining.md) and [Package Review Process](upstream/review-progress.md), and the [packaging references](upstream/README.md).

## 1. Confirm accounts and avoid duplicate submissions

- Sign in to [Fedora Accounts](https://accounts.fedoraproject.org/) and check whether your profile lists `packager` membership. The public profile redirected to login during preparation, so membership is **unconfirmed**. A group page's invitation to contact a sponsor is not proof of membership or non-membership.
- Check that your contributor agreement is signed and your public SSH key is configured. Never put private keys or tokens in this repository.
- Fedora Accounts and [Red Hat Bugzilla](https://bugzilla.redhat.com/) both use `zeldrisho@proton.me`, as confirmed by the contributor. Git author email is separate: this repository inherits the global GitHub noreply identity; matching it to the account email is not an established requirement in the guidance checked.
- Search [Fedora packages](https://packages.fedoraproject.org/), [dist-git](https://src.fedoraproject.org/rpms/actionlint), and [package reviews](https://fedoraproject.org/PackageReviewStatus/) for `actionlint`, including retired packages and open reviews. A missing package webpage or empty web search is not sufficient evidence that the name is available. The automated dist-git check encountered an anti-bot challenge; the contributor subsequently confirmed no existing actionlint package or review.

If the package already exists, coordinate with its maintainers instead of filing a duplicate. An existing review or retired package may require a different process.

## 2. Prepare and validate artifacts

From the repository root:

```sh
make validate
python3 -m unittest discover -s tests -v
make srpm PACKAGE=actionlint
```

The SRPM is written under `dist/srpm/`. Keep the matching spec, source checksums, logs, and SRPM together. Rebuild and refresh the review artifacts after any packaging change; do not reuse a published Version-Release for different package contents.

### Clean-chroot build (existing COPR evidence verified)

[COPR build 11162667](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11162667-actionlint/builder-live.log.gz) passed in Rawhide's x86_64 Mock chroot, including `%check` and license verification. Its published SRPM inputs match the current package; the [review draft](actionlint-review.md) records the artifact URLs and report limitations. Reuse this evidence rather than requiring a duplicate local Mock build.

For future packaging changes, obtain matching clean-chroot evidence from COPR or a local Mock build. Mock is not installed in the preparation environment. To build locally, install it and configure access using Fedora's current Mock documentation, then select an available Fedora Rawhide or target-release configuration. For example, on a configured x86_64 host:

```sh
mkdir -p dist/review/actionlint
mock -r fedora-rawhide-x86_64 \
  --resultdir "$PWD/dist/review/actionlint" \
  --rebuild dist/srpm/actionlint-*.src.rpm
rpmlint packages/actionlint/actionlint.spec \
  dist/review/actionlint/*.rpm
```

Use a result directory containing only artifacts from this build. Keep the full Mock logs and unmodified lint output. Confirm the license report, `bundled(golang(...))` provides, installed license files (including `vendor/modules.txt`), and runtime behavior. A successful host rebuild does **not** replace this isolated build or prove offline operation. See [toolchain commands](toolchain.md) for RPM inspection and [package notes](../packages/actionlint/README.md) for vendor regeneration and test exclusions.

The [packager source and installation audit](actionlint-audit.md) records the license-text review, byte-identical vendor regeneration, installed license/provides checks, and a limited installed-RPM smoke test. A full dependency-resolving installation test remains outside that smoke test's scope. Before uploading sources to Fedora's lookaside cache, recheck licensing if sources change and address any license-report errors; independent reviewer evaluation is still required. The automated expression check alone does not establish license compliance.

## 3. Publish and open the review

1. Publish the exact matching spec and SRPM at public, directly downloadable HTTPS URLs. COPR artifacts can be used if they match the submitted spec. Prefer immutable/versioned URLs so later edits do not silently change review inputs.
2. Fill the placeholders in the [actionlint review draft](actionlint-review.md), including artifact and build-log URLs. Complete the pending checks before presenting the package as ready.
3. Open a [Fedora Package Review request](https://bugzilla.redhat.com/bugzilla/enter_bug.cgi?product=Fedora&format=fedora-review) using the Bugzilla account linked by email to your Fedora account.
4. Put **FE-NEEDSPONSOR in the Blocks field**, not Depends On, as requested by the contributor for this submission. Review can proceed before sponsorship.
5. Introduce yourself on the development mailing list with the review link and mention that you need sponsorship if applicable. Follow the onboarding guide for the introduction.
6. Respond to feedback and post updated spec/SRPM URLs after fixes. Only the reviewer sets approval (`fedora-review +`). If approval is complete but sponsorship is still needed, the supplied review process directs you to [packager sponsors](https://forge.fedoraproject.org/packaging/sponsors/issues).

## 4. After approval and sponsorship

Once the review is approved and the necessary account access is available:

- Configure a Fedora Forge token locally as described in the review-process reference; do not include it in commands committed here.
- Request dist-git with `fedpkg request-repo actionlint <review-bug-number>`.
- After repository creation, clone it and import the approved SRPM with `fedpkg` following Fedora's linked new-package instructions. Upload source archives to the lookaside cache; keep the spec and `go-vendor-tools.toml` in dist-git.
- Consider `%autorelease` and `%autochangelog` during migration, preserving upgrade ordering from published COPR builds. Do not change this monorepo's release mechanism merely to prepare the review.
- Build Rawhide with `fedpkg build`. Request supported release branches as needed and use Bodhi for release updates where required.
- Close the review as `NEXTRELEASE` when appropriate, and enable release monitoring and Koschei where available.

Follow the current linked Fedora instructions when executing these account-dependent steps. The contributor has submitted the review ticket. No repository request, lookaside source upload, or official Fedora build has been performed by this preparation.
