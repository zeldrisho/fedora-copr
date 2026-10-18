---
title: "Fedora Packaging Guidelines"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/"
author:
published:
created: 2026-10-16
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
The Packaging Guidelines are a collection of common issues and the severity that should be placed on them. While these guidelines should not be ignored, they should also not be blindly followed. If you think that your package should be exempt from part of the Guidelines, please bring the issue to the [Fedora Packaging Committee](https://forge.fedoraproject.org/packaging/guidelines).

These documents cover the fine details of acceptable Fedora packaging and while they may include various examples they will not be particularly useful as a tutorial. They also do not cover the details and policies relating to gaining access to the Fedora repositories as a packager, or the mechanics of actually creating and releasing packages as part of the distribution. For documents which cover those issues, please see the following:

It is the package reviewer’s responsibility to point out specific problems with a package and a packager’s responsibility to deal with those issues. The reviewer and packager work together to determine the severity of the issues (whether they block a package or can be worked on after the package is in the repository.) Please remember that any package that you submit must also conform to the [Review Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/ReviewGuidelines/).

The original author of these documents is [Tom 'spot' Callaway](https://fedoraproject.org/wiki/TomCallaway), though they were originally based on many other documents. They have been significantly modified over the years by many members of the Packaging Committee.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY in these guidelines are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

Report issues with these guidelines, including typos, [here](https://forge.fedoraproject.org/packaging/guidelines).

## Applicability

In general, these guidelines apply to the currently released, non-end-of-life versions of Fedora, as well as the development version of Fedora (Rawhide). If a particular portion of these guidelines is relevant only to a subset of those releases, this will be specifically noted. However, please note that Rawhide can change rapidly, and there will be times when changes are visible there which are not yet reflected here.

The guidelines also to some degree cover packages for EPEL, but only when combined with the [EPEL packaging guidelines](https://docs.fedoraproject.org/en-US/epel/epel-packaging/). Fedora packaging changes far more rapidly than EPEL packaging, so over time these guidelines will drift further away from any particular EPEL release and for the older supported EPEL release the differences can be quite significant. Portions of these guidelines which do not apply to EPEL will not generally be indicated.

## General Exception Policy

As these guidelines can never cover all possible contingencies, there will always be packages which need exceptions. It is the packager’s responsibility to follow these guidelines as closely as is feasible and to clearly document, as comments in the package specfile, instances where they cannot be followed.

If, in a guideline, the language "should" or "is suggested" is used and it is not feasible for the package to conform to that guideline, the packager may deviate from the it. The nature of the deviation and the reasoning behind it MUST be documented in the specfile.

Where the language "must", "is required to" or "needs to" is used, the packager may deviate from the guideline only with approval from the packaging committee. Please follow the procedure at the [Packaging Committee](https://fedoraproject.org/wiki/Packaging_Committee#Bringing_Issues_to_the_Committee) page for making these requests.

## Allowed Packages

Please review [What Can Be Packaged](https://docs.fedoraproject.org/en-US/packaging-guidelines/what-can-be-packaged/) to ensure that what is to be packaged is allowed in Fedora.

## Naming

You should go through the [Naming Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/) to ensure that your package is named appropriately.

## Version and Release

Documentation covering the proper way to use the Version and Release fields can be found [here](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/).

## Licensing

You should review the information regarding [licenses determined to be allowed in Fedora](https://docs.fedoraproject.org/en-US/legal/license-approval/) and the [Licensing Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) to ensure that your package is licensed appropriately and that the license is properly indicated.

### Fedora Trademarks

Packagers **MUST NOT** add any Fedora trademark assets including the Fedora logo, Fedora logo icons, or graphics that include the Fedora logo. Those assets **MUST** be added to the fedora-logos package. Your packages(s) install the logos by depending on the fedora-logos package. If the upstream contains Fedora trademark assets that you believe are used inappropriately, email [legal@fedoraproject.org](mailto:legal@fedoraproject.org)

This is because the Fedora logo is a trademark, which are handled under a different legal framework than code. It must only be distributed under terms that protect the trademark. Keeping Fedora trademarks separate in their own package instead of scattered across various other packages is also an essential practice for enabling remixes that necessarily must [not use the Fedora trademark](https://fedoraproject.org/wiki/Legal:Trademark_guidelines#Secondary_Mark), and instead roll their own \*-logos package or use the generic-logos package.

## Libraries and Applications

Many language- or domain-specific guidelines refer to "libraries", "modules", "plug-ins" or other terms specific to the language or domain. This is specifically important to package naming. Some applications may include libraries, and some libraries may include applications, so the distinction is not always clear.

### Library or Application?

- If the primary purpose of a package is to provide executables to be run by users, it SHOULD be packaged as an application. If it also includes libraries which may be imported or linked to by other code, see [Mixed Use Packages](#_mixed_use_packages) below.
- If the primary purpose of a package is to provide libraries intended to be imported or loaded into other code, it is considered a library and MUST be packaged as such. If it contains utility programs that can be run by users as well, see [Mixed Use Packages](#_mixed_use_packages) below.

It is left to the packager to determine the primary purpose of a package. Often times upstream will already have done this with their choice of naming and that choice SHOULD be followed by the Fedora packager.

### Mixed Use Packages

Many packages, regardless of their primary purpose, include both applications and libraries. In this case one or both SHOULD be packaged in subpackages in order to allow other applications to depend on only the library and not the associated application(s). Installing an application that depends on a library or service should not automatically pull in other applications associated with that library or service.

## Package Independence

Packages SHOULD be installable independently whenever this is technically feasible, but they MUST specify dependencies of correct type on other packages if necessary, see [Dependency Types](#_dependency_types) below.

Desktop applications MUST NOT depend on other desktop applications unless strictly required. In particular, packages that contain a visible `.desktop` file (a `.desktop` file that does not contain the line `NoDisplay=true`) SHOULD NOT have a `Requires`, `Recommends`, or `Supplements` on any other package containing a visible desktop file, directly or indirectly.

For example, it would be reasonable for a video game level editor to require the associated video game in order to function, or for an application’s plugin to require the associated application. But it would not be reasonable for an application that happens to use a database library to depend on a database management suite associated with that library, or for an application that happens to use a particular programming language to depend on management tools associated with that programming language.

If a source package provides multiple graphical applications, those applications SHOULD be packaged in separate subpackages when feasible.

## Spec Files

The spec file ("spec") is a fundamental element in the packaging workflow. Any change that is made to the package will include a change to the spec. Because packages in Fedora are maintained by a community of packagers as well as automated tooling, it is important for the specs to follow certain conventions. The bulk of these packaging guidelines involves what goes into a spec, but here are a few general items.

### Spec File Naming

The spec file MUST be named `%{name}.spec`. That is, if your package is named `example`, the spec file must be named `example.spec`.

### Spec Legibility

All spec files MUST be legible and maintained in such a way that the community of packagers is able to understand and work with them.

To help facilitate legibility, only macros and conditionals for Fedora and EPEL are allowed to be used in Fedora Packages. Use of macros and conditionals for other distributions, including Fedora derivatives, is not permitted in spec files of packages in the main Fedora repositories unless those macros and conditionals are also present in Fedora.

### Spec File Encoding

Unless you need to use characters outside the [ASCII repertoire](https://commons.wikimedia.org/wiki/File:Ascii_full.png), you will not need to be concerned about the encoding of the spec file. If you do need non-ASCII characters, save your spec files as UTF-8. If you’re in doubt as to what characters are ASCII, please refer to [this chart](https://commons.wikimedia.org/wiki/File:Ascii_full.png).

#### Non-ASCII Filenames

Similarly, filenames that contain non-ASCII characters must be encoded as UTF-8. Since there’s no way to note which encoding the filename is in, using the same encoding for all filenames is the best way to ensure users can read the filenames properly. If upstream ships filenames that are not encoded in UTF-8 you can use a utility like convmv (from the convmv package) to convert the filename in your %install section.

### Spec Maintenance and Canonicity

Fedora’s git repository is the canonical location for Fedora spec files. Maintainers MUST expect that other maintainers and automated tooling will make changes to their packages, potentially without communicating prior to doing so (though communication is always encouraged). If some maintainers are also attempting to keep copies of a spec in an outside repository, they MUST be prepared to merge changes made to the spec in Fedora’s repository, and MUST NOT overwrite those changes with a copy from an external repository or using `fedpkg import`.

## Source File Verification

Where the upstream project publishes OpenPGP signatures of their releases, Fedora packages **SHOULD** verify that signature as part of the RPM build process.

Although a checksum in the sources file certifies that a file retreived from the lookaside cache is the one that the packager uploaded, it is silent on whether the file is what the upstream project released. A signature by the upstream developers certifies that the source is identical to what they released. Verifying the signature as part of the build ensures that packagers don’t forget to verify it.

### Obtaining the Correct Keys

The verification method requires one or more OpenPGP keyring files with public keys from the upstream project. The keyrings shall together contain all the keys that are trusted to certify the authenticity of the sources, and **MUST NOT** contain any other keys.

Ideally the upstream project publishes such a keyring as a downloadable file. You shall download that file and do everything you reasonably can to verify that it is authentic. Then you shall add it unmodified to the package SCM, and provide its URL in the spec file so that others can verify it. The URL **MUST** use HTTPS or a similarly authenticated protocol if at all possible.

Even if you are unable to verify the key at the first addition, it still enhances security in a trust-on-first-use way. It will ensure that future attacks will be detected if the key is the right one, or that a current attack will be detected later if future releases are signed by the correct key.

### Verifying Signatures

When source file verification is done, it **MUST** be done first in the `%prep` section of the spec file, before any potentially compromised code is executed. The verification **MUST** be done with the macro `%{openpgpverify}`, which expands into a command whose parameters shall be the pathnames of the keyring, the signature and the signed file. `BuildRequires: openpgpverify` is necessary for the verification to work.

Any detached signature file (e.g. foo.tar.gz.asc or foo.tar.gz.sig) must be uploaded to the package lookaside cache alongside the source code, while the keyring must be committed directly to the package SCM.

The following format must be used:

```rpm-spec
Source0: ftp://ftp.example.com/pub/foo/%{name}-%{version}.tar.gz
Source1: ftp://ftp.example.com/pub/foo/%{name}-%{version}.tar.gz.asc
Source2: https://www.example.com/keyring-0123456789ABCDEF0123456789ABCDEF.pgp
…
BuildRequires: openpgpverify
…
%prep
%{openpgpverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data='%{SOURCE0}'
```

The first source is the actual tarball, the second one is the signature from upstream, and the third one is the keyring.

The macro also supports short form where you provide just the source numbers:

```rpm-spec
%openpgpverify -k2 -s1 -d0
```

### Exceptions

If the upstream tarball is signed using old keys depending on SHA1 digest or otherwise incompatible with current OpenPGP standard, legacy `%{gpgverify}` macro can be used until this is resolved (it has the same API and could be used as a drop-in replacement). Upstreams SHOULD be notified to update their keys, for example using following guide:

[https://www.redhat.com/en/blog/updating-gpg-keys-for-fedora-and-rhel](https://www.redhat.com/en/blog/updating-gpg-keys-for-fedora-and-rhel)

If the upstream tarball of a package needs to be modified, for example because it contains forbidden items, then the tarball cannot be verified as part of the build process. In this case the upstream OpenPGP keyring must still be included in the package SCM and the instructions/script used to build the stripped-down tarball needs to verify the upstream source.

If the upstream project does not publish a keyring file (for example if they publish only a fingerprint on their website and refer to a keyserver network for downloading the key), then you may need to create a keyring after you have verified the key. In this case there is no upstream URL to the keyring, so instead you should document how you created the keyring in a comment in the spec file. A minimal keyring with the key with the fingerprint `7D33D762FD6C35130481347FDB4B54CBA4826A18` can be created with the following command:

```
gpg2 --export --export-options export-minimal 7D33D762FD6C35130481347FDB4B54CBA4826A18 > keyring-7D33D762FD6C35130481347FDB4B54CBA4826A18.pgp
```

or with Sequoia CLI:

```
sq network keyserver search 7D33D762FD6C35130481347FDB4B54CBA4826A18 --output keyring-7D33D762FD6C35130481347FDB4B54CBA4826A18.pgp
```

If upstream signed a tarball differently, for example by signing only the uncompressed tarball but distributing a compressed version, then the verification step must be adjusted accordingly, for example:

```rpm-spec
Source0: ftp://ftp.example.com/pub/foo/%{name}-%{version}.tar.xz
Source1: ftp://ftp.example.com/pub/foo/%{name}-%{version}.tar.asc
Source2: https://www.example.com/keyring-0123456789ABCDEF0123456789ABCDEF.pgp
…
BuildRequires: openpgpverify xz
…
%prep
xzcat '%{SOURCE0}' | %{openpgpverify} --keyring='%{SOURCE2}' --signature='%{SOURCE1}' --data=-
```

If the data and the signature are combined in a single file, then the signed data must be written to an output file:

```rpm-spec
%{openpgpverify} --keyring='%{SOURCE1}' --data='%{SOURCE0}' --output=<pathname>
```

Packages that are vital during bootstrapping of Fedora may use a [bootstrap flag](#bootstrapping) to skip the verification before GPGverify and GnuPG have been built.

### Help

If you need help getting your package compliant to this guideline, or if you do not know what to do if a build fails on a signature verification, then you should seek help on the Fedora devel mailing list before circumventing the check, to make sure that you do not build compromised software.

## Architecture Support

All Fedora packages must successfully compile and build into binary rpms on at least one supported primary architecture, except where the package is useful only on a secondary architecture (such as an architecture-specific boot utility, microcode loader, or hardware configuration tool). Fedora packagers should make every effort to support all [primary architectures](https://fedoraproject.org/wiki/Architectures#Primary_Architectures).

Content, code which does not need to compile or build, and architecture independent code (noarch) are notable exceptions.

### Architecture Build Failures

If a Fedora package does not successfully compile, build or work on an architecture, then those architectures should be listed in the spec in `ExcludeArch`. Each architecture listed in `ExcludeArch` needs to have a bug filed in bugzilla, describing the reason that the package does not compile/build/work on that architecture. The bug number should then be placed in a comment, next to the corresponding `ExcludeArch` line. New packages will not have bugzilla entries during the review process, so they should put this description in the comment until the package is approved, then file the bugzilla entry, and replace the long explanation with the bug number. The bug should be marked as blocking one (or more) of the following bugs to simplify tracking such issues:

### Noarch with Unported Dependencies

Sometimes, you are working on a noarch package that can only run in locations that a different, arched package builds on. This is common for packages written in a scripting language which depend on the language’s interpreter package, for instance. If the arched package that your package deps on isn’t available on all architectures Fedora (or EPEL) targets you run into a situation where you may need to exclude your package from certain architectures' package repositories or prevent it from building on certain architectures in the buildsystem.

#### Arch-Specific Runtime and Build-Time Dependencies

You can limit both the architectures used to build a noarch package, and the repositories to which the built noarch package will be added, by using either the `ExcludeArch:` or `ExclusiveArch:` tags:

```rpm-spec
BuildArch: noarch
# List the arches that the dependent package builds on below
ExclusiveArch: %{ix86} %{arm} x86_64 noarch
```

Sometimes a language runtime you are packaging for will provide a macro for the arches it’s available on, for instance, `%{nodejs_arches}`. If it does exist, then you can use something like `ExclusiveArch: %{nodejs_arches} noarch` in your spec file. Take a look at the guidelines for the language to see if such a macro exists.

### No Arch-Specific Sources or Patches

Packages MUST NOT have `Source:` or `Patch:` tags which are conditionalized on architecture. For example, this is forbidden:

```rpm-spec
%ifarch ppc64
Patch0: build-fix-for-ppc64.patch
%endif
```

Conditionalizing `Source:` or `Patch:` tags by architecture causes the contents of the source package to differ depending on the architecture which was used to build it.

Note that this unfortunately prevents `%autosetup` from being used to apply patches when some of those patches apply only to certain architectures. The best solution is to write patches which simply work on all architectures. If that is not possible, then simply use `%autosetup -N` and to use the `%patch` macro to apply each patch using `%ifarch` or `%ifnarch` as appropriate. For example:

```rpm-spec
%prep
%autosetup -N
%ifarch s390x
%patch 0 -p1
%endif
```

## Filesystem Layout

Fedora follows the [Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/fhs.shtml) with regards to filesystem layout, with exceptions noted below. The FHS defines where files should be placed on the system.

### Exceptions

- Fedora allows cross-compilers to place files in `/usr/target`.
- The `/nix` top-level directory may be used exclusively for Nix runtime and package store. It may only be created and owned by the `nix-filesystem` package.
- Fedora does not allow new directories directly under `/` or `/usr` without FPC approval.

### Libexecdir

The [Filesystem Hierarchy Standard](https://www.pathname.com/fhs/) does not include any provision for libexecdir, but Fedora packages MAY store appropriate files there. Libexecdir (aka, `/usr/libexec` on Fedora systems) should only be used as the directory for executable programs that are designed primarily to be run by other programs rather than by users.

Fedora’s rpm includes a macro for libexecdir, `%{_libexecdir}`. Packagers are highly encouraged to store libexecdir files in a package-specific subdirectory of `%{_libexecdir}`, such as `%{_libexecdir}/%{name}`.

If upstream’s build scripts support the use of `%{_libexecdir}` then that is the most appropriate place to configure it (e.g., passing `--libexecdir=%{_libexecdir}/%{name}` to autotools configure). If upstream’s build scripts do not support that, `%{_libdir}/%{name}` is a valid second choice. If you have to patch support for using one of these directories in, then you should patch in LIBEXECDIR, preferably configurable at build time (so distributions that do not have `/usr/libexec` can set LIBEXECDIR to another directory more appropriate for their distro).

### Multilib Exempt Locations

If a package is exempt from multilib, it may use `%{_prefix}/lib` instead of `%{_libdir}`. Packages that contain architecture specific files that would ordinarily be installed into `%{_libexecdir}` are always considered ineligible for multilib. However, you should be sure that the (sub)package that they are in does not have other content that would be considered eligible for multilib. If this is not the case for the files you wish to do this in for your package or you are just unsure, ask FESCo for an explicit multilib exemption.

### /run

System services should store small volatile run-time data in `/run`. This is a tmpfs backed directory that is mounted in very early boot, before any services are started (and before `/var` is available). `/var/run` is a legacy symlink to `/run`.

### No Files or Directories Under /srv, /usr/local, or /home/$USER

The [FHS says](https://www.pathname.com/fhs/pub/fhs-2.3.html#SRVDATAFORSERVICESPROVIDEDBYSYSTEM):

```
"...no program should rely on a specific subdirectory structure of /srv existing
or data necessarily being stored in /srv. However /srv should always exist on FHS
compliant systems and should be used as the default location for such data.

Distributions must take care not to remove locally placed files in these
directories without administrator permission."
```

The FHS is explicitly handing control of the directory structure under `/srv` to the system administrator rather than the distribution. Therefore, no Fedora packages can have any files or directories under `/srv`, come preconfigured to use specific files or directories under `/srv`, to remove files there, or to modify the files there in any way.

In addition, no Fedora package can contain files or directories or modify files under:

- `/usr/local` as these directories are not permitted to be used by Distributions in the FHS
- `/home/$USER` as users can arbitrarily modify the files in their home directories and rpm packages that modify those files run the risk of destroying user data. Additionally, sites may be nfs mounting `/home` on many different types of systems or even network automounting them on demand. Modifying files in home directories that are thus configured will have negative effects in both of these situations.

It is important to note that the software in a Fedora package, once installed and configured by a user, can use `/srv` as a location for data. The package simply must not do this out of the box

### Limited Usage of /opt, /etc/opt, and /var/opt

`/opt` and its related directories (`/etc/opt` and `/var/opt`) is reserved for the use of vendors in the FHS. We have reserved the `fedora` name with [LANANA](https://www.lanana.org/lsbreg/providers/providers.txt) for our use. If a package installs files into `/opt` it may only use directories in the `/opt/fedora` hierarchy. Fedora attempts to organize this directory by allocating a subdirectory of our `/opt/fedora` directory for specific subsystems. If you think you need to use `/opt/fedora` please file an FPC ticket to decide whether it’s a valid use of `/opt` and what subdirectory should be allocated for your use.

Currently, we have allocated `/opt/fedora/scls`, `/etc/opt/fedora/scls`, and `/var/opt/fedora/scls` for use by [Software Collections](https://fedoraproject.org/wiki/User:Toshio/SCL_Guidelines_\(draft\)).

Because the Google-supplied Chrome packaging has chosen a specific file location for extension-specific files which, if used, would conflicts with the above guidelines, the Packaging Committee has approved the following exception: A package MAY install files into the `/etc/opt/chrome/native-messaging-hosts` directory, and may create that directory hierarchy, as long as package as a whole also supports Chromium. (The Chromium support MAY be in a different subpackage.) If Chrome in the future allows a more standard directory to be used for this purpose, this exception will be removed.

### Merged file system layout

Fedora has merged several directories that historically used to be separate.

| Path | Merged with | RPM Macro |
| --- | --- | --- |
| `/bin` | `/usr/bin` | `{_bindir}` |
| `/sbin` | `/usr/bin` | `%{_bindir}` |
| `/usr/sbin` | `/usr/bin` | `%{_bindir}` |
| `/lib64` or `/lib` | `/usr/lib64` or `/usr/lib` | `%{_libdir}` |
| `/lib` | `/usr/lib` | `%{_prefix}/lib` |

For example, end users will find that `/bin/sh` is the same file as `/usr/bin/sh`, and `/usr/sbin/sendmail` is the the same as `/usr/bin/sendmail`.

However, rpm file dependencies don’t work according to what’s on the filesystem, they work according to the path specified in the rpm `%files` section. So an rpm which specified:

```rpm-spec
%files
/bin/sh
```

would be able to satisfy a file dependency for `/bin/sh` but not for `/usr/bin/sh`. Packages **must** use the real filesystem paths in the `%files` section. If other packages have dependencies on a different path that resolves to the same file, and it is not convenient to update them to the new path, packages **may** use a virtual `Provides` to list the alternate path.

For instance:

```rpm-spec
Provides: /sbin/ifconfig
[...]
%files
%{_bindir}/ifconfig
```

## Use rpmlint

Run rpmlint on binary and source rpms to examine them for common errors, and fix them (unless rpmlint is wrong, which can happen, too). If you find rpmlint’s output cryptic, the `-e` switch to it can be used to get more verbose descriptions of most errors and warnings. Note that rpmlint will perform additional checks if given the name of an installed package. For example, `dnf install foo-1.0-1.f20.x86_64.rpm; rpmlint -i foo` will perform a set of tests on the foo package that `rpmlint foo-1.0-1.f20.x86_64.rpm` cannot. A community-maintained page on rpmlint issues can be found [here](https://fedoraproject.org/wiki/Common_Rpmlint_issues).

## Tags and Sections

- The `Copyright:`, `Packager:`, `Vendor:` and `PreReq:` tags MUST NOT be used.
- The `BuildRoot:` tag, `Group:` tag, and `%clean` section SHOULD NOT be used.
- The contents of the buildroot SHOULD NOT be removed in the first line of `%install`.
- The `Summary:` tag value SHOULD NOT end in a period.
- The `Source:` tags document where to find the upstream sources for the package. In most cases this SHOULD be a complete URL to the upstream tarball. For special cases, please see the [SourceURL Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/).
- URLs in the `URL:`, `Source:` and `Patch:` tags SHOULD require authentication of the server whenever possible. This typically means writing `https:` instead of `http:` or `ftp:`.

## Package Dependencies

All package dependencies (build-time or runtime, regular, weak or otherwise) MUST ALWAYS be satisfiable within the official Fedora repositories.

RPM can automatically determine dependencies for most compiled libraries and for some scripting languages such as Perl. Automatically determined dependencies MUST NOT be duplicated by manual dependencies.

Build dependencies, however, MUST be explicitly listed, unless you are using an automatic build dependency generator (e.g. [Rust](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/#_buildrequires) or [Python](https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#_build_time_dependency_generator)). Refer to the [Build-Time Dependencies (BuildRequires)](#buildrequires).

Versioned dependencies (build-time or runtime) SHOULD ONLY be used when actually necessary to guarantee that the proper version of a package is present. If a versioned dependency would be satisfied by a version present in three previous Fedora releases then a versioned dependency is not needed and a regular unversioned dependency SHOULD be used instead.

A versioned dependency on a package with a defined Epoch MUST be included in that dependency. Otherwise the dependency will not function as expected.

### Dependency Types

`Requires` MUST be used if the dependency is required for the software to function correctly.

If the package functions correctly but in diminished capacity, then `Recommends` or `Suggests` SHOULD be used. If the functionality should be available by default for users, `Recommends` SHOULD be used, and `Suggests` otherwise. Alternatively, the reverse dependencies `Supplements` or `Enhances` may be used in the other package. See [Packaging:WeakDependencies](https://docs.fedoraproject.org/en-US/packaging-guidelines/WeakDependencies/) for guidelines on using those dependency types.

### Architecture-specific Dependencies

A dependency is made arch-specific by appending the macro `%{?_isa}` to the package name. For example:

```rpm-spec
Requires: foo
```

becomes:

```rpm-spec
Requires: foo%{?_isa}
```

If the foo-devel package has a foo-config script, you can try doing a foo-config --libs and foo-config --cflags to get strong hints what packages should be marked as foo’s requirements. For example:

```console
$ gtk-config --cflags
-I/usr/include/gtk-1.2 -I/usr/include/glib-1.2 -I/usr/lib/glib/include -I/usr/X11R6/include
$ gtk-config --libs
-L/usr/lib -L/usr/X11R6/lib -lgtk -lgdk -rdynamic -lgmodule -lglib -ldl -lXi -lXext -lX11 -lm
```

This means that gtk+-devel should contain

`Requires: glib-devel%{?_isa} libXi-devel%{?_isa} libXext-devel%{?_isa} libX11-devel%{?_isa}`

### Rich/Boolean Dependencies

Packages MAY make full use of the [rich (or Boolean) dependency feature](https://rpm-software-management.github.io/rpm/manual/boolean_dependencies.html) supported in RPM.

### File and Directory Dependencies

RPM gives you the ability to depend on arbitrary files or directories instead of packages. Packages MAY include such dependencies for paths inside one of the following directories:

- `/usr/bin`
- `/etc`

They also MAY depend on paths listed in an explicit `Provides:`. They MUST NOT include dependencies on other paths, as that would require downloading of additional repository metadata to be enabled.

Please also note that it is not uncommon for multiple packages to provide the same directory. Directory dependencies SHOULD ONLY be used to express the dependency on that directory existing, not on any other functionality of any other package that might provide that directory.

When declaring file and directory dependencies, [installation path macros](https://docs.fedoraproject.org/en-US/packaging-guidelines/RPMMacros/#macros_installation) like `%{_bindir}` MUST NOT be used. `%{_bindir}` of the package that provides `sometool` may be different from `%{_bindir}` of a package that requires `sometool`. In such case, `BuildRequires: %{_bindir}/sometool` does not work as expected.

### Explicit Requires

Explicit Requires are Requires added manually by the packager in the spec file. Packages must not contain unnecessary explicit Requires on libraries. We generally rely on rpmbuild to automatically add dependencies on library SONAMEs. Modern package management tools are capable of resolving such dependencies to determine the required packages in many cases. However, present versions of rpmbuild only add deps on library SONAMES, not the library’s full version. This can be a problem if a library has added features over the course of time without backwards incompatibilities that would cause SONAMES to be changed. This can lead to a case where the user has an old version of a library installed, the new version of the library with new ABI is built in Fedora and an application using that ABI is built. If the user just attempts to install or update that one application without also updating the library, the application will install fine (because the SONAME dependency is satisfied) but will fail when run because the library installed on the system is missing features it needs.

Although you do need to add explicit library dependencies to keep this from occurring, there are drawbacks to manually specifying this in all your packages. History has shown that such dependencies add confusion when library/files are moved from one package to another, when packages get renamed, when one out of multiple alternative packages would suffice, and when versioned explicit dependencies become out-of-date and inaccurate. Additionally, in some cases, old explicit dependencies on package names require unnecessary updates/rebuilds. For example, Fedora packages are only required to retain historical provides for two full release cycles.

Because of this and because we hope to have this fixed in rpmbuild, this is something to be aware of but it’s not required that you explicitly specify the libraries you require with their version information.

When explicit library Requires are necessary, explicit library dependencies should typically be arch-specific (unless the packages involved are noarch) and there should be a spec file comment justifying it:

```rpm-spec
# The automatic dependency on libfubar.so.1 is insufficient,
# as we strictly need at least the release that fixes two segfaults.
Requires: libfubar%{?_isa} >= 0:1.2.3-7
```

Packagers should revisit an explicit dependency as appropriate to avoid it becoming inaccurate and superfluous. For instance in the example above, when no current Fedora release shipped with libfubar < 1.2.3-7, it is no longer necessary to list the explicit, versioned requirement.

### Filtering Auto-Generated Requires

RPM attempts to auto-generate Requires (and Provides) at build time, but in some situations, the auto-generated Requires/Provides are not correct or not wanted. For more details on how to filter out auto-generated Requires or Provides, please see: [Packaging:AutoProvidesAndRequiresFiltering](https://docs.fedoraproject.org/en-US/packaging-guidelines/AutoProvidesAndRequiresFiltering/).

## Build-Time Dependencies (BuildRequires)

It is important that your package list all necessary build dependencies using the `BuildRequires:` tag. You MAY assume that enough of an environment exists for RPM to function, to build packages and execute basic shell scripts, but you SHOULD NOT assume any other packages are present as RPM dependencies and anything brought into the buildroot by the build system can change over time.

### BuildRequires and %{\_isa}

You MUST NOT use arched BuildRequires. The arch ends up in the built SRPM but SRPMs need to be architecture independent. For instance, if you did this:

```rpm-spec
# Example of what *not* to do
BuildRequires:  foo%{?_isa} >= 3.3
```

Then the SRPM that is built in Fedora would have one of these Requirements depending on what builder the SRPM was created on:

```
foo(x86-32) >= 3.3
# or
foo(x86-64) >= 3.3
```

This would prevent yum-builddep or similar tools that use the SRPM’s requirements from operating correctly.

### BuildRequires Based on pkg-config

Fedora packages which use `pkg-config` to build against a library (e.g. 'foo') on which they depend, **SHOULD** express their build dependency correctly as `pkgconfig(foo)`. For more information, see [Packaging:PkgConfigBuildRequires](https://docs.fedoraproject.org/en-US/packaging-guidelines/PkgConfigBuildRequires/).

## Conditional Build-Time Dependencies

If the spec file contains conditional dependencies selected based on presence of optional `--with(out) foo` arguments to `rpmbuild`, build the source RPM to be submitted with the default options, i.e., so that none of these arguments are present in the `rpmbuild` command line. The reason is that those requirements get "serialized" into the resulting source RPM, i.e., the conditionals no longer apply.

## Summary and Description

The summary should be a short and concise description of the package. The description should expand upon this.

### Dos and Don’ts

- Do not end the summary with a period.
- The summary should be 80 characters/columns or less. If you are using something other than ASCII look at a utf length function or something similar to calculate the column count.
- Make sure that there are no lines in the description longer than 80 characters/columns. If you are using something other than ASCII look at a utf length function or something similar to calculate the column count.
- Do not include installation instructions in the description; it is not a manual. If the package requires some manual configuration or there are other important instructions to the user, refer the user to the documentation in the package. Add a *README.Fedora*, or similar, if you feel this is necessary.
- For consistency, we use the American English spelling and grammar rules in the summary and description. Packages can contain additional translated summary/description for supported Non-English languages, if available.

### Trademarks in Summary or Description

Packagers should be careful how they use trademarks in Summary or Description. There are a few rules to follow:

- Never use `(TM)` or `(R)` (or the Unicode equivalents, ™/®). It is incredibly complicated to use these properly, so it is actually safer for us to not use them at all.
- Use trademarks in a way that is not ambiguous. Avoid phrasing like "similar to" or "like". Some examples:
- **BAD:** It is similar to Adobe Photoshop.
- **GOOD:** It supports Adobe Photoshop PSD files, …
- **BAD:** A Linux version of Microsoft Office
- **GOOD:** A word-processor with support for Microsoft Office DOC files

If you’re not sure, ask yourself, is there any chance someone may get confused and think that this package is the trademarked item? When in doubt, try to leave the trademark out.

## Documentation

Any relevant documentation included in the source distribution should be included in the package in the proper documentation directory. Irrelevant documentation includes build instructions, the omnipresent *INSTALL* file containing generic build instructions, or example, and documentation for non-Linux systems, e.g. *README.MSDOS*. Also pay attention about which subpackage you include documentation in. For example API documentation belongs in the `-devel` subpackage, not the main one. Or if there’s a lot of documentation, consider putting it into a subpackage. In this case, it is recommended to use `*-doc` as the subpackage name.

Marking a *relative* path with `%doc` in the `%files` section will cause RPM to copy the referenced file or directory from `%_builddir` to the proper location for documentation. Files can also be placed in `%_pkgdocdir`, and the build scripts of the software being packaged may do this automatically when called in `%install`. However, mixing these methods is problematic and may result in duplicated or conflicting files, so use of `%doc` with *relative* paths and installation of files directly into `%_pkgdocdir` in the same source package is forbidden.

Files marked as documentation must not cause the package to pull in more dependencies than it would without the documentation. One simple way to ensure this in most cases is to remove all executable permissions from files in `%_pkgdocdir`.

Files located in `%_pkgdocdir` must not affect the runtime of the packaged software. The software must function properly and with unchanged functionality if those files are modified, removed or not installed at all.

Although license files are documentation, they are treated specially (including using a different tag). Please see [Licensing Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/) for how to handle them.

### Separate Documentation Packages

If building documentation requires many additional dependencies then you MAY elect to not build it in the main package and instead create a separate \*-doc source package which builds only the documentation. This separately packaged documentation MUST correspond to the version of the packaged software. In other words, if a new release of the software includes changes to the documentation, then the documentation package MUST also be updated. But if the new version of the software does not include documentation changes, then you MAY choose not to update the documentation package.

A comment SHOULD be added near Version tag of the main package to remind maintainers to update the separate \*-doc package when needed.

## Changelogs

The changelog describes the changes to the package that are relevant to the users of the package. This includes new upstream versions, important changes to how the package is built, rebuilds, and other changes affecting the outcome. Changes which are only relevant to packagers should not be mentioned in the changelog. This includes spec file cleanups, build error fixes or workarounds, and other changes which don’t have an effect on content of the binary packages.

The changelog **should** be generated automatically from git commit logs using the `%autochangelog` macro:

```rpm-spec
%changelog
%autochangelog
```

The commit subject (the first line of the commit message) and optionally some additional lines are used to generate the changelog text. The commit author name and email address and the commit timestamp are also used in changelog entry.

The text in the the commit message which will become part of the changelog should provide a brief summary of the changes relevant for the user. The commit message may contain additional information that is relevant to packagers.

If a particular change is related to a Bugzilla bug, include the bug ID in the changelog entry for easy reference, e.g.

```
Add README file (rhbz#1000042)
```

If a particular commit fixes a CVE, this information should be included too.

The intent is to give the user a hint as to what changed in a package update without overwhelming them with the technical details. They must never simply contain an entire copy of the source CHANGELOG entries. Links to upstream NEWS files or changelogs can be entered for those who want additional information.

See [autochangelog documentation](https://fedora-infra.github.io/rpmautospec-docs/autochangelog.html) for the details of how the changelog is generated from git commit messages, and how to create multi-line entries or skip entries for certain commits.

Packagers **may** alternatively use a manual changelog instead of the `%autochangelog` macro. This is described in [Manual Changelog](https://docs.fedoraproject.org/en-US/packaging-guidelines/manual-changelog/).

### Example

The packager updates package to version 1.0 and creates a commit

```
$ git show
commit 0000000000001234567890ABCDEF000000000000
Author: Joe Packager <joe@example.com>
Date:   Wed Jun 14 2003

    Version 1.0

    ... (rhbz#1000024)
    - Also fixes the slowdown reported in rhbz#1000025
    - Upstream changelog: https://example.com/package/NEWS.html#v1.0

    Whitespace in the spec file has been cleaned up.

diff --git package.spec package.spec
index 5c77064c03..efcd53a61c 100644
--- package.spec
+++ package.spec
@@ -1,5 +1,5 @@
 Name:           package
-Version:        0.1
+Version:        0.2
 Release:        %autorelease
...
```

When the package is built, an appropriate changelog entry will be generated. It can be previewed with `rpmautospec generate-changelog`:

```
$ rpmautospec generate-changelog
* Wed Jun 14 2003 Joe Packager <joe@example.com> - 0.2-1
- Version 1.0 (rhbz#1000024)
- Also fixes the slowdown reported in rhbz#1000025
- Upstream changelog: https://example.com/package/NEWS.html#v1.0
```

Note that the sentence about whitespace is not included in the changelog.

## Manpages

As man pages are the traditional method of getting help on a Unix system, packages SHOULD contain them for all executables. If some man pages are absent, packagers SHOULD work with upstream to add them. It is also occasionally possible to find pages created by other distributions, or to use the output of the `help2man` program; those are often useful as a starting point. When installing man pages, note that RPM will re-compress them into its preferred format. So the `%files` section MUST reference manpages with a pattern that takes this into account:

```rpm-spec
%files
%{_mandir}/man1/foo.1*
```

Note also that files installed in `%{_mandir}` are automatically marked by RPM as documentation. Thus it is not necessary to use `%doc`.

For localised manpages, use `%find_lang --with-man` as described in [Handling Locale Files](#handling_locale_files).

## Compiler

Fedora packages should default to using gcc as the compiler (for all languages that gcc supports) or clang if upstream does not support building with gcc. However, if there is a good technical reason, packagers may choose not to use the default compiler. Examples of valid technical reasons to not use the default compiler, include but are not limited to:

- The default compiler cannot build a package correctly.
- The packager needs to disable a compiler feature (e.g. LTO) in order for the default compiler to correctly compile their package.
- The default compiler takes significantly longer to build a package.
- The default compiler is missing a feature that would benefit the package.

Packagers choosing to use a non-default compiler should document the reason for this decision in a comment in the spec file.

## Compiler Macros

If clang is being used to build a package, packagers must set the %toolchain macro to clang:

```rpm-spec
%global toolchain clang
```

This ensures that Fedora’s clang-specific compiler flags are used when compiling.

If a packager wants to use conditional macros in a spec file to make it easier to switch between two different compilers, then the following macros names should be used:

```rpm-spec
%bcond_with toolchain_clang
%bcond_with toolchain_gcc
```

Packagers may also use the %build\_cc, %build\_cxx, or %build\_cpp macros in the spec file in place of hard-coding the compiler name. The values of these variables are controled by setting the %toolchain macro to either clang or gcc.

## Compiler Flags

Compilers used to build packages must honor the applicable compiler flags set in the system rpm configuration. Honoring means that the contents of that variable is used as the basis of the flags actually used by the compiler during the package build.

For C, C++, and Fortran code, the [%{optflags} macro](https://docs.fedoraproject.org/en-US/packaging-guidelines/RPMMacros/#build-flags-macros-and-variables) contains these flags. Overriding these flags for performance optimizations (for instance, -O3 instead of -O2) is generally discouraged. If you can present benchmarks that show a significant speedup for this particular code, this could be revisited on a case-by-case basis. Adding to and overriding or filtering parts of these flags is permitted if there’s a good reason to do so; the rationale for doing so must be documented in the specfile.

Packages SHOULD avoid editing the 'CFLAGS' etc. environment variables by hand, and instead use methods for compiler flags manipulation described in [this documentation](https://src.fedoraproject.org/rpms/redhat-rpm-config/blob/rawhide/f/buildflags.md)

There are certain, security related flags that are commonly allowed. These flags may degrade performance slightly but the increased security can be worthwhile for some programs.

### PIE

PIE adds security to executables by composing them entirely of position-independent code. Position-independent code (PIC) is machine instruction code that executes properly regardless of where in memory it resides. PIE allows Exec Shield to use address space layout randomization to prevent attackers from knowing where existing executable code is during a security attack using exploits that rely on knowing the offset of the executable code in the binary, such as return-to-libc attacks.

In Fedora, PIE is enabled by default. To disable it in your spec, add:

```rpm-spec
%undefine _hardened_build
```

If your package meets any of the following criteria you MUST NOT disable the PIE compiler flags:

- Your package is long running. This means it’s likely to be started and keep running until the machine is rebooted, not start on demand and quit on idle.
- Your package has suid binaries, or binaries with capabilities.
- Your package runs as root.

## Debuginfo Packages

Packages should produce useful `-debuginfo` packages, or explicitly disable them when it is not possible to generate a useful one, but rpmbuild would do it anyway. Whenever a `-debuginfo` package is explicitly disabled, an explanation why it was done is required in the specfile. Debuginfo packages are discussed in more detail in a separate document, [Packaging:Debuginfo](https://docs.fedoraproject.org/en-US/packaging-guidelines/Debuginfo/).

## Devel Packages

Fedora packages must be designed with a logical separation of files. Specifically, -devel packages must be used to contain files which are intended solely for development or needed only at build-time. This is done to minimize the install footprint for users. There are some types of files which almost always belong in a -devel package:

- Header files (foo.h), usually found in /usr/include
- Static library files when the package does not provide any matching shared library files. See [Packaging Static Libraries](#packaging-static-libraries) for more information about this scenario.
- Unversioned shared system library files, when a matching versioned shared system library file is also present. For example, if your package contains:

```
/usr/lib/libfoo.so.3.0.0
/usr/lib/libfoo.so.3
/usr/lib/libfoo.so
```

The versioned shared library files (/usr/lib/libfoo.so.3.2.0 and /usr/lib/libfoo.so.3) are necessary for users to run programs linked against libfoo, so they belong in the base package. The other, unversioned, shared library file (/usr/lib/libfoo.so) is only used to actually link libfoo to code being compiled, and is not necessary to be installed on a users system. This means that it belongs in a -devel package. Please note that in most cases, only the fully versioned shared library file (/usr/lib/libfoo.so.3.2.0) is an actual file, all of the other files are symbolic links to it. When a shared library file is only provided in an unversioned format, the packager should ask upstream to consider providing a properly versioned library file. However, in such cases, if the shared library file is necessary for users to run programs linked against it, it must go into the base package. If upstream versions the shared library file at a future point, packagers must be careful to move to the versioned layout described above.

### Unversioned Shared Objects

As an additional complication, some software generates [unversioned shared objects](https://docs.fedoraproject.org/en-US/packaging-guidelines/Unversioned_shared_objects/) which are not intended to be used as system libraries. These files are usually plugins or modular functionality specific to an application, and are not to be located in the ld library paths or cache. These types of unversioned shared objects do not need to go into a -devel package. They are only loaded at runtime and should be included in a private directory of the main package.

For specific details about how to deal with these types of DSOs, please see [unversioned shared objects](https://docs.fedoraproject.org/en-US/packaging-guidelines/Unversioned_shared_objects/) for detailed guidance.

### Exceptions

There are some notable exceptions to this packaging model, specifically:

- compilers often include development files in the main package because compilers are themselves only used for software development, thus, a split package model does not make any sense.

When in doubt as to whether a file belongs in the base package or in -devel, packagers should consider whether the file is necessary to be present for a user to use or execute the functionality in the base package properly, or if it is only necessary for development. If it is only necessary for development, it must go into a -devel package.

As with all Fedora Packaging Guidelines, it is recognized that there are unique situations that fall outside of the boundaries of this model. Should you come across such a case, please open a ticket with the [Fedora Packaging Committee](https://forge.fedoraproject.org/packaging/guidelines) and explain it to us so that we can extend the Guidelines to address it.

### Pkgconfig Files (foo.pc)

The placement of pkgconfig(.pc) files depends on their usecase. Since they are almost always used for development purposes, they should be placed in a -devel package. A reasonable exception is when the main package itself is a development tool not installed in a user runtime, e.g. gcc or gdb.

## Requiring Base Package

Subpackages are often extensions for their base package and in that case they should require their base package. When a subpackage requires the base package, it **MUST** do so using a fully versioned arch-specific (for non-noarch packages) dependency:

```rpm-spec
Requires: %{name}%{?_isa} = %{version}-%{release}
```

Devel packages are an example of a package that must require their base packages using a fully versioned dependency. -libs subpackages which only contain shared libraries do not normally need to explicitly depend on their base packages as they usually do not need the base package to be functional libraries.

If you end up in a situation where the main package depends on the subpackage and the subpackage on the main package you should think carefully about why you don’t have everything in the main package.

## Shared Libraries

Whenever possible (and feasible), Fedora packages containing libraries SHOULD build them as shared libraries. It is not necessary to call `ldconfig` when installing shared libraries.

### Downstream.so Name Versioning

In cases where upstream ships unversioned.so **library** (so this is not needed for plugins, drivers, etc.), the packager **MUST** try to convince upstream to start versioning it.

If that fails due to unwilling or unresponsive upstream, the packager may start versioning downstream but this must be done with caution and ideally only in rare cases. We don’t want to create a library that could conflict with upstream if they later start providing versioned shared libraries. Under no circumstances should the unversioned library be shipped in Fedora.

For downstream versioning, the name should be composed like this:

```
libfoobar.so.0.n
```

The *n* should initially be a small integer (for instance, "1"). we use two digits here ("0.n") because the common practice with upstreams is to use only a single digit here. Using multiple digits helps us avoid potential future conflicts. Do not forget to add the SONAME field (see below) to the library.

When new versions of the library are released, you should use an [ABI comparison tool](https://fedoraproject.org/wiki/How_to_check_for_ABI_changes_in_a_package) to check for ABI differences in the built shared libraries. If it detects any incompatibilities, bump the *n* number by one.

#### SONAME Handling

When running an executable linked to shared object with SONAME field, the dynamic linker checks for this field instead of filename to determine the object with which it should link. This allows developers to simply link against the unversioned library symlink and the dynamic linker will link against the correct object.

Keep in mind that although the filename is usually the library’s SONAME plus an incrementing minor version there’s nothing that intrinsically links these. ldconfig uses the SONAME as the value for a symlink to the actual filename. The dynamic linker then uses that symlink to find the library, disregarding the actual filename. The dynamic linker merely does a simple equality check on the field and does not check for ABI incompatibilities or similar problems. This is the main reason for using an [ABI comparison tool](https://fedoraproject.org/wiki/How_to_check_for_ABI_changes_in_a_package) and incrementing the SONAME.

The SONAME field is written to the shared object by linker, using (at least in case of `ld`) the `-soname SONAME` flags. This can be passed as an option to `gcc` like this:

```console
$ gcc $CFLAGS -Wl,-soname,libfoo.so.0.n -o libfoo.so.0.n
```

If you want to check if the SONAME field is set and what value it has, use the `objdump` command (from `binutils`):

```console
$ objdump -p /path/to/libfoo.so.0.n | grep 'SONAME'
```

## Packaging Static Libraries

Packages including libraries SHOULD exclude static libs as far as possible (e.g., by configuring with *\--disable-static*). Applications linking against libraries SHOULD link against shared libraries not static versions.

Libtool archives, *foo.la* files, SHOULD NOT be included. Packages using libtool will install these by default even if you configure with *\--disable-static*, so they may need to be removed before packaging. Due to bugs in older versions of libtool or bugs in programs that use it, there are times when it is not always possible to remove \*.la files without modifying the program. In most cases it is fairly easy to work with upstream to fix these issues. Note that if you are updating a library in a stable release (not devel) and the package already contains \*.la files, removing the \*.la files SHOULD be treated as an API/ABI change — i.e., removing them changes the interface that the library gives to the rest of the world thus MUST follow Fedora policies for potentially destabilizing updates.

### Packaging Static Libraries

- In general, packagers SHOULD NOT ship static libraries.
- We want to be able to track which packages are using static libraries (so we can find which packages need to be rebuilt if a security flaw in a static library is fixed, for instance). There are two scenarios in which static libraries are packaged:
	1. **Static libraries and shared libraries.** In this case, the static libraries MUST be placed in a *\*-static* subpackage. Separating the static libraries from the other development files in *\*-devel* allow us to track this usage by checking which packages `BuildRequire` the *\*-static* package. The intent is that whenever possible, packages will move away from using these static libraries, to the shared libraries. If the *\*-static* subpackage requires headers or other files from *\*-devel* in order to be useful it MUST require the *\*-devel* subpackage.
	2. **Static libraries only.** When a package only provides static libraries you MAY place all the static library files in the *\*-devel* subpackage. When doing this you also MUST have a virtual Provide for the *\*-static* package:
		```rpm-spec
		%package devel
		Provides: foo-static = %{version}-%{release}
		```

Packages which explicitly need to link against the static version MUST `BuildRequire: foo-static`, so that the usage can be tracked.

- If (and only if) a package has shared libraries which require static libraries to be functional, the static libraries can be included in the *\*-devel* subpackage. The devel subpackage must have a virtual Provide for the *\*-static* package, and packages dependent on it must `BuildRequire` the *\*-static* package.

### Packaging Header Only Libraries

Certain libraries, especially some C++ template libraries, are header only libraries. Since the code is generated during compile time, they act just like static libraries and need to be treated as such.

```rpm-spec
%package devel
Provides: foo-static = %{version}-%{release}
```

Packages which use the header library must `BuildRequire: foo-static`, so that the usage can be tracked.

#### Use noarch only in subpackages

The base package for a header library MUST NOT be marked noarch. This ensures that any tests are run on all architectures, and makes it possible to detect whether the build or install process has modified the headers based on the build architecture.

When the contents of subpackages, including the `-devel` package, are actually architecture-independent, they may still be marked noarch. Since the base package for a header library typically has no `%files` list, this may result in an arched package that builds only noarch rpms. This may require adding `%global debug_package %{nil}` to the spec file in order to avoid empty `debugsourcefiles.list` issues.

### Statically Linking Executables

Executables and libraries SHOULD NOT be linked statically against libraries which come from other packages. (It is of course acceptable for files generated during a package’s build process to be linked statically against `.a` files generated as part of that build process.)

If it is necessary to link against `.a` files from a different package, a build dependency on the `-static` package (not just the `-devel` package) which provides those files MUST be present so that the usage can be tracked.

## Bundling and Duplication of System Libraries

Fedora packages SHOULD make every effort to avoid having multiple, separate, upstream projects bundled together in a single package.

All packages whose upstreams allow them to be built against system libraries MUST be built against system libraries. In this case, bundled libraries (and/or their source code) MUST be explicitly deleted during `%prep`. Build scripts may need to be patched to deal with this situation. Whenever possible, the patch should conditionalize the use of the bundled libraries, so that the patch can be sent upstream for consideration.

All packages whose upstreams have no mechanism to build against system libraries MAY opt to carry bundled libraries, but if they do, they MUST include an indication of what they bundle. This provides a mechanism for locating libraries with bundled code which can, for example, assist in locating packages which may have particular security vulnerabilities.

To indicate an instance of bundling, first determine the name and version of the bundled library:

- If the bundled package also exists separately in the distribution, use the name of that package. Otherwise consult the [Naming Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/) to determine an appropriate name for the library as if it were entering the distribution as a separate package.
- Use the [Versioning Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/) to determine an appropriate version for the library, if possible. If the library has been forked from an upstream, use the upstream version that was most recently merged in or rebased onto, or the version the original library carried at the time of the fork.

Then at an appropriate place in your spec, add `Provides: bundled(<libname>) = <version>` where `<libname>` and `<version>` are the name and version you determined above. If it was not possible to determine a version, use `Provides: bundled(<libname>)` instead. Note that `Provides:` on the main package are not inherited by subpackages, so that you may have to put them on the appropriate subpackage instead; this applies in particular in cases where only a subpackage is built, such as Python packages.

In addition to indicating bundling in this manner, packages whose upstreams have no mechanism to build against system libraries must be contacted publicly about a path to supporting system libraries. If upstream refuses, this must be recorded in the spec file, either in comments placed adjacent to the Provides: above, or in an additional file checked into the SCM and referenced by a comment placed adjacent to the `Provides:` above.

### Avoid Bundling of Fonts in Other Packages

Fonts in general-purpose formats such as Type1, OpenType TT (TTF) or OpenType CFF (OTF) are subject to specific packaging guidelines ([Packaging/FontsPolicy](https://docs.fedoraproject.org/en-US/packaging-guidelines/FontsPolicy/)), and should always be packaged in the system-wide font repositories instead of private application directories. For more information, see: [Packaging/FontsPolicy](https://docs.fedoraproject.org/en-US/packaging-guidelines/FontsPolicy/).

## Beware of rpath

Sometimes, code will hardcode specific library paths when linking binaries (using the -rpath or -R flag). This is commonly referred to as an rpath. Normally, the dynamic linker and loader (ld.so) resolve the executable’s dependencies on shared libraries and load what is required. However, when -rpath or -R is used, the location information is then hardcoded into the binary and is examined by ld.so in the beginning of the execution. Since the Linux dynamic linker is usually smarter than a hardcoded path, we usually do not permit the use of rpath in Fedora.

There is a tool called *check-rpaths* which is included in the *rpmdevtools* package. It is a good idea to add it to the `%__arch_install_post` macro in your `~/.rpmmacros` config file:

```rpm-spec
%__arch_install_post          \
/usr/lib/rpm/check-rpaths     \
/usr/lib/rpm/check-buildroot
```

When *check-rpaths* is run, you might see output like this:

```
ERROR   0001: file '/usr/bin/xapian-tcpsrv' contains a standard rpath '/usr/lib64' in [/usr/lib64]
```

Any rpath flagged by check-rpaths **MUST** be removed.

### rpath for Internal Libraries

When a program installs internal libraries they are often not installed in the system path. These internal libraries are only used for the programs that are present in the package (for example, to factor out code that’s common to the executables). These libraries are not intended for use outside of the package. When this occurs, it is acceptable for the programs within the package to use an rpath to find these libraries.

Example:

```
# Internal libraries for myapp are present in:
%{_libdir}/myapp/
%{_libdir}/myapp/libmyapp.so.0.3.4
%{_libdir}/myapp/libmyapp.so

# myapp has an rpath to %{_libdir}/myapp/
readelf -d /usr/bin/myapp | grep RPATH
 0x0000000f (RPATH)                      Library rpath: [/usr/lib/myapp]
```

|  | **Non-Internal Libraries**: When programs outside of the package are supposed to link against the library, it is better to use the [Alternative to Rpath](#alternatives-to-rpath) or simply move the libraries into `%{_libdir}` instead. That way the dynamic linker can find the libraries without having to link all the programs with an rpath. |
| --- | --- |

### Alternatives to rpath

Often, rpath is used because a binary is looking for libraries in a non-standard location (standard locations are /lib, /usr/lib, /lib64, /usr/lib64). If you are storing a library in a non-standard location (e.g. /usr/lib/foo/), you should include a custom config file in /etc/ld.so.conf.d/. For example, if I was putting 32 bit libraries of libfoo in /usr/lib/foo, I would want to make a file called "foo32.conf" in /etc/ld.so.conf.d/, which contained the following:

```
/usr/lib/foo
```

Make sure that you also make a 64bit version of this file (e.g. foo64.conf) as well (unless the package is disabled for 64bit architectures, of course).

### Removing rpath

There are several different ways to fix the rpath issue:

- If the application uses configure, try passing the *\--disable-rpath* flag to configure.
- If the application uses a local copy of libtool, add the following lines to the spec after %configure:

```rpm-spec
%configure
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
```

- Sometimes, the code/Makefiles can be patched to remove the *\-rpath* or *\-R* flag from being called. This is not always easy or sane to do, however.
- As a last resort, Fedora has a package called *chrpath*. When this package is installed, you can run `chrpath --delete` on the files which contain rpaths. So, in our earlier example, we’d run:

```
chrpath --delete $RPM_BUILD_ROOT%{_bindir}/xapian-tcpsrv
```

Make sure that you remember to add a **BuildRequires: chrpath** if you end up using this method.

## Configuration Files

Configuration files must be marked as such in packages.

As a rule of thumb, use `%config(noreplace)` instead of plain `%config` unless your best, educated guess is that doing so will break things. In other words, think hard before overwriting local changes in configuration files n package upgrades. An example case when **not** to use `noreplace` is when a package’s configuration file changes so that the new package revision wouldn’t work with the config file from the previous package revision. Whenever plain `%config` is used, add a brief comment to the specfile explaining why.

Don’t use %config or %config(noreplace) under /usr. /usr is deemed to not contain configuration files in Fedora.

### Configuration of Package Managers

Packages MUST NOT install repository configuration files which violate the [Third Party Repository Policy](https://docs.fedoraproject.org/en-US/fesco/Third_Party_Repository_Policy/), unless those files are installed under `%{_docdir}`.

## Per-Product Configuration

In the Fedora.next world, we will have a set of curated Fedora Products as well as the availability of classic Fedora. Historically, we have maintained a single set of configuration defaults for all Fedora installs but different target use-cases have different needs. Please see the [Per-Product Configuration Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Per-Product_Configuration/) for instructions on how to create packages that need to behave differently between Fedora.next Products.

## Initscripts

SystemV-style initscripts are forbidden in Fedora. Systemd units must be used instead.

## Systemd Units

Detailed guidelines for packaging systemd units and systemd-managed services are [here](https://docs.fedoraproject.org/en-US/packaging-guidelines/Systemd/).

## Desktop Files

If a package contains a GUI application, then it needs to also include a properly installed.desktop file. For the purposes of these guidelines, a GUI application is defined as any application which draws a window and runs from within that window. Installed.desktop files MUST follow the [desktop-entry-spec](https://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html), paying particular attention to validating correct usage of Name, GenericName, [Categories](https://standards.freedesktop.org/menu-spec/latest/apa.html), [StartupNotify](https://standards.freedesktop.org/startup-notification-spec/startup-notification-latest.txt) entries.

### Icon Tag in Desktop Files

The icon tag can be specified in two ways:

- Full path to specific icon file:

`Icon=/usr/share/pixmaps/comical.png`

- Short name without file extension:

`Icon=comical`

The short name without file extension is preferred, because it allows for icon theming (it assumes.png by default, then tries.svg and finally.xpm), but either method is acceptable.

### .desktop File Creation

If the package doesn’t already include and install its own.desktop file, you need to make your own. You can do this by including a.desktop file you create as a Source: (e.g. Source3: %{name}.desktop) or generating it in the spec file. Here are the contents of a sample.desktop file (comical.desktop):

```
[Desktop Entry]
Name=Comical
GenericName=Comic Archive Reader
Comment=Open .cbr & .cbz files
Exec=comical
Icon=comical
Terminal=false
Type=Application
Categories=Graphics;
```

### desktop-file-install Usage

It is not simply enough to just include the.desktop file in the package, one MUST run `desktop-file-install` (in `%install`) OR `desktop-file-validate` (in `%check` or `%install`) and have `BuildRequires: desktop-file-utils`, to help ensure.desktop file safety and spec-compliance. `desktop-file-install` MUST be used if the package does not install the file or there are changes desired to the.desktop file (such as add/removing categories, etc). `desktop-file-validate` MAY be used instead if the.desktop file’s content/location does not need modification. Here are some examples of usage:

```rpm-spec
desktop-file-install                                    \
--dir=%{buildroot}%{_datadir}/applications              \
%{SOURCE3}
```

```rpm-spec
desktop-file-install                                    \
--add-category="AudioVideo"                             \
--delete-original                                       \
--dir=%{buildroot}%{_datadir}/applications              \
%{buildroot}/%{_datadir}/applications/foo.desktop
```

```rpm-spec
desktop-file-validate %{buildroot}/%{_datadir}/applications/foo.desktop
```

Do **not** apply a vendor tag to.desktop files (using --vendor).

## AppData Files

Packages containing graphical applications should include AppData files. See [Packaging:AppData](https://docs.fedoraproject.org/en-US/packaging-guidelines/AppData/) for the relevant guidelines.

## Macros

Packagers are strongly encouraged to use macros instead of hard-coded directory names (see [RPMMacros](https://docs.fedoraproject.org/en-US/packaging-guidelines/RPMMacros/)). However, in situations where the macro is longer than the path it represents, or situations where the packager feels it is cleaner to use the actual path, the packager is permitted to use the actual path instead of the macro. There are several caveats to this approach:

- The package must be consistent. For any given path, within the same spec, use either a hard-coded path or a macro, not a combination of the two.
- %{\_libdir} must always be used for binary libraries due to multi-lib, you may not substitute a hard-coded path.

Macros with names beginning with underscores are generally considered to be implementation details internal to RPM and its associated macro packages and SHOULD NOT be referenced in specfiles except to set their values in order to influence RPM behavior. This implies that macro forms of system executables SHOULD NOT be used. For example, `rm` should be used in preference to `%{__rm}`. However, in some cases needed data are simply not provided under names which are not prefixed with underscores. If that is the case, the macro named with leading underscores MAY be used. Authors of macro packages are encouraged to avoid using leading underscores when naming macros which are intended to be used in specfiles (as opposed to being set).

Having macros in a Source: or Patch: line is a matter of style. Some people enjoy the ready readability of a source line without macros. Others prefer the ease of updating for new versions when macros are used. In all cases, remember to be consistent in your spec file and verify that the URLs you list are valid. spectool (from the rpmdevtools package) can aid you in checking that whether the URL contains macros or not.

If you need to determine the actual string when it contains macros, you can use rpm. For example, to determine the actual Source: value, you can run:

```
rpm -q --specfile foo.spec --qf "$(grep -i ^Source foo.spec)\n"
```

### %autosetup

As an alternative to the usual `%setup` macro, the `%autosetup` can be used. In addition to the normal %setup tasks, it will apply all defined Patch# items in the spec automatically. It is also capable of handling VCS formatted patch files, but this will require additional BuildRequires, and assumes that *all* patch files in the spec are formatted for that single VCS type. For this reason, it is not recommended that you specify a VCS with `%autosetup`. For more details on proper use of `%autosetup`, refer to the [RPM documentation](https://rpm-software-management.github.io/rpm/manual/autosetup.html).

### Using %{buildroot} and %{optflags} vs $RPM\_BUILD\_ROOT and $RPM\_OPT\_FLAGS

There are two styles of defining the rpm Build Root and Optimization Flags in a spec file:

|  | macro style | variable style |
| --- | --- | --- |
| Build Root | %{buildroot} | $RPM\_BUILD\_ROOT |
| Opt. Flags | %{optflags} | $RPM\_OPT\_FLAGS |

There is very little value in choosing one style over the other, since they will resolve to the same values in all scenarios. You should pick a style and use it consistently throughout your packaging.

Mixing the two styles, while valid, is bad from a QA and usability point of view, and should not be done in Fedora packages.

### Why the %makeinstall Macro Should Not Be Used

Fedora’s RPM includes a `%makeinstall` macro but it must **NOT** be used when make install DESTDIR=%{buildroot} works. %makeinstall is a kludge that can work with Makefiles that don’t make use of the DESTDIR variable but it has the following potential issues:

- `%makeinstall` overrides a set of Make variables during "make install" and prepends the %{buildroot} path, i.e. it performs make prefix="%{buildroot}%{\_prefix}" libdir="%{buildroot}%{\_libdir} …".
- It is error-prone and can have unexpected effects when run against less than perfect Makefiles, e.g., the buildroot path may be included in installed files where variables are substituted at install-time.
- It can trigger unnecessary and wrong rebuilds when executing "make install", since the Make variables have different values compared with the %build section.
- If a package contains libtool archives, it can cause broken \*.la files to be installed.

Instead, Fedora packages should use: `%make_install` (Note the "\_"!), `make DESTDIR=%{buildroot} install` or `make DESTDIR=$RPM_BUILD_ROOT install`. Those all do the same thing.

### Source RPM Buildtime Macros

All macros in `Summary:` and `%description` need to be expandable at srpm buildtime. Because SRPMs are built without the package’s BuildRequires installed, depending on macros defined outside of the spec file can easily lead to the unexpanded macros showing up in the built SRPM. One way to check is to create a minimal chroot and build the srpm:

```
mock --init
mock --copyin [SRPM] /
mock --shell bash
rpm -ivh [SRPM]
cd /builddir/build/SPECS
rpmbuild -bs --nodeps [SRPM]
rpm -qpiv /builddir/build/SRPMS/[SRPM]
```

Check the `rpm` output for unexpanded macros (`%{foo}`) or missing information (when\`%{?foo}\` is expanded to the empty string). Even easier is to simply avoid macros in `Summary:` and `%description` unless they are defined in the current spec file.

### Improper Use of %\_sourcedir

Packages which use files itemized as Source# files, must refer to those files by their `Source#` macro name, and must not use `$RPM_SOURCE_DIR` or `%{sourcedir}` to refer to those files. See [Packaging:RPM\_Source\_Dir](https://docs.fedoraproject.org/en-US/packaging-guidelines/RPM_Source_Dir/) for full details.

### Software Collection Macros

[Software Collections](https://fedoraproject.org/wiki/User:Toshio/SCL_Guidelines_\(draft\)) are to be kept to separate packages from mainstream packages similar to how [MingW packages](https://docs.fedoraproject.org/en-US/packaging-guidelines/MinGW/) are managed.

In the past, SCL macros were allowed to be present inside of mainstream packages if they were not used. Since we’re now building SCLs, we are now enforcing a strict separation. Packages **MUST** be updated to restrict SCL macros to only those packages particularly approved as part of an SCL.

### Packaging of Additional RPM Macros

Additional RPM macros must be stored in %{\_rpmmacrodir}. They must be named using the syntax "macros.$PACKAGE" (e.g. macros.perl).

Normally, these files are packaged in the -devel subpackage, since they are usually only needed for building other packages. However, in some situations, this is not always ideal and packagers are encouraged to use their best judgment when determining the proper package for these files. RPM macro files MUST NOT be marked as `%config`.

## Scripting Inside of Specfiles

Sometimes it is necessary to write a short script (perhaps a one-liner) that is executed in the `%prep`, `%build`, or `%install` sections of a spec file to get some information about the build environment. In order to simplify the dependency graph, spec files should only use the following languages for this purpose:

- Python
- Perl
- Standard programs used in shell programing, for instance gawk or sed
- Lua (as supported by the native lua interpreter in rpm)

Additionally, if your package cannot build without a specific scripting language (such as Ruby, or Tcl), and therefore already has a BuildRequires on that language, it may also be called from the spec file.

Note: If you call Perl or Python in your spec file (and it is not already a BuildRequires for the package), you need to explicitly add a BuildRequires for Perl or Python.

## Handling Locale Files

Translation files may be handled by different programs for different frameworks. Make sure you add BuildRequires: for the correct package or else your package could fail to generate translation files in the buildroot.

If the package uses gettext for translations, add

```rpm-spec
BuildRequires: gettext
```

For Qt-based packages that use the Linguist tool chain, for the localization utilities add the appropriate qtX-linguist package

```rpm-spec
BuildRequires: qt6-linguist
```

If you have few enough locale files that they can all go into one package, you can use the `%find_lang` macro. (If you need to split your package into separate language packs, please see [the langpack guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Langpacks/).) This macro will locate all of the them belonging to your package (by name), and put this list in a file. You can then use that file to include all of the locales. `%find_lang` should be run in the %install section of your spec file, after all of the files have been installed into the buildroot. The correct syntax for `%find_lang` is usually:

```rpm-spec
%find_lang %{name}
```

In some cases, the application may use a different "name" for its locales. You may have to look at the locale files and see what they are named. If they are named `myapp.mo`, then you will need to pass `myapp` to `%find_lang` instead of `%{name}`. After `%find_lang` is run, it will generate a file in the active directory (by default, the top level of the source dir). This file will be named based on what you passed as the option to the `%find_lang` macro. Usually, it will be named `%{name}.lang`. You should then use this file in the `%files` list to include the locales detected by `%find_lang`. To do this, you should include it with the -f parameter to `%files`.

```rpm-spec
%files -f %{name}.lang
%{_bindir}/foobar
...
```

Note that `%find_lang` by default searches for gettext locales, but it can also handle Qt translations, localised manpages and help files.

```rpm-spec
%find_lang %{name} --with-gnome
```

```rpm-spec
%find_lang %{name} --with-kde
```

To process Qt’s `.qm` binary translation files use

```rpm-spec
%find_lang %{name} --with-qt
```

To process localised manpages (doesn’t include the default, non-localised one), use

```rpm-spec
%find_lang %{name} --with-man
```

To see all the options, run `/usr/lib/rpm/find-lang.sh` in the terminal.

Names different from `%{name}` (e.g. multiple manpages) must be handled via separate calls to `%find_lang`.

Here is an example of proper usage of `%find_lang`, in `foo.spec` with the "foo" application localised using gettext and man pages named "bar" instead of "foo":

```rpm-spec
Name: foo
...
%prep
%setup -q

%build
%configure --with-cheese
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install
%find_lang %{name}
%find_lang bar --with-man

%files -f %{name}.lang -f bar.lang
%license LICENSE
%doc README
%{_bindir}/%{name}
%{_mandir}/man1/bar.1*

%changelog
* Fri Jan 13 2012 Karel Volny <kvolny@redhat.com> 0.1-2
- add man pages example

* Thu May 4 2006 Tom "spot" Callaway <tcallawa@redhat.com> 0.1-1
- sample spec that uses %%find_lang
```

### Why do we need to use %find\_lang?

Using `%find_lang` helps keep the spec file simple, and helps avoid several other packaging mistakes.

- Packages that use `%{_datadir}/*` to grab all the locale files in one line also grab ownership of the locale directories, which is not permitted.
- Most packages that have locales have lots of locales. Using `%find_lang` is much easier in the spec file than having to do:

```rpm-spec
%{_datadir}/locale/ar/LC_MESSAGES/%{name}.mo
%{_datadir}/locale/be/LC_MESSAGES/%{name}.mo
%{_datadir}/locale/cs/LC_MESSAGES/%{name}.mo
%{_datadir}/locale/de/LC_MESSAGES/%{name}.mo
%{_datadir}/locale/es/LC_MESSAGES/%{name}.mo
...
```

- As new locale files appear in later package revisions, `%find_lang` will automatically include them when it is run, preventing you from having to update the spec any more than is necessary.

Keep in mind that usage of `%find_lang` in packages containing locales is a MUST unless the locale files are broken out into langpacks. In which case, you should follow [the langpack guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Langpacks/).

## Log Files

Packages which generate log files should write out their logfiles in a package-specific (and package owned) directory under %{\_localstatedir}/log. Unless the software being packaged rotates its own logs, it must also ship a logrotate config file to rotate its log file(s).

### logrotate Config File

Logrotate config files should be named in a way that matches the daemon/software which is generating the logs, which is usually (though not always) the same name as the package. When unsure, use "%{name}.conf". These files must be placed in %{\_sysconfdir}/logrotate.d, and should use standard file permissions (0644) and ownership (root:root).

Since these are config files, they must be marked as %config(noreplace) in the %files list.

#### Example Minimal logrotate Config File

```
/var/log/example/*log {
    missingok       # If the log file is missing, go on to the next one without issuing an error message
    notifempty      # Don't do any rotation if the logfile is empty
    compress        # Compress older files with gzip
    delaycompress       # Don't compress yesterdays files
}
```

## Timestamps

When adding file copying commands in the spec file, consider using a command that preserves the files' timestamps, e.g., `cp -p` or `install -p`.

When downloading sources, patches etc., consider using a client that preserves the upstream timestamps. For example `wget -N` or `curl -R`. To make the change global for wget, add this to your `~/.wgetrc`: `timestamping = on`, and for curl, add to your `~/.curlrc`: `-R`.

## Parallel Make

Whenever possible, invocations of `make` should be done as

```rpm-spec
%make_build
```

This generally speeds up builds and especially on SMP machines.

Do make sure, however, that the package builds cleanly this way as some make files do not support parallel building. Therefore you should consider adding

```rpm-spec
%_smp_mflags -j3
```

to your `~/.rpmmacros` file — even on UP machines — as this will expose most of these errors.

## Scriptlets

Packages may contain pieces of run-time code that are triggered during DNF transactions. These are called sriptlets and are documented [here](https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/).

## Build Scripts

Build scripts of the packages (%prep, %build, %install, %check and %clean) may only alter files (create, modify, delete) under %{buildroot}, %{\_builddir} and valid temporary locations like /tmp, /var/tmp (or $TMPDIR or %{\_tmppath} as set by the rpmbuild process) according to the following matrix

|  | /tmp, /var/tmp, $TMPDIR, %{\_tmppath} | %{\_builddir} | %{buildroot} |
| --- | --- | --- | --- |
| %prep | yes | yes | no |
| %build | yes | yes | no |
| %install | yes | yes | yes |
| %check | yes | yes | no |
| %clean | yes | yes | yes |

Further clarification: That should hold true irrespective of the builder’s uid.

## Build Packages with Separate User Accounts

When building software, which you have not conducted a full security-audit on, protect sensitive data, such as your GPG private key, in a separate user account.

The same applies to reviewers/testers. Rebuild src.rpms in a separate account which does not have access to any sensitive data.

## Relocatable Packages

The use of RPM’s facility for generating relocatable packages is strongly discouraged. It is difficult to make work properly, impossible to use from the installer or from yum, and not generally necessary if other packaging guidelines are followed. However, in the unlikely event that you have a good reason to make a package relocatable, you MUST state this intent and reasoning in the request for package review.

## File and Directory Ownership

Your package should own all of the files that are installed as part of the %install process.

In most cases, it should not be necessary for multiple packages to contain identical copies of the same file. However, if it is necessary, multiple packages may contain identical copies of the same file, as long as the following requirements are met:

- The packages sharing ownership of the identical files are built from a single SRPM.

OR

- The packages sharing ownership of the identical files are not in a dependency chain (e.g. if package A requires package B, they should not both contain identical files, either A or B must own the common files, but not both.)

In addition, identical files are defined as files which are always identical in content, checksum, permissions, and location on the filesystem in each package.

One notable type of file that is often shared identically between subpackages is the license text. There are certain situations where it is required to duplicate the license text across multiple %files section within a package. For more details, please refer to [Subpackage Licensing](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/#subpackage-licensing).

Directory ownership is a little more complex than file ownership. Packages must own all directories they put files in, except for:

- any directories owned by the `filesystem`, `man`, or other explicitly created `-filesystem` packages
- any directories owned by other packages in your package’s natural dependency chain

In this context, a package’s "natural dependency chain" is defined as the set of packages necessary for that package to function normally. To be specific, you do not need to require a package for the sole fact that it happens to own a directory that your package places files in. If your package already requires that package for other reasons, then your package should not also own that directory.

In all cases we are guarding against unowned directories being present on a system. Please see [Packaging:UnownedDirectories](https://docs.fedoraproject.org/en-US/packaging-guidelines/UnownedDirectories/) for the details.

|  | When co-owning directories, you **must** ensure that the ownership and permissions on the directory match in all packages that own it. |
| --- | --- |

Here are examples that describe how to handle most cases of directory ownership.

### The directory is wholly contained in your package, or involves core functionality of your package

An example:

```
gnucash places many files under the /usr/share/gnucash directory
```

### The directory is also owned by a package implementing required functionality of your package

An example:

```
pam owns the /etc/pam.d directory
gdm places files into /etc/pam.d
gdm depends on pam to function normally, and would Require: pam (either implicitly or explicitly) separate from the directory ownership.
```

Solution: the `pam` package should own the `/etc/pam.d` directory, and `gdm` should `Require:` the `pam` package.

### The directory is owned by a package which is not required for your package to function

Some packages create and own directories with the intention of permitting other packages to store appropriate files, but those other packages do not need that original package to be present to function properly.

An example:

```
gtk-doc owns the /usr/share/gtk-doc/ directory
evolution puts files into /usr/share/gtk-doc/
evolution does not need gtk-doc in order to function properly.
Nothing in evolution's dependency chain owns /usr/share/gtk-doc/
```

Solution: the `evolution` package should own the `/usr/share/gtk-doc` directory. There is no need to add an explicit Requires on gtk-doc solely for the directory ownership.

Sometimes, it may be preferable for such directories to be owned by an "artificial filesystem" package, such as `mozilla-filesystem`. These packages are designed to be explicitly required when other packages store files in their directories, thus, in such situations, these packages should explicitly Require the artificial filesystem package and not multiply own those directories. Packagers should consider the number of affected directories and packages when determining whether to create artificial filesystem packages, and use their own best judgement to determine if this is necessary or not.

|  | **Rule of Thumb**: When determining whether this exception applies, packagers and reviewers should ask this question: Do the files in this common directory enhance or add functionality to another package, where that other package is not necessary to be present for the primary functionality of this package? |
| --- | --- |

### The package you depend on to provide a directory may choose to own a different directory in a later version and your package will run unmodified with that later version

An example involving Perl modules:

Assume `perl-A-B` depends on `perl-A` and installs files into /usr/lib/perl5/vendor\_perl/5.8.8/i386-linux-thread-multi/A/B. The base Perl package guarantees that it will own /usr/lib/perl5/vendor\_perl/5.8.8/i386-linux-thread-multi for as long as it remains compatible with version 5.8.8, but a future upgrade of the `perl-A` package may install into (and thus own) /usr/lib/perl5/vendor\_perl/5.9.0/i386-linux-thread-multi/A. So the `perl-A-B` package needs to own /usr/lib/perl5/vendor\_perl/5.8.8/i386-linux-thread-multi/A as well as /usr/lib/perl5/vendor\_perl/5.8.8/i386-linux-thread-multi/A/B in order to maintain proper ownership.

### File Permissions

Permissions on files MUST be set properly. Inside of /usr, files should be owned by root:root unless a more specific user or group is needed for security. They MUST be universally readable (and executable if appropriate). Outside of /usr, non-config and non-state files SHOULD be owned by root:root, universally readable (and executable if appropriate) unless circumstances require otherwise.

The default file mode is 0644 or 0755. Directories should be mode 0755. Most well behaved build scripts and rpm will use these defaults. If the directory needs to be group writable, it SHOULD also have the setgid bit set so that files written there are owned by that group. These directories SHOULD have mode 2775.

The %defattr directive in the %files list SHOULD ONLY be used when setting a non-default value, or to reset to the default value after having set a non-default value.

### Explicit lists

Packagers **SHOULD NOT** simply glob everything under a shared directory.

In particular, the following **SHOULD NOT** be used in `%files`:

- `%{_bindir}/*`
- `%{_datadir}/*`
- `%{_includedir}/*`
- `%{_mandir}/*`
- `%{_docdir}/*`

This rule serves as a check against common mistakes which are otherwise hard to detect. It does limit some possibilities for automation.

The most common mistake this rule prevents is upstream adding new commands in `%{_bindir}/*`. You should always check such changes for [conflicts](https://docs.fedoraproject.org/en-US/packaging-guidelines/Conflicts/#_common_conflicting_files_cases_and_solutions), and keep the list of such files explicit and auditable.

## Users and Groups

Some packages require or benefit from dedicated runtime user and/or group accounts. Guidelines for handling these cases are in a [separate document](https://docs.fedoraproject.org/en-US/packaging-guidelines/UsersAndGroups/).

Note that system services packaged for Fedora MUST NOT run as the `nobody` user, but MUST instead allocate their own system user.

## Web Applications

Web applications packaged in Fedora should put their content into /usr/share/%{name} and NOT into /var/www/. This is done because:

- /var is supposed to contain variable data files and logs. /usr/share is much more appropriate for this.
- Many users already have content in /var/www, and we do not want any Fedora package to step on top of that.
- /var/www is no longer specified by the Filesystem Hierarchy Standard

## Conflicts

Whenever possible, Fedora packages should avoid conflicting with each other. Unfortunately, this is not always possible. For full details on Fedora’s Conflicts policy, see: [Conflicts](https://docs.fedoraproject.org/en-US/packaging-guidelines/Conflicts/).

Tools such as Alternatives and Environment Modules can also help prevent package conflicts.

### Alternatives

The "alternatives" tool provides a means for parallel installation of packages which provide the same functionality by maintaining sets of symlinks. For full details on how to properly use alternatives, see [Alternatives](https://docs.fedoraproject.org/en-US/packaging-guidelines/Alternatives/).

### Environment Modules

When there are multiple variants that each serve the needs of some user and thus must be available simultaneously by users, the alternatives system simply isn’t enough since it is system-wide. In such situations, use of Environment Modules can avoid conflicts. For full details on how to properly use Environment Modules, see [Environment Modules](https://docs.fedoraproject.org/en-US/packaging-guidelines/EnvironmentModules/).

## Patch Guidelines

### All patches should have an upstream bug link or comment

All patches in Fedora spec files **SHOULD** have a comment above them about their upstream status. Any time you create a patch, it is best practice to file it in an upstream bug tracker, and include a link to that in the comment above the patch. For example:

```rpm-spec
# https://bugzilla.gnome.org/show_bug.cgi?id=12345
Patch: gnome-panel-fix-frobnicator.patch
```

The above is perfectly acceptable; but if you prefer, a brief comment about what the patch does above can be helpful:

```rpm-spec
# Don't crash with frobnicator applet
# https://bugzilla.gnome.org/show_bug.cgi?id=12345
Patch: gnome-panel-fix-frobnicator.patch
```

Sending patches upstream and adding this comment will help ensure that Fedora is acting as a good FLOSS citizen ([Staying Close to Upstream Projects](https://docs.fedoraproject.org/en-US/package-maintainers/Staying_Close_to_Upstream_Projects/)). It will help others (and even you) down the line in package maintenance by knowing what patches are likely to appear in a new upstream release.

#### If upstream doesn’t have a bug tracker

You can indicate that you have sent the patch upstream and any known status:

```rpm-spec
# Sent upstream via email 20080407
Patch: foobar-fix-the-bar.patch
```

```rpm-spec
# Upstream has applied this in SVN trunk
Patch: foobar-fix-the-baz.patch
```

#### Fedora-specific (or rejected upstream) patches

It may be that some patches truly are Fedora-specific; in that case, say so:

```rpm-spec
# This patch is temporary until we land the long term System.loadLibrary fix in OpenJDK
Patch: jna-jni-path.patch
```

### Applying Patches

Normally, patches to a package SHOULD be listed in `PatchN:` tags in the RPM spec file and applied using the %patch or %autosetup macros. The files MUST then be checked into the Fedora Package revision control system (currently the git repos on pkgs.fedoraproject.org and commonly accessed via fedpkg). Storing the files in this way allows people to use standard tools to visualize the changes between revisions of the files and track additions and removals without a layer of indirection (as putting them into lookaside would do).

Applying patches directly from RPM\_SOURCE\_DIR IS NOT ALLOWED. Please see [Packaging:RPM\_Source\_Dir](https://docs.fedoraproject.org/en-US/packaging-guidelines/RPM_Source_Dir/) for the complete rationale.

The maintainer MAY deviate from this rule when the upstream of the package provides an extremely large patch or a tarball of patches against a base release. In this case the tarball of patches MAY be listed as a `SourceN:` line and the patches would be applied by untarring the archive and then applying the distributed patch(es) using the regular /usr/bin/patch command. Additional patches to the package (for instance, generated by the Fedora maintainer to fix bugs) MUST still be listed in `PatchN:` lines and be applied by %patch macros after the patches from the tarball were applied. Maintainers and reviewers should be cautious when exercising this exception as shipping an update as a patchset may be a sign that the patchset is not from the actual upstream or that the patches should be reviewed for correctness rather than simply accepted as the upstream code base.

## Use of Epochs

RPM supports a field called "Epoch:", which is a numeric field, that, if set, adds another qualifier for RPM to use in doing package comparisons. Specifically, if set, the Epoch of a package trumps all other comparisons (except for a larger Epoch). If Epoch is not set in a package, RPM treats it the same as if it was set to 0.

Example:

```rpm-spec
Version: 1.2
Release: 3%{?dist}
Epoch: 1
```

A package with those definitions would be considered greater than a package with a higher version or a higher release. Since Epoch is confusing to humans (and can never be removed from a package once used), it should only be used in Fedora **as a last resort** to resolve upgrade ordering of a package, and should be avoided wherever possible.

Also, Epoch complicates normal packaging guidelines. If a package uses an Epoch, it must be referred to in any place where `%{version}-%{release}` is used. For example, if a package being depended upon has an Epoch, this must be listed when adding a versioned dependency:

```rpm-spec
Requires: foo = %{epoch}:%{version}-%{release}
```

### Epochs from Third Party Repositories

If a package to be imported is or previously was present in a publicly accessible repository, the packager can optionally include an Epoch tag equal to that of the most recent version of the third-party package.

## Symlinks

There are two ways of making a symlink, either as a relative link or an absolute link. In Fedora, neither method is required. Packagers should use their best judgement when deciding which method of symlink creation is appropriate.

### Relative Symlinks

A relative symlink is a symlink which points to a file or directory relative to the position of the symlink. For example, this command would create a relative symlink:

```
ln -s ../..%{_bindir}/foo %{buildroot}%{_bindir}/bar
```

Pros:

- Relative symlinks will point to the same file inside or outside of a chroot.

Cons:

- Much more complicated to create than absolute symlinks
- Relative symlinks may break or behave unexpectedly when a part of a filesystem is mounted to a custom location.
- Relative symlinks may break when bind mounting or symlinking directories.
- Relative symlinks may make it more difficult to use rpm system macros.

### Absolute Symlinks

An absolute symlink is a symlink which points to an absolute file or directory path. For example, this command would create an absolute symlink:

```
ln -s %{_bindir}/foo %{buildroot}%{_bindir}/bar
```

Pros:

- Much easier to create than relative symlinks.
- Absolute symlinks work properly when bind mounting or symlinking directories.
- Absolute symlinks work well with rpm system macros.

Cons:

- Absolute symlinks may break when used with chroots.

## Replacing a Symlink to a Directory or a Directory to Any Type File

In some cases replacing a symlink to a directory requires special handling. Replacing a directory with any type of file always requires special handling.

See [Packaging:Directory\_Replacement](https://docs.fedoraproject.org/en-US/packaging-guidelines/Directory_Replacement/) for information about doing this.

## Test Suites

If the source code of the package provides a test suite, it should be executed in the `%check` section, whenever it is practical to do so.

## tmpfiles.d

There are specific guidelines for handling tmpfiles.d configurations and directories (in /run and /run/lock): [Tmpfiles.d](https://docs.fedoraproject.org/en-US/packaging-guidelines/Tmpfiles.d/).

## Renaming/Replacing or Removing Existing Packages

|  | [Package Renaming Process](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Renaming_Process/) should be followed when renaming an existing package. |
| --- | --- |

In the event that it becomes necessary to rename or replace an existing package, the new package should make the change transparent to end users to the extent applicable.

If a package is being renamed without any functional changes, or is a compatible-enough replacement to an existing package (where "enough" means that it includes only changes of magnitude that are commonly found in version upgrade changes), provide clean upgrade paths and compatibility with:

```rpm-spec
Provides: oldpackagename = $provEVR
Obsoletes: oldpackagename < $obsEVR
```

$provEVR refers to an (Epoch-)Version-Release tuple the original unchanged package would have had if it had been version or release bumped. You usually use macros here because the provides EVR should continue to go up as the renamed package advances in version and release. $obsEVR is an (Epoch-)Version-Release tuple arranged so that there is a clean upgrade path but without gratuitously polluting the version space upwards. You usually do not use macros for this as you’re simply trying to advance beyond the last known release under the old name.

If a package supersedes/replaces an existing package without being a sufficiently compatible replacement as defined above, use only the `Obsoletes:` line from the above example.

|  | **Take `%{?dist}` into account**: When deciding what $obsEVR should be, remember that it needs to be higher than the previous `Release:`, including the `%{?dist}` suffix. Example: if the package previously had the release tag of `-4.fcNN`, the release specified in $obsEVR should be at least 5. |
| --- | --- |

|  | If the replaced package uses `rpmautospec`, either look at the built package (e.g. in koji) to find the actual release tag of the latest build, or use `rpmautospec calculate-release` to calculate just the release number. |
| --- | --- |

If retired packages need to be removed from end user machines because they cause dependency issues which interfere with upgrades or are otherwise harmful, a packager SHOULD request that `Obsoletes:` be added to `fedora-obsolete-packages`. Simply file a bugzilla ticket [here](https://bugzilla.redhat.com/enter_bug.cgi?product=Fedora&version=rawhide&component=fedora-obsolete-packages). Please include information on which packages need to be obsoleted, the exact versions which need to be obsoleted, and the reasons why they cannot be allowed to remain installed.

If the obsoleted package had an Epoch set, it must be preserved in both the `Provides:` and `Obsoletes:`. For example, assume foo being renamed to bar, bar is compatible with foo, and the last foo package release being `foo-1.0-3.fcNN` with `Epoch: 2`. The following should be added to bar (and similarly for all subpackages as applicable):

```rpm-spec
Provides: foo = 2:%{version}-%{release}
# Important: We set the Obsoletes release to 4 to be higher than the last build of foo
Obsoletes: foo < 2:1.0-4
```

Explicit `Provides:` need to be aware of whether the package is supplying things that can be used in an arch-independent or arch-specific fashion. For packages that are not noarch, `Provides:` should be made arch-specific by applying the `%{?_isa}` macro to the end of the text string in Provides (e.g. `Provides: foo%{?_isa} = 2:%{version}-%{release}`). Packages that explicitly provide things that can be used in an arch-independent way (for example, those whose dependents don’t need to be of the same arch) need not apply this macro. In some cases, a package will supply multiple elements, some of which may be consumed only by dependents of an identical arch and some which may be consumed by dependents of any arch. In such cases, both arch-specific and arch-independent Provides: are warranted.

Examples of packages that should explicitly provide only arch-specific `Provides:` include native code libraries or plug-ins and their associated -devel packages. Packages that should explicitly provide only arch-independent `Provides:` include most stand-alone programs (in addition to all noarch packages). Even though these programs may themselves be arch-specific, clients that run them should not care about their arch in most cases. A package that explicitly provides, for example, both a native code library as well as an interpreted language interface to that library should have both arch-specific (for clients of the native code library) and arch-independent (for clients of the interpreted language interface) Provides:.

If there is no standard naming for a package or other long term naming compatibility requirements involved with the rename, the Provides should be assumed to be deprecated and short lived and removed in the distro release after the next one (i.e., if introduced in FC-X, keep in all subsequent package revisions for distros FC-X and FC-(X+1), drop in FC-(X+2)), and the distro version where it is planned to be dropped documented in a comment in the specfile. Maintainers of affected packages should be notified and encouraged to switch to use the new name. Forward compatibility Provides: in older distro branches can be considered in order to make it possible for package maintainers to keep same simple specfiles between branches but still switch to the newer name.

For packages that are not usually pulled in by using the package name as the dependency such as library only packages (which are pulled in through library soname depenencies), there’s usually no need to add the Provides. Note however that the -devel subpackages of lib packages are pulled in as build dependencies using the package name, so adding the Provides is often appropriate there.

### One-to-Many Replacement

Sometimes a package is split into two or more packages (either subpackages or separate source packages) to make some components optional, but users of the optional parts shall be able to upgrade without losing the functionality. Thus the new packages need to be pulled in on upgrade from a version before the split. If some are later removed, they shall not be pulled in again on further upgrades.

This is achieved by putting an `Obsoletes:` tag like above in each of the packages that together replace the original package. If the name of the original package still exists after the split, that package needs to obsolete itself. Even if an optional split-out package requires the original package, the original package still must obsolete itself. Otherwise the split-out package won’t be pulled in.

Example: Foo version 3 contains Bar as a non-essential component. In version 4, Bar is moved to a subpackage. Bar shall not disappear on upgrade.

```rpm-spec
Name:      foo
Version:   4
Release:   1%{?dist}
Obsoletes: foo < 4

%package bar
Requires:  foo%{?_isa} = %{version}-%{release}
Obsoletes: foo < 4
```

|  | Packages pulled in this way are not marked as user-installed by DNF 4, so `dnf autoremove` will remove them. This appears to be fixed in DNF 5. |
| --- | --- |

## Deprecating Packages

A procedure exists for indicating that a package is deprecated and may leave the distribution in the future. See [Deprecating Packages](https://docs.fedoraproject.org/en-US/packaging-guidelines/deprecating-packages/).

## Networking Support

If an application contains native and stable support for both IPv4 and IPv6, and support for IPv6 does not negatively affect IPv4 then both MUST be enabled in the Fedora package.

## Cron Files

For details on how to package cron files, refer to: [CronFiles](https://docs.fedoraproject.org/en-US/packaging-guidelines/CronFiles/).

## Security Updates to Resolve Known CVE Issues

If an update to your package resolves a known security concern (at the time of the update) with a Common Vulnerabilities and Exposures (CVE) number assigned to it, you should mention the CVE number in the RPM changelog entry.

## Build Time Network Access

Packages in the Fedora buildsystem are built in a mock chroot with no access to the internet. Packages must not depend or or use any network resources that they don’t themselves create (i.e., for tests). In no cases should source code be downloaded from any external sources, only from the lookaside cache and/or the Fedora git repository.

## Bootstrapping

If your package introduces build time circular dependencies, you should use this macro to bootstrap your package:

```rpm-spec
# When we are bootstrapping, we drop some dependencies, and/or build time tests.
%bcond_with bootstrap

[...]

%if %{without bootstrap}
# dependencies for %%check
BuildRequires: foo
%endif

[...]

%if %{without bootstrap}
%check
make check
%endif
```

|  | Since Fedora 30, as a nice side-effect, when bootstrapping mode is enabled, the `~bootstrap` suffix is appended to the dist tag. This avoids the need to bump release between bootstrap and final build. You can temporarily enable bootstrapping by commit, which changes `%bcond_with bootstrap` to `%bcond_without bootstrap` and later reverting the commit to do final build. |
| --- | --- |

|  | Since Fedora 31, you can disable the automatic suffix addition by specifying `%global __bootstrap %{nil}` in your spec file. |
| --- | --- |

If your package explicitly `Provides:` some functionality that is missing when bootstrapped, then that `Provides:` should look like:

```rpm-spec
%if %{without bootstrap}
Provides: bar(some_functionality)
%endif
```

Please note that usage of pre-built binaries in bootstrap still needs an exception from the Packaging Committee as stated in [General Exception Policy](#_general_exception_policy).

## System Cryptographic Policies

Applications which make use the SSL or TLS cryptographic protocols MUST follow [Crypto Policies](https://docs.fedoraproject.org/en-US/packaging-guidelines/CryptoPolicies/).

## Shebang Lines

When packaging script files, where the interpreter to be used is specified in the first line of the script (the shebang line) following `#!`, the following rules apply:

- `env`, `/bin/env` and `/usr/bin/env` MUST NOT be used. The interpreter used to run packaged applications cannot depend upon what the user has in their personal `$PATH`.
- Files which are not installed as executables SHOULD NOT have shebang lines.
- Language-specific guidelines may have additional restrictions.

Shebang lines for executable scripts are automatically modified to convert calls to `env` into direct use of the proper executable in `/usr/bin`. Various checks are also applied to verify that the shebang lines are valid, and the build process can fail as a result of these. Finally, other language-specific modifications may also be made. It is thus generally unnecessary to manually modify executable scripts to fix `env` usage as long as this functionality is enabled.

If the automatic checks and modifications break a package, there are two primary options:

- The packager can elect to fix the shebang lines manually (using patches, scripting via sed, or other similar methods).
- The packager can remove the executable permission from the script so that the checks and modifications are not made.

If (and only if) the script needs to remain executable and cannot be modified to pass the checks, then the maintainer MAY elect to disable the checks and modifications. It is also possible to disable the functionality for specific paths or for specific shebang lines by setting `%__brp_mangle_shebangs_exclude_from` and `%__brp_mangle_shebangs_exclude`, respectively, using the same syntax as the settings described in [Packaging:AutoProvidesAndRequiresFiltering](https://docs.fedoraproject.org/en-US/packaging-guidelines/AutoProvidesAndRequiresFiltering/). It is also possible to disable the functionality entirely by adding `%undefine __brp_mangle_shebangs` near the beginning of the specfile.

## BRP (BuildRoot Policy) Scripts

BRP scripts are injected at the end of `%install` (via the `%__os_install_post` macro) and perform some automatic sanity checks of, or adjustments to, files installed in the build root.

All packages SHOULD always be subject to all the BRP scripts, but sometimes it is necessary for a package to opt-out of certain ones. It is possible to disable any BRP script simply by defining the corresponding variable to `%{nil}`. For example, to disable the `brp-python-bytecompile` script:

```rpm-spec
# Turn off Python bytecode compilation because this is a Jython
# package and we will generate JVM bytecode instead
%global __brp_python_bytecompile %{nil}
```

Any package that disables a BRP script this way MUST also note the reason in an accompanying comment. For a list of the BRP scripts run by default, invoke:

```
sed -r -n '/^%.?__os_install_post/,/%.?nil/p' /usr/lib/rpm/redhat/macros
```

For a list of all BRP scripts, invoke:

```
rpmbuild --eval '%dump' |& grep ': __brp_'
```

### Removal of common sources of build irreproducibility

One of the BRP scripts that is invoked by default is `%__os_install_post_build_reproducibility`. Its purpose is to normalize installed files by removing unwanted embedded metadata that is dependent on the build environment and may cause different builds from the same sources to be irreproducible.

See `/usr/lib/rpm/macros.d/macros.build-reproducibility` for details about how it can be configured.

## Packaging for EPEL

For the most part, these guidelines and the application-specific guidelines below cover packaging for both Fedora and EPEL. However, there are necessarily some differences. When packaging for EPEL, please also consult [the EPEL packaging guidelines](https://fedoraproject.org/wiki/EPEL:Packaging) for additional information.

## Domain Specific Guidelines

Some applications, languages and build systems have specific guidelines written for them, located on their own pages:

- [Ada](https://docs.fedoraproject.org/en-US/packaging-guidelines/Ada/)
- [BLAS/LAPACK](https://docs.fedoraproject.org/en-US/packaging-guidelines/BLAS_LAPACK/)
- [C and C++](https://docs.fedoraproject.org/en-US/packaging-guidelines/C_and_C++/)
- [CMake](https://docs.fedoraproject.org/en-US/packaging-guidelines/CMake/)
- [D](https://docs.fedoraproject.org/en-US/packaging-guidelines/D/)
- [Emacs](https://docs.fedoraproject.org/en-US/packaging-guidelines/Emacs/)
- [Fonts](https://docs.fedoraproject.org/en-US/packaging-guidelines/FontsPolicy/)
- [Fortran](https://docs.fedoraproject.org/en-US/packaging-guidelines/Fortran/)
- [GAP](https://docs.fedoraproject.org/en-US/packaging-guidelines/GAP/)
- [Haskell](https://docs.fedoraproject.org/en-US/packaging-guidelines/Haskell/)
- [Java](https://docs.fedoraproject.org/en-US/packaging-guidelines/Java/)
- [JavaScript](https://docs.fedoraproject.org/en-US/packaging-guidelines/JavaScript/)
- [Language packs](https://docs.fedoraproject.org/en-US/packaging-guidelines/Langpacks/)
- [LibreOffice Extensions](https://docs.fedoraproject.org/en-US/packaging-guidelines/LibreOfficeExtensions/)
- [Lisp](https://docs.fedoraproject.org/en-US/packaging-guidelines/Lisp/)
- [Meson](https://docs.fedoraproject.org/en-US/packaging-guidelines/Meson/)
- [MinGW](https://docs.fedoraproject.org/en-US/packaging-guidelines/MinGW/)
- [Mono](https://docs.fedoraproject.org/en-US/packaging-guidelines/Mono/)
- [MPI](https://docs.fedoraproject.org/en-US/packaging-guidelines/MPI/)
- [Node.js](https://docs.fedoraproject.org/en-US/packaging-guidelines/Node.js/)
- [OCaml](https://docs.fedoraproject.org/en-US/packaging-guidelines/OCaml/)
- [Octave](https://docs.fedoraproject.org/en-US/packaging-guidelines/Octave/)
- [Perl](https://docs.fedoraproject.org/en-US/packaging-guidelines/Perl/)
- [PHP](https://docs.fedoraproject.org/en-US/packaging-guidelines/PHP/)
- [Python](https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/)
- [R](https://docs.fedoraproject.org/en-US/packaging-guidelines/R/)
- [Ruby](https://docs.fedoraproject.org/en-US/packaging-guidelines/Ruby/)
- [Rust](https://docs.fedoraproject.org/en-US/packaging-guidelines/Rust/)
- [Sugar activities](https://docs.fedoraproject.org/en-US/packaging-guidelines/SugarActivityGuidelines/)
- [Tcl/Tk extensions](https://docs.fedoraproject.org/en-US/packaging-guidelines/Tcl/)
- [Tree-sitter parsers](https://docs.fedoraproject.org/en-US/packaging-guidelines/Tree-sitter/)
- [Web Assets](https://docs.fedoraproject.org/en-US/packaging-guidelines/Web_Assets/)
- [WordPress extensions](https://docs.fedoraproject.org/en-US/packaging-guidelines/WordPress_plugin_packaging_guidelines/)

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
