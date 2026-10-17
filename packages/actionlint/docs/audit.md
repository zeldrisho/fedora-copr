# actionlint source and installation audit

Preparation audit for **actionlint 1.7.12-1**, using the sources in COPR build **11162667**. This is a packager self-check, not Fedora reviewer approval or a legal determination. See the [review record](review.md), [Fedora Go guidance](../../../docs/packaging-guidelines/golang.md), and [licensing guidance](../../../docs/packaging-guidelines/licensing-guidelines.md).

## Licensing findings

The upstream and vendor archives were unpacked separately for inspection. Go Vendor Tools 0.12.0 with askalono reported no missing module licenses and verified the spec's cumulative expression:

```text
Apache-2.0 AND BSD-3-Clause AND MIT
```

The main project license and all 14 module-level license texts were read, together with YAML's NOTICE and the Go modules' PATENTS files. The following breakdown agrees with those texts:

| Component | Version | License findings |
| --- | --- | --- |
| actionlint | 1.7.12 | MIT, `LICENSE.txt`, rhysd |
| github.com/bmatcuk/doublestar/v4 | 4.10.0 | MIT |
| github.com/clipperhouse/uax29/v2 | 2.7.0 | MIT |
| github.com/fatih/color | 1.19.0 | MIT |
| github.com/google/go-cmp | 0.7.0 | BSD-3-Clause |
| github.com/mattn/go-colorable | 0.1.14 | MIT |
| github.com/mattn/go-isatty | 0.0.20 | MIT |
| github.com/mattn/go-runewidth | 0.0.21 | MIT |
| github.com/mattn/go-shellwords | 1.0.12 | MIT |
| github.com/robfig/cron/v3 | 3.0.1 | MIT |
| github.com/yuin/goldmark | 1.7.17 | MIT |
| go.yaml.in/yaml/v4 | 4.0.0-rc.3 | Apache-2.0 plus MIT-covered libyaml ports identified by NOTICE |
| golang.org/x/net | 0.52.0 | BSD-3-Clause; PATENTS grant retained |
| golang.org/x/sync | 0.20.0 | BSD-3-Clause; PATENTS grant retained |
| golang.org/x/sys | 0.42.0 | BSD-3-Clause; PATENTS grant retained |

**YAML deserves an explicit note:** its root LICENSE is Apache-2.0, which is what the automated module-level detector reports. Its NOTICE identifies eight MIT-covered files in `internal/libyaml`; `api.go` also contains the MIT text and copyright headers. The aggregate RPM expression already includes MIT, so this does not require a change to the spec's expression. The RPM retains YAML's LICENSE and NOTICE, including the libyaml attribution.

All three identifiers appear in the installed Fedora license-data-derived lint configuration, supplied by `rpmlint-fedora-license-data-1.76-1.fc44`. This is supporting local policy data, not a claim that live Fedora policy was refreshed during this audit.

All **20** main-RPM `%license` files match their source counterparts byte-for-byte: the main license, 14 module license files, YAML NOTICE, three PATENTS files, and `vendor/modules.txt`. All **14** module entries in that manifest have matching `bundled(golang(...))` provides.

This review covers the identified license texts, notices, module manifest, and installed license payload. It is not an exhaustive line-by-line audit of all source code or generated data. The Fedora reviewer still evaluates compliance and any additional source-level concerns.

### Repeat the automated license check

From the repository root, without changing the spec or config:

```sh
go_vendor_license --config packages/actionlint/go-vendor-tools.toml \
  --path packages/actionlint/actionlint.spec report all --verify-spec
```

Local output: `/tmp/actionlint-license-audit/report.txt`.

## Vendor reproducibility

Regeneration used a scratch directory containing only the checked-in spec, config, and upstream archive. No repository files were overwritten. Go Vendor Tools ran `go mod tidy`, then `go mod vendor`; network access at this source-preparation stage is distinct from an offline binary build.

The generated archive is **byte-for-byte identical** to the checked-in and published vendor source:

```text
aa660504a5f2b3d5630635c028c17199fa65c2709aa714574b029acb52372497  actionlint-1.7.12-vendor.tar.bz2
```

To repeat, use a new temporary directory:

```sh
work=$(mktemp -d)
cp packages/actionlint/actionlint.spec \
  packages/actionlint/go-vendor-tools.toml \
  packages/actionlint/actionlint-1.7.12.tar.gz "$work/"
(cd "$work" && go_vendor_archive create --config go-vendor-tools.toml actionlint.spec)
cmp "$work/actionlint-1.7.12-vendor.tar.bz2" \
  packages/actionlint/actionlint-1.7.12-vendor.tar.bz2
```

Local regeneration log: `/tmp/actionlint-vendor-regeneration.log`.

## Installed-RPM smoke test

The locally built **1.7.12-1.fc44 x86_64** main RPM was installed using RPM into a temporary root with a private RPM database. Bubblewrap supplied a user namespace with namespace-local root and `CAP_SYS_CHROOT`; the host filesystem was read-only except for the temporary install root. The host RPM database was not modified.

Results:

- Private database query reports `actionlint-1.7.12-1.fc44.x86_64`.
- `rpm -V --nodeps actionlint` against that root passed: installed package files match RPM metadata.
- The installed `/usr/bin/actionlint -version` reports `1.7.12`.
- A valid minimal GitHub Actions workflow exits **0**.
- A workflow using `${{ unknown_context.value }}` exits **1**, with the expected undefined-variable diagnostic.
- Runtime checks ran with a separate network namespace and external shellcheck/pyflakes integrations disabled.

**Limits:** installation used `--nodeps --noscripts` into a minimal root, with host shared libraries mounted read-only for execution. This is an installed-payload/runtime test, not a full Fedora DNF dependency-resolution test or a test of the Rawhide RPM. The package has no package-specific scriptlets; full supported-environment installation remains a reviewer check. Runtime network isolation does not prove that the earlier build was network-isolated.

Local smoke-test output: `/tmp/actionlint-license-audit/installed-smoke.txt`. Temporary root: `/tmp/actionlint-license-audit/installroot/`.

## Remaining submission work

- Confirm Fedora account group membership and Bugzilla email alignment.
- The contributor confirmed no existing actionlint package or review; recheck if submission is delayed.
- Publish any local lint/audit logs needed by the reviewer; `/tmp/` paths are not public artifacts.
- Obtain the independent human Fedora review and sponsorship, if needed.
