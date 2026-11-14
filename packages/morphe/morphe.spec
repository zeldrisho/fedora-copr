Name:           morphe
Version:        2.1.1
Release:        2%{?dist}
Summary:        Desktop and command-line Android app patcher

# The source-built JAR bundles dependencies; see its aboutlibraries.json.
# The bundled license inventory has not been independently audited.
License:        GPL-3.0-only AND Apache-2.0 AND BSD-3-Clause AND MIT AND LGPL-2.1-or-later AND LicenseRef-Callaway-BouncyCastle
URL:            https://github.com/MorpheApp/morphe-desktop
Source0:        https://github.com/MorpheApp/morphe-desktop/archive/refs/tags/v%{version}.tar.gz
Source1:        https://github.com/MorpheApp/morphe-patcher/archive/refs/tags/v2.3.0.tar.gz#/morphe-patcher-2.3.0.tar.gz
Source2:        morphe
Source3:        morphe.desktop
Source4:        https://github.com/MorpheApp/morphe-library/archive/refs/tags/v1.4.0.tar.gz#/morphe-library-1.4.0.tar.gz
Source5:        https://github.com/MorpheApp/jadb/archive/refs/tags/v1.2.3.tar.gz#/jadb-1.2.3.tar.gz
Source6:        https://services.gradle.org/distributions/gradle-9.8.2-bin.zip
Source7:        checksums.sha256

BuildArch:      noarch
ExclusiveArch:  x86_64 aarch64 noarch
BuildRequires:  unzip
BuildRequires:  java-25-openjdk-devel
BuildRequires:  maven
BuildRequires:  desktop-file-utils
Requires:       java-25-openjdk

%description
Morphe is a graphical and command-line application for patching Android apps.
This personal COPR package builds a bundled JAR from upstream source.

%prep
(cd %{_sourcedir} && sha256sum -c %{SOURCE7})
%autosetup -n morphe-desktop-%{version}
mkdir morphe-patcher morphe-library jadb
tar -xf %{SOURCE1} -C morphe-patcher --strip-components=1
tar -xf %{SOURCE4} -C morphe-library --strip-components=1
tar -xf %{SOURCE5} -C jadb --strip-components=1
unzip -q %{SOURCE6}
# Follow Homebrew's composite-build substitutions; the versioned system JDK
# avoids Gradle downloading a toolchain and works independently of defaults.
# Fail instead of silently losing these adaptations when upstream changes.
test "$(grep -Fc 'file("../$libraryPath")' settings.gradle.kts)" -eq 1
test "$(grep -Fc 'app.morphe:morphe-library"' settings.gradle.kts)" -eq 1
test "$(grep -Fc 'credentials {' build.gradle.kts)" -eq 1
test "$(grep -Fc 'jvmToolchain(21)' build.gradle.kts)" -eq 1
sed -i 's|file("../$libraryPath")|file("$libraryPath")|; s|app.morphe:morphe-library"|app.morphe:morphe-library-jvm"|' settings.gradle.kts
sed -i 's|credentials {|content { includeGroup("app.morphe") }; credentials {|; s|jvmToolchain(21)||' build.gradle.kts

%build
export HOME="$PWD/build-home"
export JAVA_HOME=/usr/lib/jvm/java-25-openjdk
export PATH="$JAVA_HOME/bin:$PATH"
mkdir -p "$HOME"
export GRADLE_USER_HOME="$HOME/.gradle" JAVA_TOOL_OPTIONS="-Duser.home=$HOME"
# Resolve Maven and Gradle dependencies during the network-enabled RPM build.
(cd jadb && mvn --batch-mode -Dmaven.test.skip=true install)
./gradle-9.8.2/bin/gradle --no-daemon -Pkotlin.jvm.target.validation.mode=ignore shadowJar
unzip -p build/libs/morphe-desktop-%{version}-all.jar aboutlibraries.json > bundled-libraries.json
unzip -p build/libs/morphe-desktop-%{version}-all.jar NOTICE > bundled-NOTICE

%install
install -Dpm 0644 build/libs/morphe-desktop-%{version}-all.jar %{buildroot}%{_libexecdir}/%{name}/morphe.jar
install -Dpm 0755 %{SOURCE2} %{buildroot}%{_bindir}/morphe
install -Dpm 0644 %{SOURCE3} %{buildroot}%{_datadir}/applications/morphe.desktop
install -Dpm 0644 src/main/resources/morphe_logo.png %{buildroot}%{_datadir}/icons/hicolor/200x200/apps/morphe.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/morphe.desktop
export HOME="$PWD/test-home" MORPHE_DATA_DIR="$PWD/test-home/data"
export PATH="/usr/lib/jvm/java-25-openjdk/bin:$PATH"
mkdir -p "$MORPHE_DATA_DIR"
java -jar %{buildroot}%{_libexecdir}/%{name}/morphe.jar --version | grep -F 'v%{version}'
java -jar %{buildroot}%{_libexecdir}/%{name}/morphe.jar --help | grep -F 'list-patches'
mkdir -p "$MORPHE_DATA_DIR/patches"
printf 'cached patch\n' > "$MORPHE_DATA_DIR/patches/stale.mpp"
java -jar %{buildroot}%{_libexecdir}/%{name}/morphe.jar utility clear-cache 2>&1 | grep -F 'Cache cleared'
test ! -e "$MORPHE_DATA_DIR/patches/stale.mpp"

%files
%license LICENSE NOTICE bundled-NOTICE bundled-libraries.json
%doc README.md
%{_bindir}/morphe
%{_libexecdir}/%{name}
%{_datadir}/applications/morphe.desktop
%{_datadir}/icons/hicolor/200x200/apps/morphe.png

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 2.1.1-1
- Initial package
