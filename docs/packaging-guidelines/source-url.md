---
title: "Referencing Source"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/"
author:
published:
created: 2026-10-16
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
One of the design goals of rpm is to cleanly separate upstream source from vendor modifications. For the Fedora packager, this means that sources used to build a package should be the vanilla sources available from upstream. To help reviewers and QA scripts verify this, the packager needs to indicate where a reviewer can find the source that was used to make the rpm.

The most common case is where upstream distributes source as a `tar.gz`, `tar.bz2` or `zip` archive that we can download from an upstream website. In these cases you must use a full URL to the package in the `Source:` line. For example:

```
Source: https://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz

Source: https://ftp.gnome.org/pub/GNOME/sources/gnome-common/2.12/gnome-common-2.12.0.tar.bz2
```

|  | Smallest Compressed Archive  If the upstream source archive is available in multiple compressed formats that our tools can decompress, it’s best to use the one that is smallest in size. This ensures the smallest source rpm to save space on the mirrors and downloads of source RPM packages. |
| --- | --- |

## Using Forges (Hosted Revision Control)

Any software publishing website, permitting the download of source archives via normalized URLs, that can be deduced from a project root URL and version, commit, tag, scm, extension… values is a *“forge”* that can be supported by the `redhat-rpm-config` `%{forgemeta}` macro. Common Forge examples are *GitLab* and *GitHub*. `%{forgemeta}` centralizes and abstracts our knowledge about those forges, so packagers do not have to handle download quirks manually.

`%{forgemeta}` makes it easy to switch from release to tag to commit source archives. Using `%{forgemeta}`, forge download URLs or guideline changes are propagated to spec files without manual refactoring.

When those changes result in a different naming or structure of the source archive, the source file needs to be uploaded to the build system before rebuilding existing spec files. That is the main drawback of using `%{forgemeta}`.

The following examples show how to use the Forge macros in various situations.

### Release Example

```
# This template shows how to package a commit state using the forgemeta macro.
# That should be the default target use case.
# Other less common use cases are documented in separate templates.
#
# The project url on the forge, for example
# https://gitlab.gnome.org/GNOME/gtk/
%global forgeurl 
#
# Packaging a release requires setting Version before calling forgemeta.
# Because most forges follow the git model, and git made no provision for
# release objects, forgemeta will try to guess the customary way to write
# release tags on the selected forge.
# If it guesses wrong use the forge-tag template instead of this one.
Version:         
#
# forgemeta converts the supplied rpm variables to variables that can be used
# in the spec file. Most of those can be overriden before or after the
# forgemeta call.
#  – use the “-i” flag to display the variables forgemeta reads and sets
#  – use the “-v” flag if you want verbose processing
#  – remove  “-i” and “-v” before commit
%forgemeta

# The following lines use  variables computed by forgemeta as default values.
# You can replace them with manual definitions. For example, replace forgeurl
# with the project homepage if it exists separately from the repository URL.
# Only replace the variables when it adds value to the spec file and you
# understand the consequences. Release ordering is controlled by the packager
# with x%{?dist}/0.x%{?dist} number chains.
Name:    
Release: 1%{?dist}
Summary: 
URL:     %{forgeurl}
Source:  %{forgesource}
%description

%prep
# forgesetup calls setup with the correct flags for archives downloaded from
# the selected forge. A forgeautosetup autosetup wrapper is also provided. If
# you disagree with the computed setup/autosetup flags, just call
# setup/autosetup directly.
#  – use the “-v” flag if you want verbose processing
%forgesetup
#
# After this point the archive extraction is done. forgemeta is no longer used.

%build

%install

%check

%files
%license 
%doc 

%changelog
```

### Tag Example

```
# This template shows how to package a tag state using the forgemeta macro.
# For more explanations on forgemeta, read the forgemeta-release template.
#
# The project url on the forge
%global forgeurl 
#
# The tag being packaged
%global tag      
#
#  – use the “-i” flag to display the variables forgemeta reads and sets
#  – use the “-v” flag if you want verbose processing
#  – remove  “-i” and “-v” before commit
%forgemeta

# The following lines use variables computed by forgemeta as default values.
# You can replace them with manual definitions.
# forgemeta will prepend tag information to dist. Release ordering is
# controlled by the packager with x%{?dist}/0.x%{?dist} numbers chains.
Name:    
Version: 
Release: 1%{?dist}
Summary: 
URL:     %{forgeurl}
Source:  %{forgesource}
%description

%prep
#  – an autosetup wrapper, forgeautosetup, is also provided
#  – use the “-v” flag if you want verbose processing; remove it before commit
#  – call forgesetup/autosetup directly if you do not like the result
%forgesetup
#
# After this point the archive extraction is done. forgemeta is no longer used.

%build

%install

%check

%files
%license 
%doc 

%changelog
```

### Commit Example

```
# This template shows how to package a commit state using the forgemeta macro.
# For more explanations on forgemeta, read the forgemeta-release template.
#
# The project url on the forge
%global forgeurl 
#
# The commit being packaged (when using git, a full hash)
%global commit   
#
#  – use the “-i” flag to display the variables forgemeta reads and sets
#  – use the “-v” flag if you want verbose processing
#  – remove  “-i” and “-v” before commit
%forgemeta

# The following lines use variables computed by forgemeta as default values.
# You can replace them with manual definitions.
# forgemeta will prepend commit information to dist. Release ordering is
# controlled by the packager with x%{?dist}/0.x%{?dist} numbers chains.
Name:    
Version: 
Release: 1%{?dist}
Summary: 
URL:     %{forgeurl}
Source:  %{forgesource}
%description

%prep
#  – an autosetup wrapper, forgeautosetup, is also provided
#  – use the “-v” flag if you want verbose processing; remove it before commit
#  – call forgesetup/autosetup directly if you do not like the result
%forgesetup
#
# After this point the archive extraction is done. forgemeta is no longer used.

%build

%install

%check

%files
%license 
%doc 

%changelog
```

### Branch Example

```
# This template shows how to package a branch state using the forgemeta macro.
#
# BRANCH STATES ARE NOT REPRODUCIBLE AND SHOULD NEVER BE SHARED WITH OTHERS.
#
# For more explanations on forgemeta, read the forgemeta-release template.
#
# The project url on the forge
%global forgeurl 
#
# The branch being packaged
%global branch   
#
#  – use the “-i” flag to display the variables forgemeta reads and sets
#  – use the “-v” flag if you want verbose processing
#  – remove  “-i” and “-v” before commit
%forgemeta

# The following lines use variables computed by forgemeta as default values.
# You can replace them with manual definitions.
# forgemeta will prepend branch information to dist. Release ordering is
# controlled by the packager with x%{?dist}/0.x%{?dist} number chains.
Name:    
Version: 
Release: 1%{?dist}
Summary: 
URL:     %{forgeurl}
Source:  %{forgesource}
%description

%prep
#  – an autosetup wrapper, forgeautosetup, is also provided
#  – use the “-v” flag if you want verbose processing; remove it before commit
#  – call forgesetup/autosetup directly if you do not like the result
%forgesetup
#
# After this point the archive extraction is done. forgemeta is no longer used.

%build

%install

%check

%files
%license 
%doc 

%changelog
```

### Multiple Sources Example

```
# This template shows how to package multiple source archives using the
# forgemeta macro.
#
# PACKAGING MULTIPLE PROJECT ARCHIVES IN A SINGLE SPEC IS DISCOURAGED. IT OFTEN
# REQUIRES ERROR-INDUCING VERSIONNING DECISIONS. In rpm, versioning is not an
# administrative decoration. Versioning controls the upgrade logic. If upstream
# deemed necessary to release a project through multiple archives, mirror its
# decision using multiple spec files. That will be safer, simpler, and
# ultimately less work.
#
# For more explanations on forgemeta, read the forgemeta-release template.
#
# Start by declaring the characteristics of each source using a    number-suffixed
# variable block:
#  – no suffix and zero suffix blocks are aliases
#  – they are “special” and identify the main source archive
#  — they use Version: to identify a release
#  – other blocks use a version<number> variable for the same need
#  – the syntax is otherwise identical to single archive mode; see the various
#    forge templates for examples.
#
# Main archive. In this example we package a full release
%global forgeurl0 
Version:          

# Second archive.
%global forgeurl1 
%global version1  

# Third archive. This time a tag. Continue as necessary.
%global forgeurl2 
%global tag2      

#  – use the “-a” flag to process all the source archives in a single pass
#  – use     “-z <number>” to process only the declaration block suffixed with
#    <number>
#  — without “-a” of “-z <number>” only the main archive is processed
#  – use the “-i” flag to display the variables forgemeta reads and sets
#  – use the “-v” flag if you want verbose processing
#  – remove  “-i” and “-v” before commit
%forgemeta -a

# The following lines use variables computed by forgemeta as default values.
# You can replace them with manual definitions.
# Release ordering is controlled by the packager with x%{?dist}/0.x%{?dist}
# numbers chains.
Name:    
Release: 1%{?dist}
Summary: 
URL:     %{forgeurl0}
# https://github.com/rpm-software-management/rpm/issues/539
Source0: %{forgesource0}
Source1: %{forgesource1}
Source2: %{forgesource2}
%description

%prep
#  – use the “-a” flag to process all the source archives in a single pass
#  – use     “-z <number>” to process only the declaration block suffixed with
#    <number>
#  — without “-a” of “-z <number>” only the main archive is processed
#  – an autosetup wrapper, forgeautosetup, is also provided
#  – forgeautosetup does not understand “-a”
#  – use the “-v” flag if you want verbose processing; remove it before commit
#  – call forgesetup/autosetup directly if you do not like the result
%forgesetup -a
#
# After this point the archive extraction is done. forgemeta is no longer used.

%build

%install

%check

%files
%license 
%doc 

%changelog
```

## Using Revision Control

In some cases you may want to pull sources from upstream’s revision control system because there have been many changes since the last release and you think that a tarball that you generate from there will more accurately show how the package relates to upstream’s development. Here’s how you can use a comment to show where the source came from:

```
# The source for this package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
#  svn export -r 250 https://www.example.com/svn/foo/trunk foo-20070221
#  tar -cJvf foo-20070221.tar.xz foo-20070221
Source: foo-20070221.tar.xz
```

When pulling from revision control, please remember to use a Name-version-release compatible with the [Versioning](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/) Guidelines. In particular, check the section on [Complex versioning](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/#_complex_versioning).

## When Upstream uses Prohibited Code

Some upstream packages include patents or trademarks that we are not allowed to ship even as source code. In these cases you have to modify the source tarball to remove this code before you even upload it to the build system. Here’s an example of using a script to document how you went from the upstream tarball to the one included in the package:

From the spec:

```
Source: libfoo-1.0-nopatents.tar.gz
# libfoo contains patented code that we cannot ship.  Therefore we use
# this script to remove the patented code before shipping it.
# Download the upstream tarball and invoke this script while in the
# tarball's directory:
# ./generate-tarball.sh 1.0
Source1: generate-tarball.sh
```

generate-tarball.sh:

```
#!/bin/sh

VERSION=$1

tar -xzvf libfoo-$VERSION.tar.gz
rm libfoo-$VERSION/src/patentedcodec.c
sed -i -e 's/patentedcodec.c//' libfoo-$VERSION/src/Makefile

tar -czvf libfoo-$VERSION-nopatents.tar.gz libfoo-$VERSION
```

## Python Packages (pypi)

As PyPI has moved to storing files in directories which change depending on the file being stored, it is rather unpleasant to use in a `Source:` URL. Instead, files.pythonhosted.org can be used trough the `%{pypi_source}` macro, followed by the project name.

```
Source: %{pypi_source foo}
```

See more about the macro in the [Python guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#_source_files_from_pypi).

## Sourceforge.net

For packages hosted on sourceforge, use

```
Source: https://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
```

changing `.tar.gz` to whatever matches the upstream distribution. Note that we are using `downloads.sourceforge.net` instead of an arbitrarily chosen mirror. You may use the package name/package version instead of the `%{name}` and `%{version}` macros, of course.

Please note that the correct url is `downloads.sourceforge.net`, and **NOT** `download.sourceforge.net`.

## Git Hosting Services

If the upstream **does** create tarballs you should use them as tarballs provide an easier trail for people auditing the packages.

Git web-based hosting services provide a mechanism to create tarballs on demand, either from a specific commit revision, or from a specific tag. If the upstream does not create tarballs for releases, you can use this mechanism to produce them.

The full 40-character hash and associated git tag may be obtained by issuing the following git command:

[git ls-remote](https://git-scm.com/docs/git-ls-remote) https://HOSTING-SERVICE/OWNER/%{name}.git

```
HOSTING-SERVICE:  name of the service, i.e. "github.com", "bitbucket.org", "gitlab.com", etc.
OWNER:            username for the repository owner
PROJECT:          upstream project name (if it's identical to the package name, use %{name} instead)
```

You may also obtain the 40-character hash and associated git tag via the web-interface of the HOSTING-SERVICE, or by cloning the repository and issuing the [git show-ref](https://git-scm.com/docs/git-show-ref) command.

Once the commit hash and git tag are known, you can define them in your spec file as follows:

```
%global commit 40-CHARACTER-HASH-VALUE
%global gittag GIT-TAG
%global shortcommit %(c=%{commit}; echo ${c:0:7})    [GitHub]
%global shortcommit %(c=%{commit}; echo ${c:0:11})   [Bitbucket]
%global shortcommit %(c=%{commit}; echo ${c:0:7})    [GitLab]
%global shortcommit %(c=%{commit}; echo ${c:0:8})    [Sourcehut]
```

### Commit Revision

For the source tarball, you can use the following syntax:

```
Source:  https://github.com/OWNER/PROJECT/archive/%{commit}/%{name}-%{shortcommit}.tar.gz               [GitHub]
Source:  https://bitbucket.org/OWNER/PROJECT/get/%{commit}.tar.gz#/%{name}-%{shortcommit}.tar.gz        [BitBucket]
Source:  https://gitlab.com/OWNER/PROJECT/-/archive/%{commit}/%{name}-%{shortcommit}.tar.gz             [GitLab]
Source:  https://git.sr.ht/~OWNER/PROJECT/archive/%{shortcommit}.tar.gz#/PROJECT-%{shortcommit}.tar.gz  [Sourcehut]
...

%prep
%autosetup -n PROJECT-%{commit}              [GitHub]
%autosetup -n OWNER-PROJECT-%{shortcommit}   [BitBucket]
%autosetup -n PROJECT-%{commit}              [GitLab]
%autosetup -n PROJECT-%{shortcommit}         [Sourcehut]
```

If the release corresponds to a git tag with a sane numeric version, you must use that version to populate the `Version:` tag in the spec file. If it does not, look at the source code to see if a version is indicated there, and use that value. If no numeric version is indicated in the code, you may set `Version` to 0, and treat the package as a "pre-release" package (and make use of the `%{shortcommit}` macro). See [Prerelease versions](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/#_prerelease_versions) for details.

Alternately, if you are using a specific revision that is either a pre-release revision or a post-release revision, you must follow the "snapshot" guidelines. They are documented here: [Snapshots](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/#_snapshots). You can substitute `%{shortcommit}` for the git hash in `%{checkout}` in that section.

### Git Tags

[Git tags](https://git-scm.com/docs/git-tag) represent a particular code point that upstream deems important; and are typically used to mark release points.

Bitbucket uses the `%{shortcommit}` identifier as part of the archive directory structure; regardless of whether you use git tag or Commit Revision to retrieve it. This is shown in the %prep section example.

For the source tarball, you can use the following syntax:

```
Source:  https://github.com/OWNER/PROJECT/archive/%{gittag}/%{name}-%{version}.tar.gz          [GitHub]
Source:  https://bitbucket.org/OWNER/PROJECT/get/%{gittag}.tar.gz#/%{name}-%{version}.tar.gz   [BitBucket]
Source:  https://gitlab.com/OWNER/PROJECT/-/archive/%{gittag}/%{name}-%{version}.tar.gz        [GitLab]
Source:  https://git.sr.ht/~OWNER/PROJECT/archive/%{version}.tar.gz#/PROJECT-%{version}.tar.gz [Sourcehut]
...

%prep
%autosetup -n PROJECT-%{gittag}               [GitHub]
%autosetup -n OWNER-PROJECT-%{shortcommit}    [BitBucket]
%autosetup -n PROJECT-%{version}              [GitLab]
%autosetup -n PROJECT-%{version}              [Sourcehut]
```

## Using %{version}

Using `%{version}` in the `Source:` makes it easier for you to bump the version of a package, because most of the time you do not need to edit `Source:` when editing the spec file for the new package.

## Troublesome URLs

When upstream has URLs for the download that do not end with the tarball name rpm will be unable to parse the tarball out of the source URL. One workaround for many cases is to construct a URL where the tarball is listed in a "URL fragment":

```
Source: https://example.com/foo/1.0/download.cgi#/%{name}-%{version}.tar.gz
```

rpm will then use `%{name}-%{version}.tar.gz` as the tarball name. If you use `spectool -g foo.spec` to download the tarball, it will rename the tarball for you.

Sometimes this does not work because the upstream cgi tries to parse the fragment or because you need to login or fill in a form to access the tarball. In these cases, you have to put just the tarball’s filename into the `Source:` tag. To make clear where you got the tarball, you should leave notes in comments above the `Source:` line to explain the situation to reviewers and future packagers. For example:

```
# Mysql has a mirror redirector for its downloads
# You can get this tarball by following a link from:
# https://dev.mysql.com/downloads/mysql/5.1.html
Source: mysql-5.1.31.tar.gz
```

## Do not conditionalize Sources

When building an SRPM, it is critical that all of the sources are present, irrespective of the platform on which the SRPM is generated. For example, the following code **does not work** (the way you might expect):

```
%if 0%{?fedora} < 35
Source1: mysource-old.tar.bz2
Patch1: oldpatch.patch
%else
Source1: mysource-ng.tar.bz2
Patch1: ngpatch.patch
%endif
```

If you were to build this SRPM from a Fedora 34 host (`rpmbuild -bs mysource.spec`), the resulting SRPM would carry `mysource-old.tar.bz2` and `oldpatch.patch`. However, if you then try to use this SRPM to build for Fedora 35, the operation would fail because `mysource-ng.tar.bz2` is not available.

The correct behavior is to always carry all of the sources that might be used in the build and then conditionalize the **usage** of them instead. For example:

```
Source1: mysource-old.tar.bz2
Source2: mysource-ng.tar.bz2

Patch1: oldpatch.patch
Patch2: ngpatch.patch
...
%prep
%autosetup -N
...
%if 0%{?fedora} < 35
tar xf %{SOURCE1}
%patch 1 -p1
%else
tar xf %{SOURCE2}
%patch 2 -p1
%endif
```

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
