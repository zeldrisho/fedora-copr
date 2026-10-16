---
title: "Naming Guidelines"
source: "https://docs.fedoraproject.org/en-US/packaging-guidelines/Naming/"
author:
published:
created: 2026-10-16
description: "Learn more about Fedora Linux, the Fedora Project & the Fedora Community."
tags:
  - "clippings"
---
|  | Versioning guidelines have moved  This document previously contained information on both naming and versioning. The versioning guidelines are now at [Packaging:Versioning](https://docs.fedoraproject.org/en-US/packaging-guidelines/Versioning/). |
| --- | --- |

## Common Character Set for Package Naming

While Fedora is an international community, for consistency and usability, there needs to be a common character set for package naming.

Specifically, all Fedora packages must be named using only the following ASCII characters. These characters are displayed here:

```
abcdefghijklmnopqrstuvwxyz
ABCDEFGHIJKLMNOPQRSTUVWXYZ
0123456789-._+
```

But do check [Separators](#separators) for additional restrictions on using the `-._+` characters.

### General Naming

Package names SHOULD be in lower case and use dashes in preference to underscores. You can take some cues from the name of the upstream tarball, the project name from which this software came, and the name which has been used for this package by other distributions/packagers in the past. You can also request guidance from the upstream developers. Do not just blindly follow those examples, however, as package names SHOULD strive to be consistent within Fedora more than consistent between distributions.

Additionally, it is possible that the upstream name does not fall into the [Common Character Set for Package Naming](#common-character-set-for-package-naming). If this is the case, refer to: [When Upstream Naming is outside of the specified character set](#when-upstream-naming-is-outside-of-the-specified-character-set).

Also remember to check whether the type of package you are packaging has specific rules for naming. [Font Packages](#font-packages) and the various sorts of [Addon Packages](#addon-packages), for instance.

### Separators

When naming packages for Fedora, the maintainer MUST use the dash `-` as the delimiter for name parts. The maintainer MUST NOT use an underscore `_`, a plus `+`, or a period `.` as a delimiter. Version numbers used in compat libraries do not need to omit the dot `.` or change it into a dash `-` (see [Multiple packages with the same base name](#multiple-packages-with-the-same-base-name) for more info on this case).

There are a few exceptions to the no underscore `_` rule:

- httpd, pam, and SDL addon packages are excluded, refer to “ [Addon Packages (httpd, pam, and SDL)](#httpd-pam-and-sdl) ”.
- packages that are locale specific, and use the locale in the name are excluded, refer to “ [Addon Packages (locales)](#locales) ”.
- Compat packages where the base package name ends in a digit, refer to “ [Multiple packages with the same base name](#multiple-packages-with-the-same-base-name) ”.
- packages where the upstream name naturally contains an underscore are excluded from this. Examples of these packages include:
	```
	arptables_jf
	dhcpv6_client
	java_cup
	knm_new
	libart_lgpl
	lm_sensors
	microcode_ctl
	nss_db
	nss_ldap
	sg3_utils
	tcp_wrappers
	```

If in doubt, ask on [devel@lists.fedoraproject.org](mailto:devel@lists.fedoraproject.org).

### When Upstream Naming is outside of the specified character set

Fedora recognizes that the task of converting text to the specified ASCII character set (aka transliteration) is difficult. Accordingly, when the upstream name is outside of the specified ASCII character set, the Fedora package maintainer SHOULD first contact the upstream for that software and ask them for a transliteration of the name for Fedora to use.

If (and only if) the upstream is unable, unwilling, or unavailable to provide a transliterated name, the Fedora packager must choose to either perform their own transliteration, or withdraw the package from consideration in Fedora.

When deciding how to transliterate a package name, the Fedora packager SHOULD look to see what (if any) other distributions have done for that package’s name, and take that into account.

### Extra Provides

Transliterated packages MAY Provide: the original, non-transliterated name, but are not required to do so.

## Conflicting Package Names

Conflicting package names, even if they differ by case alone, are not allowed. Please see [Packaging:Conflicts#Conflicting Package Names](https://docs.fedoraproject.org/en-US/packaging-guidelines/Conflicts/#_conflicting_package_names) for more details.

## Multiple packages with the same base name

For many reasons, it is sometimes advantageous to keep multiple versions of a package in Fedora to be installed simultaneously. When doing so, the package name MUST reflect this fact. One package SHOULD use the base name (with no version information). All other packages derived from it MUST include the base name suffixed by either:

- The package version, which SHOULD include the periods present in the original version.
	- If the base package name ends with a digit, a single underscore (`_`) MUST be appended to the name, and the version MUST be appended to that, in order to avoid confusion over where the name ends and the version begins.
	- If the base package name does not end with a digit, the version MUST be directly appended to the package name with no intervening separator.
- a hyphen (`-`) followed by a descriptive suffix such as "stable" which provides some indication as to the nature of the packaged version.

**Examples:**

- The python-sqlalchemy package occasionally has multiple versions in Fedora for backwards compatibility. The most current version of python-sqlalchemy is named `python-sqlalchemy` and an older supported version is `python-sqlalchemy0.5`. No delimiter is used in this situation.
- The most current version of the v8 package is named `v8`. In order to package version "3.13", the package MUST be named `v8_3.13`.

Please also note that strings such as "-latest" can often become misleading over time if the package (in **all** active Fedora releases) is not kept updated with the latest upstream version.

### Documentation Packages with Embedded OS versioning

Documentation packages (as approved by the Fedora Documentation Project) can be named with the OS version number in the package name to allow parallel installation of multiple versions, in cases where the documentation is specific to a release of Fedora and there is value in having multiple versions simultaneously installed.

## Case Sensitivity

In Fedora packaging, the maintainer uses their best judgement when considering how to name the package. While case sensitivity is not a mandatory requirement, case SHOULD only be used where necessary. Keep in mind to respect the wishes of the upstream maintainers. If they refer to their application as "ORBit", you SHOULD use `ORBit` as the package name, and not `orbit`. However, if they do not express any preference of case, you SHOULD default to lowercase naming.

The exception to this is for perl module packaging. The CPAN Group and Type SHOULD be capitalized in the name, as if they were proper nouns. (Refer to “ [Addon Packages (Perl modules)](#perl-modules) ” for details.)

## Renaming/replacing existing packages

## Documentation Subpackages

Large documentation files SHOULD go in a subpackage. This subpackage must be named with the format: `%{name}-doc`. The definition of large is left up to the packager’s best judgement, but is not restricted to size. Large can refer to either size or quantity of files.

## Font Packages

Packages containing fonts must be named `[foundryname-]projectname[-fontfamilyname]-fonts`, in lowercase.

### Clarifications

1. For Fedora purposes a “foundry” is an entity that publishes a set of fonts with consistent font QA rules. Thus a generic hosting service such as [Sourceforge](http://www.sf.net/) is not a foundry, but the [Open Font Library](http://openfontlibrary.org/) is.
2. It is good practice to contract *foundryname-* in a short prefix.
3. The *foundryname-* prefix can optionally be skipped:
	- for entities that never released more than one font family, or
	- when the font project and the publishing entity are one and the same.
4. If *projectname* or *foundryname* are repeated in *fontfamilyname*, they can be dropped from *fontfamilyname*.
5. When *foundryname*, *projectname* or *fontfamilyname* contain the *font* or *fonts* affix, this affix should be dropped from them <sup>[<a href="#_footnotedef_1" title="View footnote.">1</a>]</sup>.
6. *\-fontfamilyname* should not be included in the srpm name of a package that includes several different font families.
7. If any element of the naming contains spaces, they should be replaced by “-”.
8. The use of the *\-fonts* suffix is not dependant on the actual number of font files in the package.

When in doubt, ask the [mailing list](https://fedoraproject.org/wiki/Fonts_SIG_mailing_lists) for clarification.

## Addon Packages

If a package is considered an "addon" package that enhances or adds functionality to an existing Fedora package without being useful on its own, its name SHOULD reflect this fact.

The new package ("child") SHOULD prepend the "parent" package in its name, in the format: `%{parent}-%{child}`.

**Examples:**

```
gnome-applet-netmon (netmon applet for gnome, relies on gnome)
php-adodb (adodb functionality for php, relies on php)
python3-twisted (the twisted module for python3, relies on python3)
xmms-cdread (direct cd read functionality for xmms, relies on xmms)
```

When the addon package is a language binding, note that the language itself is always the parent. Thus, a lua binding for the "randomdb" database would be `lua-randomdb`, not `randomdb-lua`. Also note that some packages may have grandfathered names using the opposite ordering.

There are some exceptions to this general addon package naming policy, and they are noted below.

### httpd, pam, and SDL

Packages that rely on Apache httpd, pam, or SDL as a parent use a slightly different naming scheme. pam and SDL addons use the format: `%{parent}_%{child}`, with an underscore `_` as a delimiter. Apache httpd addons use the format: `mod_%{child}`, with an underscore `_` as a delimiter. This naming scheme is usually the same as used for the source tarball name.

**Examples:**

```
mod_perl (Perl components for Apache httpd, relies on httpd)
pam_krb5 (krb5 components for pam, relies on pam)
SDL_gfx (Additional graphics components for SDL, relies on SDL)
SDL_ttf (TrueType font rendering support for SDL, relies on SDL)
```

### emacs components

Packages of emacs add-on components (code that adds additional functionality to emacs) SHOULD have a name that takes into account the upstream name of the emacs component by being called `emacs-$NAME`.

**Examples:**

```
emacs-auctex (auctex component for GNU Emacs)
emacs-deferred (deferred component for GNU Emacs)
emacs-flycheck (flycheck component for GNU Emacs)
```

### Erlang modules

Packages of Erlang modules (thus they rely on Erlang as a parent) have their own naming scheme. They SHOULD take into account the upstream name of the Erlang module. This makes a package name format of `erlang-$NAME`. When in doubt, use the name of the module that you use when importing it into a script.

**Example:**

```
erlang-esdl (Erlang module named esdl)
```

### GAP packages

See the [GAP guidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/GAP/#_naming) for the proper naming of GAP addon packages.

### Gnome shell extensions

Packages that extend gnome shell SHOULD begin with the prefix `gnome-shell-extension-`. In particular, this prefix SHOULD NOT be pluralized (i.e., it SHOULD NOT be `gnome-shell-extensions`).

### GStreamer plugins

Packages that extend GStreamer SHOULD begin with the prefix `gstreamer1-plugin-`. In particular, this prefix SHOULD NOT be pluralized (i.e., it SHOULD NOT be `gstreamer1-plugins`) unless it is a collection of plugins (i.e., `gstreamer1-plugins-good`).

### LibreOffice extensions

Packages of LibreOffice extensions (thus they rely on LibreOffice as a parent) have their own naming scheme. They must take into account the upstream name of the LibreOffice extension. This makes a package name format of `libreoffice-$NAME`.

### Locales

If a package adds a locale to an existing parent package, then it can use an underscore in the locale.

**Examples:**

```
ttfonts-zh_TW (adds zh_TW locale fonts in ttfonts family)
ttfonts-zh_CN (adds zh_CN locale fonts in ttfonts family)
```

### Lua modules

It is common that multiple versions of Lua are packaged, and each may have corresponding module packages. Of course the base Lua packages of course MUST follow the relevant [naming guidelines](#multiple-packages-with-the-same-base-name) resulting in package names such as `lua5.1`.

The module packages SHOULD carry the name of the corresponding base Lua package (as mandated by the [relevant guidelines](#multiple-packages-with-the-same-base-name)) as a prefix. Some examples:

| module name | base lua version | package name |
| --- | --- | --- |
| argparse | (default) | `lua-argparse` |
| argparse | 5.1 | `lua5.1-argparse` |
| sql | 5.2 | `lua5.2-sql` |

### NGINX modules

Packages of NGINX modules SHOULD begin with the prefix `nginx-mod-`. In particular, this prefix SHOULD NOT be pluralized (i.e., it SHOULD NOT be `nginx-mods`). Some upstream projects may use `module` as a prefix, and this should be accounted for and replaced accordingly in the package name.

### OBS Studio plugins

Packages of OBS Studio plugins SHOULD begin with the prefix `obs-studio-plugin-`. In particular, this prefix SHOULD NOT be pluralized (i.e., it SHOULD NOT be `obs-studio-plugins`).

### OCaml modules

OCaml modules, libraries and syntax extensions SHOULD be named `ocaml-foo`. Examples include: `ocaml-extlib`, `ocaml-ssl`.

This naming does not apply to applications written in OCaml, which can be given their normal name. Examples include: `mldonkey`, `virt-top`, `cduce`

### Perl modules

Packages of Perl modules (thus they rely on Perl as a parent) use a slightly different naming scheme. They SHOULD be named `perl-CPANDIST` where `CPANDIST` is the name of the packaged CPAN module distribution (which is almost always also the unit of Perl module packaging). In the rare cases when a CPAN module distribution needs to be split into smaller subpackages e.g., due to dependencies, the extra subpackages SHOULD be named `perl-CPANDIST-Something`.

**Examples:**

```
perl-Archive-Zip (Archive-Zip is the CPAN distribution name)
perl-Cache-Cache (Cache-Cache is the CPAN distribution name)
```

### PHP modules

For details on the PHP naming scheme, see [Naming scheme](https://docs.fedoraproject.org/en-US/packaging-guidelines/PHP/#_naming_scheme).

### Python modules

Naming of Python modules is fully covered in the [Naming section](https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#_naming) of the Python Packaging Guidelines.

In short: The package name SHOULD reflect the upstream name of the Python module, and SHOULD generally take into account the name of the module used when importing it in Python scripts. This name will be prefixed depending on the type of the package.

- A built (i.e. non-SRPM) package for a *Python library* MUST be named with the prefix `python3-`.
- A source package containing primarily a *Python library* MUST be named with the prefix `python-`.

The character `+` is reserved for [Extras](https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#_extras).

#### Python2 binary package naming

Python 2 binary packages MUST be named using a `python2-` prefix. Note that Python 2 is deprecated in Fedora and requires an explicit exception.

### R modules

Packages of R modules (thus they rely on R as a parent) have their own naming scheme. They SHOULD take into account the upstream name of the R module. This makes a package name format of `R-$NAME`. When in doubt, use the name of the module that you type to import it in R.

**Examples:**

```
R-mAr (R module named mAr)
R-RScaLAPACK (R module named RScaLAPACK)
R-waveslim (R module named waveslim)
```

### Sugar Activities

The name for all packaged Sugar activities must be prefixed with `sugar-`. For more details, see [Packaging/SugarActivityGuidelines](https://docs.fedoraproject.org/en-US/packaging-guidelines/SugarActivityGuidelines/).

### Tcl/Tk extensions

The name for all packaged Tcl/Tk extensions must be prefixed with `tcl-`. This rule applies even for Tcl/Tk packages that are already prefixed with `tcl` in the name. For more details, see [Packaging/Tcl#NamingConventions](https://docs.fedoraproject.org/en-US/packaging-guidelines/Tcl/#_naming_conventions).

### TeX

As Fedora has switched TeX environments in the past, TeX packages SHOULD not be named after the TeX environment (TeX Live or teTeX) but instead SHOULD carry the prefix `tex-`.
