---
title: "What can be packaged"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/what-can-be-packaged/"
author:
published:
created: 2026-10-17
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
Not everything can be packaged in Fedora. Most things considered to be "free software" or "open source software" are permitted, but definitions of these are not always consistent and Fedora has a few specific requirements and exceptions. This is an overview of some specific requirements and exceptions, but it is not intended to be exhaustive. If questions arise, the [Packaging Committee](https://fedoraproject.org/wiki/Packaging_Committee) and the [Legal Team](https://fedoraproject.org/wiki/Legal:Main) are the primary places to receive answers.

## Legal Issues

Some software (or in some cases, portions of that software) cannot be packaged for legal reasons. This includes issues related to licensing, patents, trademark law, etc.

See the following pages for various examples.

## Impermissible Content

It is important to make distinction between computer executable code and content. While code is permitted (assuming, of course, that it has an open source compatible license, is not legally questionable, etc.), only some kinds of content are permissible.

The rule is this:

If the content enhances the OS user experience, then the content is OK to be packaged in Fedora. This means, for example, that things like: fonts, themes, clipart, and wallpaper are OK.

Content still has to be reviewed for inclusion. It must have an open source compatible license, must not be legally questionable. In addition, there are several additional restrictions for content:

- Content must not be pornographic, or contain nudity, whether animated, simulated, or photographed. There are better places on the Internet to get porn.
- Content should not be offensive, discriminatory, or derogatory. If you’re not sure if a piece of content is one of these things, it probably is.
- All content is subject to review by FESCo, who has the final say on whether or not it can be included.

Some examples of content which is permissible:

- Package documentation or help files.
- Clipart for use in office suites.
- Background images (non-offensive, discriminatory, with permission to freely redistribute).
- Fonts (under an open source license, with no ownership/legal concerns).
- Game levels are not considered content, since games without levels would be non functional.
- Sound or graphics included with the source tarball that the program or theme uses (or the documentation uses) are acceptable.
- Game music or audio content is permissible, as long as the content is freely distributable without restriction, and the format is not patent encumbered.
- Example files included with the source tarball are not considered content.

Some examples of content which are not permissible:

- Comic book art files
- Religious texts
- Files in patent-encumbered media formats

If you are unsure if something is considered approved content, ask the [Packaging Committee](https://fedoraproject.org/wiki/Packaging_Committee) or, if your question is of a legal nature, [Legal Team](https://fedoraproject.org/wiki/Legal:Main).

## Packages which are not useful without external code

Some software is not functional or useful without the presence of external code dependencies in the runtime operating system environment. When those external code dependencies are non-free, legally unacceptable, or binary-only (with the exception of permissible firmware), then the dependent software is not acceptable for inclusion in Fedora. If the code dependencies are acceptable for Fedora, then they should be packaged and included in Fedora as a pre-requisite for inclusion of the dependent software. Software which downloads code bundles from the internet in order to be functional or useful is not acceptable for inclusion in Fedora (regardless of whether the downloaded code would be acceptable to be packaged in Fedora as a proper dependency).

This also means that packages which are not functional or useful without code or packages from third-party sources are not acceptable for inclusion in Fedora.

## Only one kernel package

Fedora allows only a single kernel package; packages containing alternate kernels are not allowed in the distribution. If there are kernel features which would be generally useful, please communicate with the [Kernel Team](https://fedoraproject.org/wiki/Kernel).

## No external kernel modules

Fedora does not allow kernel modules to be packaged outside of the main kernel package. You should communicate with the [Kernel Team](https://fedoraproject.org/wiki/Kernel) regarding enabling additional kernel modules.

## No inclusion of pre-built binaries or libraries

All program binaries and program libraries included in Fedora packages must be built from the source code that is included in the source package. This is a requirement for the following reasons:

- Security: Pre-packaged program binaries and program libraries not built from the source code could contain parts that are malicious, dangerous, or just broken. Also, these are functionally impossible to patch.
- Compiler Flags: Pre-packaged program binaries and program libraries not built from the source code were probably not compiled with standard Fedora compiler flags for security and optimization.

Content binaries (such as.pdf,.png,.ps files) are *not* required to be rebuilt from the source code.

If you are in doubt as to whether something is considered a program binary or a program library, here is some helpful criteria:

- Is it executable? If so, it is probably a program binary.
- Does it contain a `.so`, `.so.#`, or `.so.#.#.#` extension? If so, it is probably a program library.
- If in doubt, ask your reviewer. If the reviewer is not sure, they should ask the Fedora Packaging Committee.

Packages which require non-open source components to build are also not permitted (e.g. proprietary compiler required).

When you encounter prebuilt binaries in a package you **MUST**:

- Remove all pre-built program binaries and program libraries in %prep prior to the building of the package. Examples include, but are not limited to, `*.class`, `*.dll`, `*.DS_Store`, `*.exe`, `*.jar`, `*.o`, `*.pyc`, `*.pyo`, `*.egg`, `*.so`, `*.swf` files.
- Ask upstream to remove the binaries in their next release.

### Exceptions

- Some software (usually related to compilers or cross-compiler environments) cannot be built without the use of a previous toolchain or development environment (open source). If you have a package which meets this criteria, contact the Fedora Packaging Committee for approval. Please note that this exception, if granted, is limited to only the initial build of the package. You may bootstrap this build with a "bootstrap" pre-built binary, but after this is complete, you must immediately increment Release, drop the "bootstrap" pre-built binary, and build completely from source. Bootstrapped packages containing pre-built "bootstrap" binaries must not be pushed as release packages or updates under any circumstances. These packages should contain the necessary logic to be built once bootstrapping is completed and the prebuilt programs are no longer needed. Information about how you should break circular dependencies by bootstrapping can be found [here](https://docs.fedoraproject.org/en-US/packaging-guidelines/#bootstrapping).
- An exception is made for binary firmware, as long as it meets the requirements documented [here](https://fedoraproject.org/wiki/Licensing:Main#Binary_Firmware).
- Some pre-packaged program binaries or program libraries may be under terms which do not permit redistribution, or be affected by legal scenarios such as patents. In such situations, simply deleting these files in %prep is not sufficient, the maintainer will need to make a modified source that does not contain these files. See: [When Upstream uses Prohibited Code](https://docs.fedoraproject.org/en-US/packaging-guidelines/SourceURL/#when-upstream-uses-prohibited-code).

## Pregenerated code

Often a package will contain code which was itself generated by other code. This often takes the form of configure files or parsing code generated by bison/yacc or lex/flex.

It is required that the original source files from which the code was generated be included in the source package. Generally these files are part of the source archive supplied by upstream, but it may be necessary to fetch those files from an upstream source repository and include them in the source package as separate Source: entries.

It is preferred, but not required, that the tools used to generate such code be free software and included in Fedora.

It is suggested, but not required, that such code be regenerated as part of the build process. The means for doing this are entirely specific to the individual package being built, but it may happen automatically if the necessary dependencies are present at build time.

Want to help? [Learn how to contribute to Fedora Docs ›](https://docs.fedoraproject.org/en-US/fedora-docs/contributing/)
