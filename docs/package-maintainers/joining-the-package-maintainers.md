---
title: "Joining the Package Maintainers"
source: "https://docs.fedoraproject.org/en-US/package-maintainers/Joining_the_Package_Maintainers/"
author:
published:
created: 2026-10-17
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
So, you have decided to become a package maintainer in the Fedora Project? This guide will lead you through your first package submission. It can be a completely new package, or update to an existing package.

## Preparation

### Understand the Sponsorship Model

Admission to the `packager` group, which is a prerequisite for many packaging tasks, is not automatic. You should at least skim through [How to Get Sponsored into the Packager Group](https://docs.fedoraproject.org/en-US/package-maintainers/How_to_Get_Sponsored_into_the_Packager_Group/) now, so that in the likely case that you want to apply, you are prepared for it.

### Read the Guidelines

If you do not know how to create an RPM package, refer to [Packaging Tutorial](https://docs.fedoraproject.org/en-US/package-maintainers/Packaging_Tutorial/).

Read the [Packaging Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/). You need to be thoroughly familiar with these. They govern all package submissions. If you have questions, ask on the Fedora List.

### Create a Bugzilla Account

Make sure you have an account in [Red Hat Bugzilla](https://bugzilla.redhat.com/).

The email address that you use for your Bugzilla account should be the same email address as you use in the [Fedora Account System](#create-a-fedora-account) for all things related to Fedora Packaging.

### Create a Fedora Account

Create an account in the [Fedora Account System](https://docs.fedoraproject.org/en-US/fedora-accounts/user/). (This is *not* the same as the Bugzilla account.)

1. Visit the account system home: [https://accounts.fedoraproject.org/](https://accounts.fedoraproject.org/)
2. Click on *New account* and fill in the blanks. Note that the email you give should be the same as the one you gave Bugzilla. This allows the system to link privileges between the two accounts.
3. After you create your account, please be sure to agree to the Fedora CLA: Click on the *edit profile* link on the right, then the *Agreements* tab. If this says *view* you have agreed already, if it says *sign* you still need to agree.
4. You will also need to upload a public RSA SSH key. You need to use the matching private key to access Fedora machines via SSH. Keep in mind that uploading new public SSH key to all servers can take some time (about half hour). You can read more about this [here](https://fedoraproject.org/wiki/Cryptography).

### Join the important Mailing Lists

Consider joining the following mailing lists:

- [devel-announce](https://lists.fedoraproject.org/admin/lists/devel-announce@lists.fedoraproject.org/) is a low traffic, announcements only list where important development information is posted.
- [devel](https://lists.fedoraproject.org/admin/lists/devel@lists.fedoraproject.org/) is a high traffic mailing list where discussions about the development of Fedora are held.
- [packaging](https://lists.fedoraproject.org/admin/lists/packaging@lists.fedoraproject.org/) is the mailing list of the [Fedora Packaging Committee](https://fedoraproject.org/wiki/Packaging_Committee), who determine the official packaging guidelines for Fedora projects.

### Introduce yourself

Next, you should introduce yourself to the community on the [devel mailing](https://lists.fedoraproject.org/admin/lists/devel@lists.fedoraproject.org/) list. The primary purpose of this is to begin the process of building trust by allowing the Fedora community members to get to know you a bit more.

We want to break anonymity and foster real-world community within the project. You are under no obligation to reveal personal secrets. The objective is to establish a level of trust between yourself and the other members of the project. But you should at least use your real name when communicating with us. Also, a brief description of who you are, your motivations and perhaps a description of the software you have submitted for review are advisable.

```
Subject: Self Introduction:  <Your name>

Body:  Add any information you believe is applicable
including past experience in free and open source projects,
a link to the review request you have filed and
a brief description of yourself. You can also post
your GPG key information if you want to.
```

Feel free to participate in all the discussion that goes on in any of the lists. Community discussion and feedback is always encouraged.

### Understand your responsibilities

Software components included in Fedora need to be maintained actively, and bugs — especially security issues — need to be fixed in a timely manner. As a Fedora package maintainer, it is your primary responsibility to ensure this.

- Understand [Package Maintainer Responsibilities](https://docs.fedoraproject.org/en-US/fesco/Package_maintainer_responsibilities/).
- Get familiar with [Policy for Encouraging Comaintainers of Packages](https://docs.fedoraproject.org/en-US/fesco/Policy_for_encouraging_comaintainers_of_packages/).
- Do not be afraid to seek the help of the Fedora community via the development mailing list whenever needed.

### Read Other Submissions

Read some other package submissions to learn about packaging and gain familiarity with the process and requirements.

One way of doing this is to join the [package-review mailing list](https://lists.fedoraproject.org/archives/list/package-review@lists.fedoraproject.org/). All comments on Fedora package reviews are sent to this (read-only from your point of view) list.

### Configure Your Git

The first thing to do when you set up Fedora packaging is to configure your username and email address for Git. These are linked in each commit you do to Fedora packages.

```
git config --global user.name "John Doe"
git config --global user.email johndoe@example.com
```

### Install Packager Tools

Follow [Installing Packager Tools](https://docs.fedoraproject.org/en-US/package-maintainers/Installing_Packager_Tools/).

## Finding software you wish to maintain for Fedora

Being a Fedora packager means doing package maintenance. To get started, you need to find some packages to maintain.

### Existing software

Even packages that already exist in Fedora need regular maintenance. The Fedora version may be behind the latest upstream release, there may be bugs to be fixed upstream or in the packaging scripts, the packaging scripts can be improved even if the resulting package already works and so on.

To get involved in the maintenance of some packages, you should know what is going on with them. Subscribe to notifications about packages you consider interesting by adjusting the *Watch* setting for them in the [Package Sources](https://src.fedoraproject.org/).

There are also mailing lists for notifications about activity in any package. Note that the volume of these mailing lists is very high. Most probably they are only useful as input for automatic processing:

- [scm-commits](https://lists.fedoraproject.org/archives/list/scm-commits@lists.fedoraproject.org/) has all commits to all package repositories.
- [package-announce](https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/) has all stable updates.

### New software

If you intend to add a new package to Fedora, follow [New Package Process for New Contributors](https://docs.fedoraproject.org/en-US/package-maintainers/New_Package_Process_for_New_Contributors/).

## Getting Help

We know that this process can be as clear as mud sometimes, and we’re always trying to make it better. If you run into any problems, or have any questions please ask on the [devel mailing list](https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/) or on [Libera](https://libera.chat/).
