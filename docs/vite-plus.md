# Vite+ packaging

## Status

Vite+ is experimental. Packit PR and main publishing jobs are enabled, but livecheck updates remain disabled pending a successful build. COPR build [11324037](https://copr.fedorainfracloud.org/coprs/build/11324037/) failed because TypeScript discovered intentionally invalid Yuku test fixtures inside the workspace. The spec now extracts only Yuku's license, not its tests.

## Sources and build

The spec follows the upstream [workspace build](https://github.com/voidzero-dev/vite-plus/blob/v1.6.0/CONTRIBUTING.md) and [Homebrew formula](https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/v/vite-plus.rb). SRPM preparation verifies the release archive and fetches the Git repositories and submodules pinned by upstream's workspace and Cargo lockfile. `sync-workspace.sh` runs upstream's synchronization against those snapshots and checks that both lockfiles remain unchanged. Run `bash packages/vite-plus/test-source-preparation.sh` for offline negative tests; set `VITE_PLUS_ARCHIVE` to a downloaded release archive to exercise source fetching too. Checksums check integrity, not independent provenance.

The RPM build requires network access for the pinned Rust nightly, pnpm and locked dependencies. Toolchains and dependencies fetched at build time are not included in the SRPM. Node 24 requires Fedora's full ICU data; a previous build crashed during type generation without it.

The production npm tree includes upstream prebuilt Zigpty, Yuku and esbuild binaries resolved from the pnpm lockfile. Only the target glibc Zigpty binary is retained. Zigpty and Yuku license texts are included separately. The pinned [Yuku core 0.19.0 manifest](https://github.com/yuku-toolchain/yuku/blob/v0.19.0/npm/yuku-core/package.json) declares MIT and lists the platform binding packages; the spec includes the [release's MIT license](https://github.com/yuku-toolchain/yuku/blob/v0.19.0/LICENSE). The [napi-zig issue](https://github.com/yuku-toolchain/napi-zig/issues/11) about missing binding-package license metadata is closed; the manifest is evidence for the notice but does not establish binary provenance or cover every embedded component. Review applicable notices before publishing.

Build [11321840](https://copr.fedorainfracloud.org/coprs/build/11321840/) failed because these upstream binaries lack build IDs. The spec disables strict missing-build-ID handling and build-ID links for this package; prebuilt binaries do not provide normal debug information or build-ID-based debugging. The Rust CLI is still built from source. The RPM checks esbuild transforms, Zigpty PTY creation, Yuku parsing and shell completions. These changes have not been validated in a Fedora RPM build on either architecture; confirm RPM packaging, installed behavior, and runtime downloads before relying on the published package.

## Updates and limitations

Livecheck updates the main version and source checksums. Review workspace pins, native dependency versions and separately included notices on updates.
