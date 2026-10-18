# Fedora package submission

General checklist for submitting a package to the official Fedora repositories. Consult the [packaging guidelines](packaging-guidelines/README.md) and [package-maintainer guidance](package-maintainers/README.md). Keep package-specific submission status and evidence in `packages/<name>/docs/review.md`; use the [review template](templates/review.md) to prepare reviewer-facing material.

## 1. Confirm accounts and avoid duplicate submissions

- Sign in to [Fedora Accounts](https://accounts.fedoraproject.org/) and check whether your profile lists `packager` membership. The public profile redirected to login during preparation, so membership is **unconfirmed**. A group page's invitation to contact a sponsor is not proof of membership or non-membership.
- Check that your contributor agreement is signed and your public SSH key is configured. Never put private keys or tokens in this repository.
- Confirm that the Fedora account and [Red Hat Bugzilla](https://bugzilla.redhat.com/) identities are correctly associated. Keep private keys and tokens out of the repository.
- Search [Fedora packages](https://packages.fedoraproject.org/), [dist-git](https://src.fedoraproject.org/rpms/<package>), and [package reviews](https://fedoraproject.org/PackageReviewStatus/) for the package, including retired packages and open reviews. A missing package webpage or empty web search is not sufficient evidence that the name is available. Record the search results and any limitations in the package-specific review record.

If the package already exists, coordinate with its maintainers instead of filing a duplicate. An existing review or retired package may require a different process. Replace the example package name in the search links below with the package under review.

## 2. Prepare and validate artifacts

From the repository root:

```sh
make validate
python3 -m unittest discover -s tests -v
make srpm PACKAGE=actionlint
```

The SRPM is written under `dist/srpm/`. Keep the matching spec, source checksums, logs, and SRPM together. Rebuild and refresh the review artifacts after any packaging change; do not reuse a published Version-Release for different package contents.

### Clean-chroot build

Obtain matching clean-chroot evidence from COPR or a local Mock build. Mock is not installed in every preparation environment. To build locally, install it and configure access using Fedora's current Mock documentation, then select an available Fedora Rawhide or target-release configuration. For example, on a configured x86_64 host:

```sh
package=<name>
mkdir -p dist/review
resultdir=$(mktemp -d "dist/review/$package.XXXXXX")
mock -r fedora-rawhide-x86_64 \
  --resultdir "$PWD/$resultdir" \
  --rebuild "dist/srpm/$package-*.src.rpm"
rpmlint "packages/$package/$package.spec" \
  "dist/srpm/$package-"*.src.rpm \
  "$resultdir"/*.rpm
```

Use a result directory containing only artifacts from this build. Keep the full Mock logs and unmodified lint output. Confirm the license report, dependency provides, installed license files, and runtime behavior. A successful host rebuild does **not** replace this isolated build or prove offline operation. See [toolchain commands](toolchain.md) for RPM inspection and the package's maintenance notes for package-specific source regeneration and test exclusions.

Record source, licensing, installation, and runtime checks with their scope and limitations in the package's `docs/audit.md`, when such an audit is needed. Before uploading sources to Fedora's lookaside cache, recheck licensing if sources change and address any license-report errors; independent reviewer evaluation is still required. The automated expression check alone does not establish license compliance.

## 3. Publish and open the review

1. Publish the exact matching spec and SRPM at public, directly downloadable HTTPS URLs. COPR artifacts can be used if they match the submitted spec. Prefer immutable/versioned URLs so later edits do not silently change review inputs.
2. Prepare package-specific review details using the [review template](templates/review.md), including artifact and build-log URLs. Complete pending checks before presenting the package as ready.
3. Open a [Fedora Package Review request](https://bugzilla.redhat.com/bugzilla/enter_bug.cgi?product=Fedora&format=fedora-review) using the Bugzilla account linked by email to your Fedora account.
4. If sponsorship is needed, put **FE-NEEDSPONSOR in the Blocks field**, not Depends On. Review can proceed before sponsorship.
5. Introduce yourself on the development mailing list with the review link and mention that you need sponsorship if applicable. Follow the onboarding guide for the introduction.
6. Respond to feedback and post updated spec/SRPM URLs after fixes. Only the reviewer sets approval (`fedora-review +`). If approval is complete but sponsorship is still needed, the supplied review process directs you to [packager sponsors](https://forge.fedoraproject.org/packaging/sponsors/issues).

## 4. After approval and sponsorship

Once the review is approved and the necessary account access is available:

- Configure a Fedora Forge token locally as described in the review-process reference; do not include it in commands committed here.
- Request dist-git with `fedpkg request-repo <package> <review-bug-number>`.
- After repository creation, clone it and import the approved SRPM with `fedpkg` following Fedora's linked new-package instructions. Upload source archives to the lookaside cache; keep the spec and package configuration in dist-git.
- Consider `%autorelease` and `%autochangelog` during migration, preserving upgrade ordering from published COPR builds. Do not change this monorepo's release mechanism merely to prepare the review.
- Build Rawhide with `fedpkg build`. Request supported release branches as needed and use Bodhi for release updates where required.
- Close the review as `NEXTRELEASE` when appropriate, and enable release monitoring and Koschei where available.

Follow the current linked Fedora instructions when executing these account-dependent steps. Record the actual status of repository requests, lookaside uploads, and official Fedora builds in the package-specific review record.
