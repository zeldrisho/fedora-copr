# Herdr package review checklist

- [x] Package name, directory, and spec basename are `herdr`.
- [x] Upstream source is a versioned source archive; Rust and Zig dependencies are supplied as source archives.
- [x] Executable is built locally; no upstream binary is installed.
- [x] Shell completions are generated from the built executable.
- [x] Project and dependency license files are included; linked Cargo licenses are recorded.
- [ ] Confirm every Zig component's license and add its specific text to `%license` where required.
- [ ] Run `make validate` and retain/lint the SRPM.
- [ ] Build offline in Fedora 44, Fedora 45, and Rawhide Mock chroots on x86_64 and aarch64.
- [ ] Inspect binary RPM files, requirements, provides, license files, and debuginfo.
- [ ] Install and smoke-test Herdr server/workspace operations in clean Fedora environments.
