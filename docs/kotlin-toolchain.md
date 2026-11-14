# Kotlin Toolchain bootstrap

This RPM installs JetBrains' Apache-2.0 [release wrapper](https://packages.jetbrains.team/maven/p/amper/amper/org/jetbrains/kotlin/kotlin-cli/0.13.0/kotlin-cli-0.13.0-wrapper), not the Kotlin Toolchain distribution. The wrapper downloads the distribution on first use to the user's cache, verifies the embedded SHA-256, and runs it. The distribution contains components with separate terms, including proprietary JetBrains Xcode support; users must review the upstream terms. Projects may download additional dependencies and JDKs. This differs from the earlier shared, offline-ready RPM: each user needs network access on first use and maintains a separate cache.

The launcher defaults to Fedora's `/usr/lib/jvm/java-25-openjdk`; `KOTLIN_CLI_JAVA_HOME` overrides it. `KOTLIN_CLI_BOOTSTRAP_CACHE_DIR` selects the cache. The RPM conflicts with Fedora's `kotlin` command. See [upstream provisioning documentation](https://kotlin-toolchain.org/latest/cli/provisioning/) and [KTC-5156](https://youtrack.jetbrains.com/issue/KTC-5156).

## Status and redistribution

The RPM build and SRPM source preparation download only the Apache-licensed wrapper and its license, not the proprietary distribution. The wrapper downloads the distribution at user runtime, not during the build. COPR's [acceptable-use rules](https://docs.copr.fedorainfracloud.org/user_documentation.html#faq) explicitly prohibit proprietary material and downloads during builds; whether a runtime bootstrapper is acceptable remains unconfirmed. **Packit jobs remain disabled until this is clarified.** Previously submitted COPR build 11322139 contained the old distribution as an SRPM input and should be reviewed for removal.

The Fedora 44, 45 and Rawhide builds on x86_64 and aarch64 have not been tested for this new wrapper package. The build check validates wrapper syntax, pinned version and hash, and launcher forwarding using an offline fixture. Passing a previously downloaded release wrapper to `python3 packages/kotlin-toolchain/test-launcher.py /path/to/wrapper` also tests a mock first download, cached operation, and checksum rejection without network access. The real first-run download requires separate testing outside COPR after reviewing the terms.

## Updates and limitations

Livecheck can propose updates to the release wrapper and license checksums in `checksums.sha256`. Review the released wrapper, its embedded version and distribution checksum, and upstream terms before merging. The wrapper at the repository's `v0.13.0` tag points to a development distribution, so use the release artifact rather than assuming the Git tag's wrapper matches. Run `python3 .packit/test-paths.py`, `python3 packages/kotlin-toolchain/test-launcher.py`, and `python3 .github/scripts/livecheck.py --check kotlin-toolchain`. COPR publication eligibility remains unconfirmed.
