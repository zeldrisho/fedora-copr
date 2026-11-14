# Smali packaging (experimental)

## Status

Smali's Packit PR job covers Rawhide, Fedora 45, and Fedora 44 on x86_64 and aarch64, with RPM build networking disabled. PR builds run automatically. A main-branch job publishes to the personal COPR. The spec requires Java 25 and defaults its launchers to that runtime to match the build. [PR #1](https://github.com/zeldrisho/fedora-copr/pull/1/checks) passed on all six targets; installation still needs testing.

## Sources and build

The package builds the [Google fork](https://github.com/google/smali) from the 3.0.10 tag, rather than the older `org.jf` upstream. It verifies the source archive during SRPM preparation. The package provides the `smali` and `baksmali` commands; its JAR is application-private, not a published Maven library.

Upstream's [build instructions](https://github.com/google/smali/tree/3.0.10#building-and-testing) specify JDK 11 and Gradle. This recipe instead uses Fedora's system JDK, ANTLR 3, JFlex and Java dependencies directly, without the Gradle wrapper or downloaded JARs. Fedora provides JCommander under the name [`beust-jcommander`](https://packages.fedoraproject.org/pkgs/beust-jcommander/beust-jcommander/), and provides the ANTLR runtime as `antlr3-java`. COPR build 11322138 failed because the unversioned `javapackages-local` is unavailable on all six targets; the recipe now selects `javapackages-local-openjdk25`, following Fedora's [JDK 25 transition guidance](https://fedoraproject.org/wiki/Changes/Java25AndNoMoreSystemJdk). The direct build and its RPM check passed on all six PR targets. The check exercises a DEX assembly/disassembly round trip; upstream's full Gradle test suite is not run.

The upstream [LICENSE](https://github.com/google/smali/blob/3.0.10/LICENSE) covers BSD-3-Clause and Apache-2.0 material. Fedora's [Java packaging guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/Java/) and [Java Packaging HOWTO](https://docs.fedoraproject.org/en-US/java-packaging-howto/) informed the use of system JARs and launcher scripts. The historical [Arch recipe](https://raw.githubusercontent.com/archlinux/svntogit-community/packages/smali/trunk/PKGBUILD) packages the older fork with Gradle and bundled fat JARs; this adaptation does neither.

## Updates and limitations

Upstream tags can be newer than its GitHub latest release: at the time of writing the latest release API reports 3.0.6 while tag 3.0.10 exists. The repository's release-based update automation will not detect newer tags until upstream publishes a corresponding release; check tags manually.
