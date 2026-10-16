---
title: "New Package Process for New Contributors"
source: "https://docs.fedoraproject.org/en-US/package-maintainers/New_Package_Process_for_New_Contributors/"
author:
published:
created: 2026-10-16
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
This is a long version of the New Package Process, containing more details so new contributors can follow it more easily. Also the mandatory [sponsoring](https://docs.fedoraproject.org/en-US/package-maintainers/How_to_Get_Sponsored_into_the_Packager_Group/) step is included.

## Install Packager Tools

Follow [Installing Packager Tools](https://docs.fedoraproject.org/en-US/package-maintainers/Installing_Packager_Tools/).

## Check if the package already exists

If some useful software is not included in Fedora already, you can submit it as a new package. The package you are submitting can be of any Free and Open Source project.

Before creating your package, make sure that the software is not already in the Fedora repository:

- Check if the package already exists by searching in [Fedora Packages](https://packages.fedoraproject.org/).
- Search in the [Review Tracker](https://fedoraproject.org/PackageReviewStatus/) for packages under review.
- Check the [orphaned or retired packages that need new maintainers](https://packager-dashboard.fedoraproject.org/user/orphan).
- Be aware of [forbidden items](https://fedoraproject.org/wiki/Forbidden_items).

## Make a Package

- If you don’t know how to create an RPM package, see the [Packaging Tutorial](https://docs.fedoraproject.org/en-US/package-maintainers/Packaging_Tutorial/).
- Make sure that your package meets the [Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/) and [Package Naming Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/).
- Be aware of the [Package Review Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/ReviewGuidelines/) (they will be used during the package review).
- Make sure your package builds. This is surprisingly important because a significant number of submissions don’t.

## Upload Your Package

Upload your SRPM and SPEC files onto the Internet somewhere so that others can retrieve them. This can be anywhere accessible by a URL, but it is important that the files be directly accessible, not hidden behind some service that makes people wait to download things or redirects through advertising pages.

Using [Copr](https://copr.fedorainfracloud.org/) is recommended. It allows creating repositories using the src.rpm or spec file, which can be then shared with the reviewers. It also can create automatic builds from these files and distribute the results.

First you need to log to [Copr](https://copr.fedorainfracloud.org/), you can use your Fedora account.

Then follow this [tutorial](https://docs.copr.fedorainfracloud.org/screenshots_tutorial.html), to build the project. During the "New Build" step you need to upload your source, you can choose the one which works for you the best, but if you don’t have the source uploaded somewhere else, you can select the *Upload* option and then in the provide the step section, click on *Browse…* button to select a file. Now in the next section you need to specify the Chroots and other built options, select at least one `fedora-rawhide` chroot and adjust other settings as necessary.

After the build is completed you can use the following links for the review process:

- Link to Spec file: go to your copr packages, click the name of your package and then under general information look for your dist-git repositary. Find the **Spec** file in this repository tree and copy it’s link, but replace the **tree** part of the URL with the string **plain**, then use it for the review submission.
- Link to SRPM file: in your copr builds, click on the **id** of your last successful build and under general information look for link named directory. Here look in to the **/srpm-build/your\_build\_id/** folder and copy the **src.rpm** file URL for your review submission.

## Create Your Review Request

Fill out [Bugzilla Fedora review form](https://bugzilla.redhat.com/bugzilla/enter_bug.cgi?product=Fedora&format=fedora-review).

- Before submitting your request, be sure there’s not a previous request for the same package. There is a convenient search box on the [package review status page](https://fedoraproject.org/PackageReviewStatus/).
- Make sure that you put the **name of the package** (excluding version and release numbers) in the `Review Summary` field, along with a very **brief summary** of what the package is.
- Put a **description** of your package (usually, this can be the same thing as what you put in the spec `%description`) in the `Review Description` field. Include the **URLs** to your **SRPM** and **SPEC** files.
- Explain in the ticket that this is your first package and you need a sponsor. Also, include any information that may help prospective sponsors. If you’ve been active in other review work, include links. If you’re the upstream maintainer, be sure to say so.
- For bonus points, include a link to a successful koji build so that everyone knows you did all of your homework.

The review process is described in detail on the [Package Review Process](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Review_Process/) page.

## Inform Upstream

The Fedora Project prefers [Staying Close to Upstream Projects](https://docs.fedoraproject.org/en-US/package-maintainers/Staying_Close_to_Upstream_Projects/). Inform the developers that you are packaging the software. You can do that by sending them an email introducing yourself and pointing out the review request. This sets up the stage for future conversations. They will usually advertise the fact that their software is now part of Fedora or might want to inform you of important bugs in the existing release, future roadmaps etc.

## Watch for Feedback

Watch the Bugzilla report for your first package. You should get notifications of changes by email. Fix any blockers that the reviewer(s) point out.

## Add Package to Source Code Management (SCM) system and Set Owner

Before proceeding, please sync your account by login on [Fedora Package Sources](https://src.fedoraproject.org/) using your FAS credentials.

If you are becoming a maintainer for a new package, instead of being a co-maintainer, use [fedpkg](https://forge.fedoraproject.org/packaging/fedpkg) to request a new git repository for your package. The sub-command is `fedpkg request-repo`, which requires a Forgejo API token with at least *Read and write* permissions for *issue*. Configure the token with `fedpkg set-forgejo-token`. You will probably want the token to have additional permissions to support other package-maintenance tasks. You must specify the repository name and review bug number. For example:

```
fedpkg request-repo python-prometheus_client 1590452
```

The request will be reviewed and processed automatically. After processing, you will have access to commit and build the package. In case the automation does not work, you can report the problem to [Toddlers issue tracker](https://forge.fedoraproject.org/apps/toddlers/issues).

`fedpkg request-repo` only creates a branch for Rawhide. To request branches for other Fedora releases, see [Requesting branches](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Maintenance_Guide/#requesting_branches).

## Check out the distgit repository

You *could* check out your distgit repository now, but before doing that, consider doing `mkdir ~/fedora-scm ; cd ~/fedora-scm` — that way, all your files are inside a single directory. Also, run `ssh-add`, so that you won’t have to keep typing in your key password.

Now you are ready to checkout your distgit repository from the SCM:

```
fedpkg clone <your_package>
```

## Test Your Package

Refer to [Using Mock to test package builds](https://fedoraproject.org/wiki/Using_Mock_to_test_package_builds) and [Koji Scratch Builds](https://docs.fedoraproject.org/en-US/package-maintainers/Using_the_Koji_Build_System/#scratch_builds) for more information on testing your package. Mock uses your local system while Koji command line tool uses the Fedora build system server.

## Import, commit, and build your package

Now that you’ve checked out your (empty) distgit repository with `fedpkg`, cd into the repository’s main branch:

```
cd <package_name>
```

Run fedpkg to import the contents of the SRPM into the SCM:

```
fedpkg import <path_to_srpm>
```

```
# Review Changes, press 'q' to stop; Revert with: git reset --hard HEAD
git commit -m "Initial import (fedora#XXXXXX)."
git push
fedpkg build
```

Obviously, replace `PATH_TO_SRPM` with the full path (not URL) to your approved SRPM, and `XXXXXX` with the package review bug number.

If your package is using *autochangelog*, writing the bug number as specified will make the Fedora update system automatically close the bug when your package is submitted to Rawhide stable repository.

This imports into, commits, and builds only the **main** ([Rawhide](https://docs.fedoraproject.org/en-US/releases/rawhide/)) branch.

If the push fails with this kind of message:

```
W access for why DENIED to YOUR_ACCOUNT
fatal: The remote end hung up unexpectedly
Could not push: Command '['git', 'push']' returned non-zero exit status 128
```

Then you don’t have the necessary rights to modify that package branch. View `https://src.fedoraproject.org/rpms/PACKAGE_NAME` to request those rights.

For more information on using the Fedora package maintenance system, see the [Package maintenance guide](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Maintenance_Guide/).

## Update Your Branches (if desired)

Branches are `f#` (formerly `F-` and before that `FC-`), `main`, etc. So `f` is the branch for Fedora.

To switch to a branch first:

```
fedpkg switch-branch <branch>
```

(e.g. `f42`)

Merge the initial commit from main (Rawhide), creating an identical commit in the branch:

```
git merge rawhide
```

Push the changes to the server:

```
git push
```

Build the package:

```
fedpkg build
```

If there is another branch to work with repeat *To switch to a branch* and import and commit to each branch.

If everything goes well, it should queue up your branch for building, the package will cleanly build, and you’re done!

If it fails to build, the build system will send you an email to report the failure and show you to the logs. Commit any needed changes to git, bump the SPEC release number, and request a new build.

### Submit Package as Update in Bodhi

The Fedora update system called [Bodhi](https://bodhi.fedoraproject.org/) is used for pushing updates, classifying packages etc. You do not need to submit updates for Rawhide (main) manually because these are automatically created for you when the build completes. For all other branches, you must manually push updates for all builds that you would like to make available to users.

You can push an update using Bodhi via the command line using this in each branch:

```
fedpkg update
```

It is often easier to complete builds for all your branches and then push a single update using the [Bodhi web interface](https://bodhi.fedoraproject.org/updates/new). Bodhi is smart enough to split your update into individual updates, one for each Fedora release branch.

You can also select multiple builds from different packages to include in a single update using the web interface. This is useful when you would like to push linked builds, for example: an application package and its dependencies that are necessary for it to run correctly.

Please see the [Package Update Guide](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Update_Guide/) for more details.

## Make the package available in "comps" files

If appropriate for the package, make it available in "comps" files so that it can be selected during installation and included in dnf package group operations. See [How to use and edit comps.xml for package groups](https://fedoraproject.org/wiki/How_to_use_and_edit_comps.xml_for_package_groups?rd=PackageMaintainers/CompsXml) for more info.

### Watch for updates

Fedora has the infrastructure available for monitoring new upstream releases of the software you are packaging. Refer to [Upstream Release Monitoring](https://docs.fedoraproject.org/en-US/package-maintainers/Upstream_Release_Monitoring/) for more details.

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
