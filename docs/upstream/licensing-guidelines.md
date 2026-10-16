---
title: "Licensing Guidelines"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/"
author:
published:
created: 2026-10-16
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
## Fedora Licensing

The goal of the Fedora Project is to work with the Linux community to create a complete, general purpose operating system exclusively from free and open source software.

All software in Fedora must be under licenses that have been determined to be [allowed for Fedora](https://docs.fedoraproject.org/en-US/legal/license-approval/). This criteria is based on the licenses approved by the [Free Software Foundation](https://www.gnu.org/philosophy/license-list.html#GPLCompatibleLicenses), [OSI](https://opensource.org/licenses/) and consultation with Red Hat Legal.

For more details on the criteria for allowed and not-allowed licenses, processes related to licensing, or other guidance related to Fedora licensing, see [Licensing in Fedora](https://docs.fedoraproject.org/en-US/legal/).

The information here provides guidance on how to add license text in `%license` and how to populate the `License:` field of spec files for Fedora packages.

## License Text

If the source package includes the text of the license(s) in its own file, then that file, containing the text of the license(s) for the package must be included in the `%files` list flagged with the `%license` directive.

Note that the path so flagged can be either relative or absolute. For relative paths, RPM will automatically copy them from the source directory into a subdirectory of `%_defaultlicensedir` (`/usr/share/licenses`). For absolute paths, RPM will simply tag the file in the final package as being a license file.

Note also that it is acceptable for license files to be so flagged in a list which is generated programmatically and included using `%files -f`. This tagging is often done automatically by macros and not directly visible to the packager. What is important is not the visible presence of the `%license` directive but instead that all relevant license files included in a package appear when using `rpm -q --licensefiles`.

If the source package does not include the text of the license(s), the packager should contact upstream and encourage them to correct this mistake.

In cases where the upstream has chosen a license that requires that a copy of the license text be distributed along with the binaries and/or source code, but does not provide a copy of the license text (in the source tree, or in some rare cases, anywhere), the packager should do their best to point out this confusion to upstream. This sometimes occurs when an upstream project’s only reference to a license is in a README (where they simply say "licensed under the FOO license"), on their website, or when they simply do not check a copy of the license into their Source tree. Packagers should point out to upstream that by not including a proper full license text, they are making it difficult or impossible for anyone to comply with their desired license terms.

However, in situations where upstream is unresponsive, unable, or unwilling to provide proper full license text as part of the source code, and the indicated license requires that the full license text be included, Fedora Packagers must either:

- Include a copy of what they believe the license text is intended to be, as part of the Fedora package in `%license`, in order to remain in compliance. It is worth noting that this may place some additional risk on the packager, however, Fedora believes that this risk is minimized by the fact that if the upstream disagrees with what we have distributed as the full license text, they can easily remedy this by making full license text available in the source code. Packagers who choose to do this should ensure that they have exhausted all attempts to work with upstream to include the license text as part of the source code, or at least, to confirm the full license text explicitly with the upstream, as this minimizes the risk on the packager. Packagers may also take copies of license texts from reliable and canonical sources (such as the original license text from the license steward, Fedora licenses page, the FSF licenses page, or the OSI license list), whenever possible.
- Choose not to package that software for Fedora.

It is important to reiterate that in situations where the indicated license does not imply a requirement that the license be distributed along with the source/binaries, Fedora packagers are NOT required to manually include the full license text when it is absent from the source code, but are still encouraged to point out this issue to upstream and encourage them to remedy it.

### Subpackage Licensing

If a subpackage is dependent (either implicitly or explicitly) upon a base package (where a base package is defined as a resulting binary package from the same source RPM which contains the appropriate license texts as `%license`), it is not necessary for that subpackage to also include those license texts as `%license`.

However, if a subpackage is independent of any base package (it does not require it, either implicitly or explicitly), it must include copies of any license texts (as present in the source) which are applicable to the files contained within the subpackage.

### License Clarification

In cases where the licensing is unclear, it may be necessary to contact the copyright holders to confirm the licensing of code or content. In those situations, it is *always* preferred to ask upstream to resolve the licensing confusion by documenting the licensing and releasing an updated tarball. However, this is not always possible to achieve.

## License: field

Every Fedora package must contain a `License:` entry. Maintainers should be aware that the contents of the `License:` field are understood to not be legally binding (only the source code itself is), but maintainers must make every possible effort to be accurate when filling the `License:` field.

The `License:` field refers to the licenses of the contents of the ***binary*** rpm.

This policy and examples can be found at [License: field in spec file](https://docs.fedoraproject.org/en-US/legal/license-field/).

### Valid License Short Names

The `License:` field for new packages as of July 2022 must be filled with the appropriate SPDX license identifier or expression from the list of [allowed licenses](https://docs.fedoraproject.org/en-US/legal/allowed-licenses/) for Fedora. Note that some licenses may be allowed for only certain types of material, e.g., fonts, content, or documentation.

The [SPDX License List](https://spdx.org/licenses/) provides identifiers for each individual license or exception based on a set of matching guidelines. SPDX license expressions cover situations where multiple licenses apply to a package, where there is a choice of a license, and where licenses are coupled with exceptions or additional permissions.

[License: field in Spec file](https://docs.fedoraproject.org/en-US/legal/license-field/) contains examples and further explanations for using SPDX expressions in the `License:` field.

For more information on what to do if you find a license that is not on the Fedora list, does not have a corresponding SPDX license identifier or expression, or other process questions, see [License Review Process](https://docs.fedoraproject.org/en-US/legal/license-review-process/).

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
