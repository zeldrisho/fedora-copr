---
title: "Package Review Process"
source: "https://docs.fedoraproject.org/en-US/package-maintainers/Package_Review_Process/"
author:
published:
created: 2026-10-17
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
In order for a new package to be added to Fedora, the package must first undertake a formal review. The process is governed by the FESCo approved [Package Review Policy](https://docs.fedoraproject.org/en-US/fesco/Package_review_policy/).

## Review Process

There are two roles in the review process, that of the contributor and that of the reviewer. This document presents both perspectives.

### Exemptions

Certain packages are exempted from the review process as described in the [Applicability section of Package Review Policy](https://docs.fedoraproject.org/en-US/fesco/Package_review_policy/#what). If an exemption is warranted, the contributor can directly request a repository for the package. The request to create a repo should include the `--exception` flag instead of a bug number:

```
fedpkg request-repo --exception <package_name>
```

### Contributor

A Contributor is defined as someone who wants to submit (and maintain) a new package in Fedora. To become a contributor, you must follow the detailed instructions to [Joining the Package Maintainers](https://docs.fedoraproject.org/en-US/package-maintainers/Joining_the_Package_Maintainers/).

As a Contributor, you should have already made a package which adheres to the [Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/) and does not contain any [Forbidden Items](https://fedoraproject.org/wiki/Forbidden_items).

When you’re happy with your spec file, you should then submit that SRPM to a package review. Currently, this is done by following these steps:

- Put your spec file and SRPM somewhere on the Internet where it can be directly downloaded (just http(s), no registration pages or special download methods, please). If you have no place to put your spec and SRPM, use [copr](https://copr.fedorainfracloud.org/).
- Fill out a [request for review in bugzilla](https://bugzilla.redhat.com/bugzilla/enter_bug.cgi?product=Fedora&format=fedora-review). Make absolutely certain to file this bug with an account tied to your FAS email address, otherwise your followup requests will be closed as invalid.

|  | If nobody comments on your review request, you might want to mail to a mailing list (for example, devel) or the [Package Review Swaps category](https://discussion.fedoraproject.org/c/workflows/pkg-review-swap/91) on Fedora Discussion to ask for a "review swap". This is an offer to do a review of someone else’s package in exchange for them reviewing your package. This is usually one-for-one, or can be some other private arrangement depending on the difficulty of the respective packages. |
| --- | --- |

- If you are not member of the [packager](https://accounts.fedoraproject.org/group/packager/) group, you need a sponsor. Add [FE-NEEDSPONSOR](https://bugzilla.redhat.com/show_bug.cgi?id=FE-NEEDSPONSOR) to the bugs being blocked by your review request. For more information read [How to Get Sponsored into the Packager Group](https://docs.fedoraproject.org/en-US/package-maintainers/How_to_Get_Sponsored_into_the_Packager_Group/).
- If this is a "re-review" request needed to [claim ownership](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Retirement_Process/#claiming) of a retired package, add `Unretirement` to the *Whiteboard* field.
- Wait for someone to review your package! At this point in the process, the `fedora-review` flag is blank, meaning that no reviewer is assigned.
- There may be comments from people that are not formally reviewing the package, they may add `NotReady` to the *Whiteboard* field, indication that the review request is not yet ready, because of some issues they report. After you have addressed them, please post the URLs to the updated SPEC and SRPM file and clear the Whiteboard. It is expected that you will respond to commentary, including updating your submission to address it; if you do not, your ticket will be closed.
- A reviewer takes on the task of reviewing your package. They will set the `fedora-review` flag to `?`.
- The reviewer will review your package. You should fix any blockers that the reviewer identifies. Once the reviewer is happy with the package, the `fedora-review` flag will be set to `+`, indicating that the package has passed review.
- If you have not yet been sponsored, request sponsorship by [raising an issue at packager-sponsors](https://forge.fedoraproject.org/packaging/sponsors/issues).
- When your package passes the review you should use `fedpkg` to request a Git repository for it. Before you can request a Git repository for the package, you will need a [Fedora Forge API token](https://forge.fedoraproject.org/user/settings/applications/tokens/new) with at least *Read and write* permissions for *issue*, added into `~/.config/rpkg/fedpkg.conf`:
	```
	[fedpkg.forgejo]
	token = <generated_code>
	```

You will probably want the token to have additional permissions to support other package-maintenance tasks.

You can also use `fedpkg set-distgit-token`.

- Request a Git repository for the package. For example, if the package name is `my-package` and the bugzilla review ticket is 12345,:
	```
	fedpkg request-repo my-package 12345
	```
	Check that your review bug is valid. It must have the `fedora-review` set to `+`, and it must be assigned to your reviewer. Otherwise your repository request will be closed as invalid.
- If you want to add your package to more Fedora releases and not just Rawhide, see [Requesting branches](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Maintenance_Guide/#requesting_branches).
- When [fedora-scm-requests tickets](https://forge.fedoraproject.org/releng/fedora-scm-requests/issues) for the requested repository and branches are closed, checkout the package:
	```
	fedpkg clone my-package
	```
- Now you can [import your SRPM package](https://docs.fedoraproject.org/en-US/package-maintainers/New_Package_Process_for_New_Contributors/#import_commit_and_build_your_package). Do a final check of spec file tags, etc.
- Request a Koji build by running `fedpkg build`. (You will need to set up [Kerberos for Fedora project](https://fedoraproject.org/wiki/Infrastructure/Kerberos))
- Repeat the process for other branches you may have requested above:
	- Checkout given branch: `fedpkg switch-branch f42`
	- Let Koji build the package for this branch: `fedpkg build`
- Request updates for Fedora release branches, if necessary, using `fedpkg update` or another Bodhi interface as detailed in [Bodhi](https://fedoraproject.org/wiki/Bodhi).
- If possible, add your package to [Upstream Release Monitoring](https://docs.fedoraproject.org/en-US/package-maintainers/Upstream_Release_Monitoring/).
- To be notified if your package stops building successfully when dependencies are updated in Fedora, you can enable [Koschei](https://fedoraproject.org/wiki/Koschei).
- You should make sure the review ticket is closed. You are welcome to close it once the package has been built on the requested branches. If you built for one of the Fedora release branches you can ask Bodhi to close the ticket for you when it completes the process. If you close the ticket yourself, use `NEXTRELEASE` as the resolution.

You do not need to go through the review process again for subsequent package changes, and should not reference the review ticket in subsequent updates you create in Bodhi.

### Reviewer

The Reviewer is the person who chooses to review a package.

The Reviewer can be any Fedora account holder who is a member of the [packager group](https://accounts.fedoraproject.org/group/packager/). (If the Contributor is not yet sponsored, the review can still proceed to completion but they will need to find a sponsor at some point.)

- Search [Package Review Tracker](https://fedoraproject.org/PackageReviewStatus/) for a review request that needs a reviewer: `fedora-review` flag is blank or the bug is assigned to `nobody@fedoraproject.org`.
- If you notice some issues that need to be solved before you want to start a formal review, add these issues in a comment and set the *Whiteboard* of the bug to contain `NotReady`. This helps other possible reviewers to notice that the review request is not yet ready for further review action.
- If you want to formally review the package, set the `fedora-review` flag to `?` and assign the bug to yourself.
- Review the package
	- Go through the MUST items listed in [Review Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/ReviewGuidelines/).
	- Go through the SHOULD items in [Review Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/ReviewGuidelines/).
	- The [FedoraReview](https://forge.fedoraproject.org/packaging/FedoraReview) tool (packaged as `fedora-review`) can help to automate this process.
- Include the text of your review in a comment in the ticket. For easy readability, simply use a regular comment instead of an attachment.
- Take one of the following actions:
	- **ACCEPT** - If the package is good, set the `fedora-review` flag to `+`. Do not close the review ticket yet - this will be done by the submitter once the package becomes available in Fedora.
	- **FAIL, LEGAL** - If the package is legally risky for whatever reason (known patent or copyright infringement, trademark concerns) close the bug as `WONTFIX` and leave an appropriate comment (i.e. *we don’t ship mp3, so stop submitting it*). Set the `fedora-review` flag to `-`, and have the review ticket block [FE-Legal](https://bugzilla.redhat.com/show_bug.cgi?id=FE-Legal).
	- **FAIL, OTHER** - If the package is just way off or unsuitable for some other reason, and there is no simple fix, then close the bug as `WONTFIX` and leave an appropriate comment (i.e. *we don’t package pornography for redistribution, sorry.* Or, *this isn’t a specfile, it’s a McDonald’s menu, sorry.*) Set the `fedora-review` flag to `-`.
	- **NEEDSWORK** - Anything that isn’t explicitly failed should be left open while the submitter and reviewer work together to fix any potential issues. Mark the bug as `NEEDINFO` while waiting for the reviewer to respond to improvement requests. This makes it easier for reviewers to find open reviews which require their input.
- Once a package is flagged as `fedora-review +` (or `-`), the Reviewer’s job is done although they may be called upon to assist the Contributor with the import/build/update process and to ensure that the Contributor closes the ticket when the process is complete.

## Definitions for fedora-review flag Settings

| fedora-review | (BLANK) | Package Needs Review |
| --- | --- | --- |
| fedora-review | ? | Package Under Review |
| fedora-review | \- | Package Failed Review, dropped for legal or other issues. |
| fedora-review | + | Package Approved |

## Special blocker tickets

There are a few tickets which can be placed in the "Blocks" field to indicate specific ticket statuses:

| FE-NEEDSPONSOR | The submitter requires a sponsor; the review can be done by anyone, but a sponsor will need to come and sponsor the submitter. |
| --- | --- |
| FE-DEADREVIEW | The review has been closed out because the submitter has left; users looking for packages to submit may find some possibilities in these dead tickets. |
| FE-Legal | The package is currently awaiting review by the legal team. |

## The Whiteboard

To save time for reviewers, the [New, reviewable Fedora package review tickets](https://fedoraproject.org/PackageReviewStatus/reviewable.html) page will hide certain tickets which are not reviewable. The *Whiteboard* field can be used to mark a ticket with various additional bits of status which will cause it to be hidden or displayed differently.

| NotReady | The package is not yet ready for review. It is possible to open a review ticket, mark it as NotReady, and continue to work on it until it’s ready to be seen by a reviewer. |
| --- | --- |
| BuildFails | The package fails to build. |
| AwaitingSubmitter | The package review is stalled and cannot proceed without input from the submitter. |
| Trivial | The package is trivial to review. See below. |
| Unretirement | A re-review needed to [claim ownership](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Retirement_Process/#claiming) of a retired package. |

The `Trivial` status is intended to indicate packages which, as an aid to new reviewers, are especially uncomplicated and easy to review. A ticket should not be marked as being trivial unless:

- The package is known to build and a link to a scratch build is included.
- The ticket explains any rpmlint output which is present.
- The spec contains nothing which is unnecessary in modern Fedora (such as `BuildRoot:`, a `%clean` section or `%defattr`).
- The spec is free from excessive or complicated macro usage.
- The spec uses only the least complicated scriptlets which are taken directly from the [Scriptlets](https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/) page.
- The package contains no daemons.
- The package is not especially security sensitive.
- The code has undergone a thorough inspection for licensing issues. Anomalies which would be found by `licensecheck` should be explained.

In short, this should be reserved only for those tickets which should be easily approachable by someone doing their first package review.

## Tracking of Package Requests

The [Package Review Tracker](https://fedoraproject.org/PackageReviewStatus/) provides various review-related reports and a simple way to search for reviews by package name or reporter name or others.

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
