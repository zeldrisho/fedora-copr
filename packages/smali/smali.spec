Name:           smali
Version:        3.0.10
Release:        1%{?dist}
Summary:        Assembler and disassembler for Android DEX files
License:        BSD-3-Clause AND Apache-2.0
URL:            https://github.com/google/smali
Source0:        https://github.com/google/smali/archive/refs/tags/%{version}.tar.gz

BuildArch:      noarch
ExclusiveArch:  %{java_arches} noarch
BuildRequires:  javapackages-local-openjdk25
BuildRequires:  antlr3-tool
BuildRequires:  antlr3-java
BuildRequires:  jflex
BuildRequires:  guava
BuildRequires:  beust-jcommander
BuildRequires:  jsr-305
Requires:       java-25-openjdk-headless
Requires:       javapackages-tools
Requires:       antlr3-java
Requires:       guava
Requires:       beust-jcommander

%description
Smali and baksmali assemble and disassemble Android DEX bytecode.

%prep
%autosetup -n %{name}-%{version}
# Do not use the checked-in Gradle wrapper or prebuilt artifacts.
find . -type f \( -name '*.jar' -o -name '*.class' \) -delete

%build
# Use Fedora's JDK and generators rather than upstream's Gradle toolchain.
mkdir -p generated classes
(cd smali/src/main/antlr && antlr3 -o "$OLDPWD/generated" smaliParser.g)
(cd smali/src/main/antlr && antlr3 -lib "$OLDPWD/generated" -o "$OLDPWD/generated" smaliTreeWalker.g)
jflex -d generated smali/src/main/jflex/smaliLexer.jflex
find util/src/main/java dexlib2/src/main/java baksmali/src/main/java smali/src/main/java \
    third_party/util/src/main/java third_party/dexlib2/src/main/java \
    third_party/baksmali/src/main/java third_party/smali/src/main/java generated \
    -name '*.java' > sources.list
javac -encoding UTF-8 -classpath "$(build-classpath guava beust-jcommander jsr-305 antlr3-runtime)" \
    -d classes @sources.list
for app in smali baksmali; do
    printf 'application.version=%%s\n' '%{version}' > "classes/$app.properties"
done
jar --create --file smali.jar -C classes .

%install
install -Dpm 0644 smali.jar %{buildroot}%{_javadir}/smali/smali.jar
# Match the JDK used for compilation instead of the system Java alternative.
%global java_home /usr/lib/jvm/java-25-openjdk
%jpackage_script com.android.tools.smali.smali.Main '' '' 'smali/smali:guava:beust-jcommander:antlr3-runtime' smali
%jpackage_script com.android.tools.smali.baksmali.Main '' '' 'smali/smali:guava:beust-jcommander:antlr3-runtime' baksmali

%check
# Exercise both entry points and a round trip without network access.
export CLASSPATH="$(build-classpath guava beust-jcommander jsr-305 antlr3-runtime):$PWD/smali.jar"
java com.android.tools.smali.smali.Main --version
java com.android.tools.smali.baksmali.Main --version
mkdir -p test-input
printf '.class public LExample;\n.super Ljava/lang/Object;\n\n.method public static main([Ljava/lang/String;)V\n    .registers 1\n    return-void\n.end method\n' > test-input/Example.smali
java com.android.tools.smali.smali.Main assemble test-input -o test.dex
java com.android.tools.smali.baksmali.Main disassemble test.dex -o test-output
grep -F 'LExample;' test-output/Example.smali
grep -F 'main([Ljava/lang/String;)V' test-output/Example.smali
java com.android.tools.smali.smali.Main assemble test-output -o test-roundtrip.dex

%files
%license third_party/NOTICE
%doc README.md AUTHORS
%{_bindir}/smali
%{_bindir}/baksmali
%{_javadir}/smali/

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 3.0.10-1
- Initial package
