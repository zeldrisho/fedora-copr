Name:           kotlin-toolchain
Version:        0.13.0
Release:        1%{?dist}
Summary:        Bootstrap launcher for the Kotlin Toolchain
License:        Apache-2.0
URL:            https://github.com/JetBrains/kotlin-toolchain
Source0:        https://packages.jetbrains.team/maven/p/amper/amper/org/jetbrains/kotlin/kotlin-cli/%{version}/kotlin-cli-%{version}-wrapper
Source1:        https://raw.githubusercontent.com/JetBrains/kotlin-toolchain/v%{version}/LICENSE.txt
Source2:        kotlin.in
Source3:        checksums.sha256

BuildArch:      noarch
BuildRequires:  coreutils
Requires:       java-25-openjdk-headless
Requires:       coreutils curl gzip tar util-linux
Conflicts:      kotlin

%description
A launcher for JetBrains Kotlin Toolchain. On first use the upstream wrapper
downloads and verifies the toolchain distribution into the user's cache. The
downloaded distribution is not included in this package and has separate
license terms. Project builds may download additional dependencies.

%prep
%setup -q -c -T
(cd %{_sourcedir} && sha256sum -c %{SOURCE3})
cp -p %{SOURCE1} LICENSE.txt

%install
install -Dpm 0755 %{SOURCE0} %{buildroot}%{_libexecdir}/%{name}/upstream-wrapper
install -Dpm 0755 %{SOURCE2} %{buildroot}%{_bindir}/kotlin

%check
sh -n %{buildroot}%{_bindir}/kotlin
sh -n %{buildroot}%{_libexecdir}/%{name}/upstream-wrapper
grep -Fx 'kotlin_cli_version=%{version}' %{SOURCE0}
grep -E '^kotlin_cli_sha256=[0-9a-f]{64}$' %{SOURCE0}
# Test the launcher offline with a fixture instead of downloading the toolchain.
printf '#!/bin/sh\nprintf "%%s\\n" "$KOTLIN_CLI_JAVA_HOME" "$@"\n' > fake-wrapper
sed "s|/usr/libexec/kotlin-toolchain/upstream-wrapper|$PWD/fake-wrapper|" %{SOURCE2} > test-launcher
KOTLIN_CLI_JAVA_HOME=/test/java sh test-launcher 'two words' > launcher-output
printf '/test/java\ntwo words\n' > launcher-expected
cmp launcher-expected launcher-output

%files
%license LICENSE.txt
%{_bindir}/kotlin
%{_libexecdir}/%{name}

%changelog
