Name:           pi-coding-agent
Version:        1.5.2
Release:        1%{?dist}
Summary:        Extensible terminal coding agent

# Provisional: runtime, prebuilt WASM, and bundled notices require further audit.
License:        MIT AND Apache-2.0 AND (Apache-2.0 WITH LLVM-exception) AND BSD-2-Clause AND BSD-3-Clause AND ISC AND BlueOak-1.0.0 AND 0BSD AND CC-BY-SA-4.0 AND CC0-1.0 AND Unlicense
URL:            https://github.com/earendil-works/pi
Source0:        https://registry.npmjs.org/@earendil-works/pi-coding-agent/-/pi-coding-agent-%{version}.tgz
# The npm tarball does not include the upstream license file.
Source4:        https://raw.githubusercontent.com/earendil-works/pi/v%{version}/LICENSE
# quickjs-wasi 3.6.2 vendors mbedTLS in its crypto WASM extension.
Source5:        https://raw.githubusercontent.com/vercel-labs/quickjs-wasi/5a7a0eeda87c99542f8cf3095b6d61ecfa755977/extensions/crypto/mbedtls/LICENSE#/LICENSE-mbedtls
# quickjs-ng commit used by quickjs-wasi 3.6.2.
Source6:        https://raw.githubusercontent.com/quickjs-ng/quickjs/6d46d07d04041b40f4f49eaa7fdebe44c314c699/LICENSE#/LICENSE-quickjs-ng
# quickjs-wasi's amalgamated Ada URL header identifies version 3.4.3.
Source7:        https://raw.githubusercontent.com/ada-url/ada/3c84d730f6c6395355d94c620e96e886e7026474/LICENSE-MIT#/LICENSE-ada-url
# standardwebhooks 1.1.1 omits the MIT license from its npm archive.
Source8:        https://raw.githubusercontent.com/standard-webhooks/standard-webhooks/b4d2c14fc5b4ccff3ff271e3b087dff812254c59/libraries/LICENSE#/LICENSE-standardwebhooks
# The HTML exporter ships these separately from the runtime dependencies.
Source9:        https://registry.npmjs.org/highlight.js/-/highlight.js-11.9.0.tgz
Source10:       https://registry.npmjs.org/marked/-/marked-18.0.11.tgz
Source11:       https://registry.npmjs.org/marked-cjk-friendly/-/marked-cjk-friendly-0.1.2.tgz
# Some AWS SDK packages omit the repository license from their npm archives.
Source12:       https://raw.githubusercontent.com/aws/aws-sdk-js-v3/dee2abd898e7d1c69dd5ca5d74ecdce92e47d19d/LICENSE#/LICENSE-aws-sdk
# WASI SDK 32 source pins; the shipped QuickJS WASM links WASI libraries.
Source13:       https://raw.githubusercontent.com/WebAssembly/wasi-libc/2fc32bc81b9f07f8d9525edea59bfbaf760c06d6/LICENSE#/LICENSE-wasi-libc
Source14:       https://raw.githubusercontent.com/WebAssembly/wasi-libc/2fc32bc81b9f07f8d9525edea59bfbaf760c06d6/LICENSE-MIT#/LICENSE-wasi-libc-MIT
Source15:       https://raw.githubusercontent.com/WebAssembly/wasi-libc/2fc32bc81b9f07f8d9525edea59bfbaf760c06d6/libc-top-half/musl/COPYRIGHT#/COPYRIGHT-wasi-musl
Source16:       https://raw.githubusercontent.com/WebAssembly/wasi-libc/2fc32bc81b9f07f8d9525edea59bfbaf760c06d6/libc-bottom-half/cloudlibc/LICENSE#/LICENSE-wasi-cloudlibc
Source17:       https://raw.githubusercontent.com/llvm/llvm-project/4434dabb69916856b824f68a64b029c67175e532/LICENSE.TXT#/LICENSE-wasi-llvm
Source18:       checksums.sha256
Patch0:         0001-linux-helper-use-build-flags.patch

ExclusiveArch:  x86_64 aarch64
BuildRequires:  nodejs-devel >= 22.19
BuildRequires:  nodejs-npm
BuildRequires:  gcc
BuildRequires:  libxcb-devel
Requires:       nodejs >= 22.19
Requires:       nodejs-npm
Recommends:     fd-find
Recommends:     ripgrep
Recommends:     git-core

%description
Pi is an extensible terminal coding agent with interactive, print, JSON, and
RPC modes. It supports extensions, skills, prompt templates, and themes.

%prep
%autosetup -n package -N
(cd %{_sourcedir} && sha256sum -c %{SOURCE18})
cp %{SOURCE4} LICENSE
cp %{SOURCE5} LICENSE-mbedtls
cp %{SOURCE6} LICENSE-quickjs-ng
cp %{SOURCE7} LICENSE-ada-url
cp %{SOURCE8} LICENSE-standardwebhooks
tar -xOzf %{SOURCE9} package/LICENSE > LICENSE-highlight-export
tar -xOzf %{SOURCE10} package/LICENSE > LICENSE-marked-export
tar -xOzf %{SOURCE11} package/LICENSE > LICENSE-marked-cjk-export
cp %{SOURCE12} LICENSE-aws-sdk
cp %{SOURCE13} LICENSE-wasi-libc
cp %{SOURCE14} LICENSE-wasi-libc-MIT
cp %{SOURCE15} COPYRIGHT-wasi-musl
cp %{SOURCE16} LICENSE-wasi-cloudlibc
cp %{SOURCE17} LICENSE-wasi-llvm
mkdir -p runtime
# Prevent npm from finding the extracted upstream package.json in the parent.
printf '{"private":true}\n' > runtime/package.json

%build
# Resolve dependencies during the network-enabled RPM build. No local lock or
# generated cache needs to be maintained when the upstream release changes.
export npm_config_audit=false npm_config_fund=false
cd runtime
npm install --omit=dev --ignore-scripts %{SOURCE0}
# Fail clearly if npm installs into the extracted upstream package instead of
# this runtime project; COPR build 11324034 failed that way.
test -d node_modules/@earendil-works/pi-tui
# Replace all upstream native prebuilds with a helper built for this target.
cd node_modules/@earendil-works/pi-tui
patch -p3 < %{PATCH0}
rm -rf native/linux/prebuilds native/darwin/prebuilds native/win32/prebuilds
%set_build_flags
bash native/linux/build.sh
cd ../../..
# Use the npm release's unbundled entry point; the prebundled CLI removes
# third-party legal comments and cannot be audited from the runtime lock.
rm -rf node_modules/@earendil-works/pi-coding-agent/dist/bundle
node - <<'NODE'
const fs = require('fs');
const path = 'node_modules/@earendil-works/pi-coding-agent/package.json';
const p = JSON.parse(fs.readFileSync(path));
if (p.bin.pi !== 'dist/bundle/cli.js' || p.exports['./rpc-entry'].import !== './dist/bundle/rpc-entry.js') throw Error('Unexpected upstream entry points');
p.bin.pi = 'dist/cli.js';
p.exports['./rpc-entry'].import = './dist/rpc-entry.js';
fs.writeFileSync(path, JSON.stringify(p, null, 2) + '\n');
NODE
ln -sfn ../@earendil-works/pi-coding-agent/dist/cli.js node_modules/.bin/pi
# Examples include prebuilt binaries and are not needed at runtime.
rm -rf node_modules/@earendil-works/pi-coding-agent/examples
# A reviewable inventory complements the license files shipped in node_modules.
node - <<'NODE' > bundled-licenses.txt
const fs = require('fs');
const packages = require('./package-lock.json').packages;
for (const [name, metadata] of Object.entries(packages)) {
  if (!name || !fs.existsSync(name)) continue;
  const notices = fs.readdirSync(name).filter(n => /^(license|licence|copying|notice)([.\-_]|$)/i.test(n));
  console.log(`${name}\t${metadata.version || ''}\t${metadata.license || 'UNKNOWN'}\t${notices.length ? notices.join(',') : 'NO-ROOT-NOTICE'}`);
}
NODE

%install
install -d %{buildroot}%{_libexecdir}/%{name} %{buildroot}%{_bindir}
cp -a runtime/node_modules %{buildroot}%{_libexecdir}/%{name}/
ln -s ../libexec/%{name}/node_modules/@earendil-works/pi-coding-agent/dist/cli.js %{buildroot}%{_bindir}/pi
cp runtime/bundled-licenses.txt .

%check
export HOME="$PWD/test-home"
mkdir -p "$HOME"
cli=%{buildroot}%{_bindir}/pi
"$cli" --version | grep -Fx '%{version}'
"$cli" --help > /dev/null
PI_CODING_AGENT_DIR="$HOME/.pi/agent" PI_OFFLINE=1 "$cli" list | grep -F 'No packages installed.'
test ! -e %{buildroot}%{_libexecdir}/%{name}/node_modules/@earendil-works/pi-coding-agent/dist/bundle
export_vendor=%{buildroot}%{_libexecdir}/%{name}/node_modules/@earendil-works/pi-coding-agent/dist/core/export-html/vendor
grep -F 'Highlight.js v11.9.0' "$export_vendor/highlight.min.js"
grep -F 'marked v18.0.11' "$export_vendor/marked.min.js"
grep -F 'marked-cjk-friendly v0.1.2' "$export_vendor/marked-cjk-friendly.min.js"
(cd %{buildroot}%{_libexecdir}/%{name} && node --input-type=module -e 'import { existsSync } from "node:fs"; if (!existsSync(new URL(import.meta.resolve("@earendil-works/pi-coding-agent/rpc-entry")))) process.exit(1)')
node -e 'require(process.argv[1])' "%{buildroot}%{_libexecdir}/%{name}/node_modules/@silvia-odwyer/photon-node"
# Decode a known image through the unbundled CLI's Photon integration offline.
node --input-type=module - "%{buildroot}%{_libexecdir}/%{name}/node_modules/@earendil-works/pi-coding-agent/dist/utils/image-resize-core.js" <<'NODE'
import { pathToFileURL } from 'node:url';
const { resizeImageInProcess } = await import(pathToFileURL(process.argv[2]));
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAEElEQVR4AQEFAPr/AP8AAP8FAAH/+lyI0QAAAABJRU5ErkJggg==', 'base64');
const result = await resizeImageInProcess(png, 'image/png');
if (!result || result.width !== 1 || result.height !== 1) throw Error('Photon image decoding failed');
NODE
# Exercise the QuickJS WASM runtime without a provider or network.
(cd %{buildroot}%{_libexecdir}/%{name} && node --input-type=module - <<'NODE'
import { readFileSync } from 'node:fs';
import { QuickJS } from 'quickjs-wasi';
const wasm = readFileSync(new URL(import.meta.resolve('quickjs-wasi/quickjs.wasm')));
const vm = await QuickJS.create({ wasm });
const result = vm.evalCode('6 * 7');
if (result.toNumber() !== 42) throw Error('QuickJS evaluation failed');
result.dispose();
vm.dispose();
NODE
)
native=$(find %{buildroot}%{_libexecdir}/%{name}/node_modules/@earendil-works/pi-tui/native/linux/prebuilds -name '*.node' -print -quit)
test -n "$native"
node -e 'require(process.argv[1])' "$native"

%files
%license LICENSE LICENSE-mbedtls LICENSE-quickjs-ng LICENSE-ada-url LICENSE-standardwebhooks LICENSE-highlight-export LICENSE-marked-export LICENSE-marked-cjk-export LICENSE-aws-sdk
%license LICENSE-wasi-libc LICENSE-wasi-libc-MIT COPYRIGHT-wasi-musl LICENSE-wasi-cloudlibc LICENSE-wasi-llvm bundled-licenses.txt
%doc README.md
%{_bindir}/pi
%{_libexecdir}/%{name}

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 1.5.2-1
- Initial package
