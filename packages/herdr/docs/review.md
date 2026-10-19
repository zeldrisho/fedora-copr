# Herdr package review checklist

This is a preparation record, not official Fedora review approval. Evidence below was checked on 2026-10-19.

## Published build evidence

- COPR build [11168076](https://copr.fedorainfracloud.org/coprs/zeldrisho/packages/build/11168076/) succeeded for Fedora 44, Fedora 45, and Rawhide, x86_64: `herdr-0.9.5-1`.
- Public [SRPM](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/srpm-builds/11168076/herdr-0.9.5-1.src.rpm) and [built Rawhide spec](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11168076-herdr/herdr.spec).
- [Rawhide review and lint output](https://download.copr.fedorainfracloud.org/results/zeldrisho/packages/fedora-rawhide-x86_64/11168076-herdr/fedora-review/review.txt): binary/SRPM lint reports 0 errors and 3 warnings (missing `herdr(1)` and non-URL Source1/Source2). Debuginfo lint reports 0 errors and 0 warnings, with filters applied. The upstream source checksum matches.
- The review ran with `--prebuilt`; its Mock-build warning does not indicate a failed COPR build. Its installed-package section says the packages were not installed despite the passing checklist label; that section is not runtime evidence.
- Fedora 44 host installation is confirmed: `herdr-0.9.5-1.fc44.x86_64`. `rpm -V` passes; `herdr --version` reports `0.9.5`; Bash completion generation succeeds. Installed requirements, bundled-crate provides, file list, and license-file list were inspected. `rpmlint -i herdr yazi` reports only Herdr's missing-manual-page warning (0 errors, 1 warning, 7 filtered).
- Repository validation passes for all three packages; 19 Python tests pass. These checks do not replace binary builds or interactive testing.

## Checklist and remaining review work

- [x] Package name, directory, and spec basename are `herdr`.
- [x] Upstream source is a versioned source archive; Rust and Zig dependencies are supplied as source archives.
- [x] Executable is built locally; no upstream binary is installed.
- [x] Shell completions are generated from the built executable.
- [x] Project and dependency license files are included; linked Cargo licenses are recorded.
- [x] Fedora 44, Fedora 45, and Rawhide x86_64 COPR builds succeed.
- [x] Fedora 44 installed version/completion checks and RPM integrity verification pass.
- [ ] Confirm every Zig component's license and add its specific text to `%license` where required. The scanner reports 18,419 unknown-license files; this requires source-level assessment, not a conclusion that all are unlicensed.
- [ ] Add an accurate manual page for `herdr` in a new release, or document reviewer acceptance of its absence.
- [ ] Review source-bundle provenance/regeneration notes in `../README.md` and the audit; non-URL local archives are intentional, not broken download endpoints.
- [ ] Review compiler flags and justify the check-local `%define rustflags_codegen_units 16` (the release binary retains normal flags).
- [ ] Retain/lint a matching SRPM and inspect all binary subpackages, including debugsource/debuginfo, independently of the generated review.
- [ ] Validate aarch64 and offline build behavior; successful x86_64 builds do not establish either.
- [ ] Install and smoke-test server/workspace creation, detach/reattach, and terminal panes in clean Fedora environments. The host version/completion checks above do not cover these operations.

Do not reuse `0.9.5-1` for changes to installed files or dependencies: it is now published and installed. COPR success is not a Bugzilla review or official Fedora Rawhide inclusion.
