---
title: "Package Review Guidelines"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/ReviewGuidelines/"
author:
published:
created: 2026-10-16
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
This is a set of guidelines for Package Reviews. Note that a complete list of things to check for would be impossible, but every attempt has been made to make this document as comprehensive as possible. Reviewers and contributors (packagers) should use their best judgement whenever items are unclear, and if in doubt, ask on the [Fedora packaging list](https://lists.fedoraproject.org/admin/lists/packaging.lists.fedoraproject.org/).

## Package Review Guidelines

Contributors and reviewers MUST follow the [Package Review Process](https://docs.fedoraproject.org/en-US/package-maintainers/Package_Review_Process/), with the exceptions listed in the next section

## Package Review Exceptions

The following exceptions apply to the review process linked above

- FPC grants an explicit exemption from the process, as indicated [here](https://fedoraproject.org/wiki/Packaging_Committee#Review_Process_Exemption_Procedure).
- The package is being created so that multiple versions of the same package can coexist in the distribution (or coexist between EPEL and RHEL). The package MUST be properly named according to the [naming guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/#_multiple_packages_with_the_same_base_name).
- The package exists in both Fedora and RHEL, but the packager wants to ship it in EPEL under an alternative name (as required by [EPEL policy](https://fedoraproject.org/wiki/EPEL/GuidelinesAndPolicies#Policy)) to provide a subpackage that exists in Fedora but does not exist (or is not shipped) in RHEL.

Exemptions which have been explicitly granted:

- fXX-backgrounds ([ticket](https://pagure.io/packaging-committee/issue/1479)): This package doesn’t follow the usual naming conventions for versioned packages, but a new one is created per Fedora release.

## Relaxed rules for existing components

Some guidelines that apply to "new" packages do not need to be applied when reviewing packages that are only *"added"* to the distribution in the sense that the name of the *source package* is "new" but the component was already available from an existing package, i.e. when

- renaming an existing package,
- moving a subcomponent from an existing package into a separate source package,
- adding an alternative version ("compat package") of an existing package, or
- adding an EPEL-only alternative version of an existing package.

For example, it is allowed for a *"new"* package like this to depend on packages marked as `deprecated()` because no *actually new* component will depend on the deprecated package.

## Things To Check On Review

There are many many things to check for a review. This list is provided to assist new reviewers in identifying areas that they should look for, but is by no means complete. Reviewers should use their own good judgement when reviewing packages. The items listed fall into two categories: **SHOULD** and **MUST**.

- **MUST**: rpmlint must be run on the source rpm and all binary rpms the build produces. The output should be posted in the review. See [Packaging Guidelines: Use rpmlint](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_use_rpmlint).
- **MUST**: The package must be named according to the [Package Naming Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/).
- **MUST**: The spec file name must match the base package `%{name}`, in the format `%{name}.spec` unless your package has an exemption. See [Packaging Guidelines: Spec File Naming](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_spec_file_naming).
- **MUST**: The package must be licensed with a Fedora approved license and meet the [Licensing Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/).
- **MUST**: The License field in the package spec file must match the actual license. See [Licensing Guidelines: Valid License Short Names](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/#_valid_license_short_names).
- **MUST**: If (and only if) the source package includes the text of the license(s) in its own file, then that file, containing the text of the license(s) for the package must be included in `%license`. See [Licensing Guidelines: License Text](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/#_license_text).
- **MUST**: The spec file must be written in American English. See [Packaging Guidelines: Summary and description](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_summary_and_description).
- **MUST**: The spec file for the package **MUST** be legible. See [Packaging Guidelines: Spec Legibility](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_spec_legibility).
- **MUST**: The sources used to build the package must match the upstream source, as provided in the spec URL. Reviewers should use sha256sum for this task as it is used by the `sources` file once imported into git. If no upstream URL can be specified for this package, please see the [Source URL Guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/) for how to deal with this.
- **MUST**: The package **MUST** successfully compile and build into binary rpms on at least one primary architecture. See [Packaging Guidelines: Architecture Support](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_architecture_support).
- **MUST**: If the package does not successfully compile, build or work on an architecture, then those architectures should be listed in the spec in `ExcludeArch`. Each architecture listed in `ExcludeArch` **MUST** have a bug filed in bugzilla, describing the reason that the package does not compile/build/work on that architecture. The bug number **MUST** be placed in a comment, next to the corresponding `ExcludeArch` line. See [Packaging Guidelines: Architecture Build Failures](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_architecture_build_failures).
- **MUST**: All build dependencies must be listed in `BuildRequires`. See [Packaging Guidelines: Build-Time Dependencies (BuildRequires)](https://docs.fedoraproject.org/en-US/packaging-guidelines/#buildrequires).
- **MUST**: The spec file MUST handle locales properly. This is done by using the `%find_lang` macro. Using `%{_datadir}/locale/*` is strictly forbidden. See [Packaging Guidelines: Handling Locale Files](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_handling_locale_files).
- **MUST**: Packages must NOT bundle copies of system libraries. See [Packaging Guidelines: Bundling and Duplication of System Libraries](https://docs.fedoraproject.org/en-US/packaging-guidelines/#bundling).
- **MUST**: If the package is designed to be relocatable, the packager must state this fact in the request for review, along with the rationalization for relocation of that specific package. Without this, use of Prefix: /usr is considered a blocker. See [Packaging Guidelines: Relocatable Packages](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_relocatable_packages).
- **MUST**: A package must own all directories that it creates. If it does not create a directory that it uses, then it should require a package which does create that directory. See [Packaging Guidelines: File And Directory Ownership](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_file_and_directory_ownership).
- **MUST**: A Fedora package must not list a file more than once in the spec file’s %files listings. (Notable exception: license texts in specific situations)See [Packaging Guidelines: Duplicate Files](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_duplicate_files).
- **MUST**: Permissions on files must be set properly. Executables should be set with executable permissions, for example. See [Packaging Guidelines: File Permissions](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_file_permissions).
- **MUST**: Each package must consistently use macros. See [Packaging Guidelines: Macros](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_macros).
- **MUST**: The package must contain code, or permissible content. See [What Can Be Packaged](https://docs.fedoraproject.org/en-US/packaging-guidelines/what-can-be-packaged/).
- **MUST**: Large documentation files must go in a -doc subpackage. (The definition of large is left up to the packager’s best judgement, but is not restricted to size. Large can refer to either size or quantity). See [Packaging Guidelines: Documentation](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_documentation).
- **MUST**: If a package includes something as %doc, it must not affect the runtime of the application. To summarize: If it is in %doc, the program must run properly if it is not present. See [Packaging Guidelines: Documentation](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_documentation).
- **MUST**: Static libraries must be in a -static package. See [Packaging Guidelines: Packaging Static Libraries](https://docs.fedoraproject.org/en-US/packaging-guidelines/#packaging-static-libraries).
- **MUST**: Development files must be in a -devel package. See [Packaging Guidelines: Devel Packages](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_devel_packages).
- **MUST**: In the vast majority of cases, devel packages must require the base package using a fully versioned dependency: `Requires: %{name}%{?_isa} = %{version}-%{release}`. See [Packaging Guidelines: Requiring Base Package](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_requiring_base_package).
- **MUST**: Packages must NOT contain any.la libtool archives, these must be removed in the spec if they are built. See [Packaging Guidelines: Packaging Static Libraries](https://docs.fedoraproject.org/en-US/packaging-guidelines/#packaging-static-libraries).
- **MUST**: Packages containing GUI applications must include a %{name}.desktop file, and that file must be properly installed with `desktop-file-install` in the `%install` section. If you feel that your packaged GUI application does not need a.desktop file, you must put a comment in the spec file with your explanation. See [Packaging Guidelines: Desktop files](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_desktop_files).
- **MUST**: Packages must not own files or directories that are already owned by other packages. The rule of thumb here is that the first package to be installed should own the files or directories that other packages may rely upon. This means, for example, that no package in Fedora should ever share ownership with any of the files or directories owned by the `filesystem` or `man` package. If you feel that you have a good reason to own a file or directory that another package owns, then please present that at package review time. See [Packaging Guidelines: File and Directory Ownership](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_file_and_directory_ownership).
- **MUST**: All filenames in rpm packages must be valid UTF-8. See [Packaging Guidelines: Non-ASCII Filenames](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_non_ascii_filenames).
- **MUST**: Packages being added to the distribution MUST NOT depend on any packages which have been marked as being deprecated. See [Deprecating Packages](https://docs.fedoraproject.org/en-US/packaging-guidelines/deprecating-packages/).

---

- **SHOULD**: If the source package does not include license text(s) as a separate file from upstream, the packager SHOULD query upstream to include it. See [Licensing Guidelines: License Text](https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/#_license_text).
- **SHOULD**: The reviewer should test that the package builds in mock. See [Using Mock to test package builds](https://fedoraproject.org/wiki/Using_Mock_to_test_package_builds).
- **SHOULD**: The package should compile and build into binary rpms on all supported architectures. See [Packaging Guidelines: Architecture Support](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_architecture_support).
- **SHOULD**: Shared libraries should provide versioned symbols (as in "libc.so.6(**GLIBC\_2.41**)(64bit)". Maintainers are encouraged to work with upstream projects that do not yet provide versioned symbols to add them. See [Versioned Symbols](https://docs.fedoraproject.org/en-US/packaging-guidelines/C_and_C++/)
- **SHOULD**: The reviewer should test that the package functions as described. A package should not segfault instead of running, for example.
- **SHOULD**: If scriptlets are used, those scriptlets must be sane. This is vague, and left up to the reviewers judgement to determine sanity. See [Packaging Guidelines: Scriptlets](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_scriptlets).
- **SHOULD**: Usually, subpackages other than devel should require the base package using a fully versioned dependency. See [Packaging Guidelines: Requiring Base Package](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_requiring_base_package).
- **SHOULD**: The placement of pkgconfig(.pc) files depends on their usecase, and this is usually for development purposes, so should be placed in a -devel pkg. A reasonable exception is that the main pkg itself is a devel tool not installed in a user runtime, e.g. gcc or gdb. See [Packaging Guidelines: Pkgconfig Files](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_pkgconfig_files_foo_pc).
- **SHOULD**: Your package should contain man pages for binaries/scripts. If it doesn’t, work with upstream to add them where they make sense. See [Packaging Guidelines: Manpages](https://docs.fedoraproject.org/en-US/packaging-guidelines/#_manpages).

## A note on dependencies

It is often useful to submit a package for review along with its dependencies in separate tickets. As long as the submitter sets up the *Depends on:* and *Blocks:* fields in BugZilla properly, this is not an issue, and it is perfectly possible to review these packages before the full dependency chain is in the distribution (by maintaining a local repository, building and installing the packages locally, or maintaining a COPR).

However, please keep in mind that you cannot do koji builds unless all of the build dependencies are met (because you cannot provide additional dependencies to koji) and when the time comes to build these packages, they must be built in order and you must wait between builds for the dependencies to make it into the appropriate branch of the distribution. This can be automated using side tags and chain builds.

Please also note that while you may actually be able to build a package because all of its build-time dependencies are met, the package may still be non-installable (and thus useless) if its *runtime* dependencies are not met. A package **MUST** not be built if any of its runtime dependencies are unsatisfied.

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
