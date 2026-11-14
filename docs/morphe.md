# Morphe

[Morphe Desktop](https://github.com/MorpheApp/morphe-desktop) patches Android apps. Install `morphe`, launch Morphe Desktop from the application menu, or run `morphe --help` for CLI usage. The CLI requires a compatible APK and patch bundle; see [upstream's documentation](https://github.com/MorpheApp/morphe-desktop/blob/main/docs/documentation.md). ADB is optional for installation to a device.

The launcher uses `$XDG_DATA_HOME/morphe` (or `~/.local/share/morphe`) by default. Set `MORPHE_DATA_DIR` to override it. On first GUI launch, upstream downloads platform-specific native components into that directory; patch sources may also be downloaded at runtime. These downloads are not managed by RPM. Upstream verifies the GUI components against hashes embedded in the JAR; review upstream's implementation and trust model before use. The system Java runtime is used rather than a bundled JetBrains Runtime; display scaling may differ, as noted in [upstream issue #329](https://github.com/MorpheApp/morphe-desktop/issues/329).

## Sources and build

The RPM builds the desktop application, Morphe patcher and library, and jadb from source, following the [Homebrew formula's](https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/m/morphe.rb) composite-build substitutions. It uses Fedora's [OpenJDK 25 development package](https://packages.fedoraproject.org/pkgs/java-25-openjdk/java-25-openjdk-devel/), available in Fedora 44, 45 and Rawhide, rather than relying on each release's default JDK. Fedora [removed OpenJDK 21 early](https://fedoraproject.org/wiki/Changes/Java21RemovedEarlierThenScheduled). The launcher and runtime dependency select Fedora's OpenJDK 25 explicitly, independent of the system Java alternatives. [Gradle 9.8.2 supports running on Java 25](https://docs.gradle.org/9.8.2/userguide/compatibility.html); remote builds are still needed to verify the full toolchain.

Fedora retired Gradle, so the build uses the prebuilt Gradle distribution pinned by [upstream's wrapper](https://github.com/MorpheApp/morphe-desktop/blob/v2.1.1/gradle/wrapper/gradle-wrapper.properties). Source archives and Gradle are hash-checked during SRPM preparation and `%prep`; a checksum does not independently establish provenance. The RPM build resolves Maven and Gradle dependencies over the network instead of maintaining generated caches in the SRPM. Those inputs can change and include prebuilt components; the JAR bundles libraries. Keep applicable notices and address corresponding-source obligations before distribution. Packit jobs remain disabled; enable networking when configuring a future test build. The revised RPM build has not been verified on Fedora.

## Updates and limitations

Livecheck updates the main release and the shared `checksums.sha256` manifest. Component versions and Gradle remain pinned separately; update them if the new release needs them. Packit jobs remain disabled pending review of corresponding-source obligations.
