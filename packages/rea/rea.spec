# The bundled native binaries are prebuilt and have no corresponding debug sources.
%global _debugsource_template %{nil}

Name:           rea
Version:        6.9.0
Release:        1%{?dist}
Summary:        Reverse engineering CLI and MCP server

# livecheck: manual Re-check the pinned OpenPGP.js source, its checksum, the Node.js range and the dependency licenses on update.

# The npm release contains generated JavaScript and bundled runtime modules.
# Review the bundled license inventory and native artifacts on every update.
License:        MIT AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND ISC AND BlueOak-1.0.0 AND Zlib AND LGPL-3.0-or-later
URL:            https://github.com/morluto/rea
Source0:        https://registry.npmjs.org/rea-agents/-/rea-agents-%{version}.tgz
Source1:        rea
# OpenPGP.js 6.3.2 publishes only generated dist files. Build the LGPL-licensed
# dependency from its tagged source so its corresponding source and build
# inputs accompany the installed files.
Source2:        https://github.com/openpgpjs/openpgpjs/archive/refs/tags/v6.3.2.tar.gz
Source3:        checksums.sha256

ExclusiveArch:  x86_64 aarch64
BuildRequires:  nodejs24-devel >= 1:24.22.1
BuildRequires:  nodejs24-npm
BuildRequires:  procps-ng
BuildRequires:  sqlite
Requires:       nodejs24 >= 1:24.22.1
Requires:       procps-ng

%description
REA provides a command-line interface and MCP server for reverse engineering
binaries, applications, and runtime behavior. Analysis engines are optional
and must be installed separately.

%prep
%autosetup -n package
(cd %{_sourcedir} && sha256sum -c %{SOURCE3})

%build
export npm_config_audit=false npm_config_fund=false
# The npm archive ships only generated OpenPGP.js bundles; rebuild the pinned
# dependency from its tagged source and committed lockfile.
mkdir openpgp-source
tar -xzf %{SOURCE2} -C openpgp-source --strip-components=1
(
cd openpgp-source
npm-24 ci --ignore-scripts
npm-24 run build
npm-24 run build-types
)
# Resolve the integrity-pinned shrinkwrap during the network-enabled RPM build.
npm-24 ci --omit=dev --ignore-scripts
# Install the locally built OpenPGP.js instead of the generated npm bundle.
rm -rf node_modules/openpgp
install -d node_modules/openpgp
cp -a openpgp-source/dist openpgp-source/lightweight \
    openpgp-source/package.json openpgp-source/LICENSE openpgp-source/README.md \
    node_modules/openpgp/
# Frida needs an install script to acquire a native binding; do not ship a
# nonfunctional or unreviewed binding. Other optional native modules remain.
rm -rf node_modules/frida
node-24 - <<'NODE' > bundled-licenses.txt
const fs = require('fs');
const lock = JSON.parse(fs.readFileSync('node_modules/.package-lock.json'));
for (const [name, metadata] of Object.entries(lock.packages)) {
  if (name === 'node_modules/frida' || !fs.existsSync(name)) continue;
  console.log(`${name}\t${metadata.version || ''}\t${metadata.license || 'UNKNOWN'}`);
}
NODE

%install
install -d %{buildroot}%{_libexecdir}/%{name} %{buildroot}%{_bindir}
# Keep the upstream release layout, including bridges and skill assets.
cp -a dist scripts bridge skills third_party licenses assets .claude-plugin .codex-plugin .cursor-plugin package.json mcp.json node_modules %{buildroot}%{_libexecdir}/%{name}/
install -pm 0755 %{SOURCE1} %{buildroot}%{_bindir}/rea

%check
export HOME="$PWD/test-home"
mkdir -p "$HOME"
node-24 %{buildroot}%{_libexecdir}/%{name}/scripts/rea.mjs --version | grep -Fx '%{version}'
node-24 %{buildroot}%{_libexecdir}/%{name}/scripts/rea.mjs --help > /dev/null
# Check the locally built OpenPGP.js bundles retain embedded sources.
node-24 - %{buildroot}%{_libexecdir}/%{name}/node_modules/openpgp/dist <<'NODE'
const fs = require('fs');
const path = require('path');
const root = process.argv[2];
for (const file of ['node/openpgp.min.mjs.map', 'node/openpgp.min.cjs.map']) {
  if (!fs.existsSync(path.join(root, file))) throw Error(`Missing OpenPGP.js map: ${file}`);
}
let count = 0;
function visit(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) visit(file);
    else if (entry.name.endsWith('.map')) {
      const map = JSON.parse(fs.readFileSync(file, 'utf8'));
      if (!Array.isArray(map.sources) || !map.sources.length ||
          !Array.isArray(map.sourcesContent) || map.sources.length !== map.sourcesContent.length ||
          map.sourcesContent.some(source => typeof source !== 'string')) {
        throw Error(`Incomplete embedded sources in ${file}`);
      }
      count++;
    }
  }
}
visit(root);
if (!count) throw Error('No OpenPGP.js source maps found');
NODE
node-24 --input-type=module -e 'const p = await import("@lydell/node-pty"); const t = p.spawn("/bin/sh", ["-c", "exit 0"]); t.onExit(e => { if (e.exitCode !== 0) process.exitCode = 1; });'
mkdir -p test-app
printf 'module.exports = 42;\n' > test-app/index.js
node-24 %{buildroot}%{_libexecdir}/%{name}/scripts/rea.mjs analyze-javascript-application test-app --format json > test-analysis.json
test -s test-analysis.json
printf "CREATE TABLE greetings (message TEXT); INSERT INTO greetings VALUES ('hello world');\n" | sqlite3 test.db
node-24 %{buildroot}%{_libexecdir}/%{name}/scripts/rea.mjs inspect-sqlite-database "$PWD/test.db" --table greetings --worker-timeout-ms 90000 --json > test-sqlite.json
grep -F 'hello world' test-sqlite.json
# Exercise the rebuilt OpenPGP.js bundle used by Hopper provisioning offline.
(cd %{buildroot}%{_libexecdir}/%{name} && node-24 --input-type=module - <<'NODE'
import * as openpgp from 'openpgp';
const { privateKey, publicKey } = await openpgp.generateKey({
  type: 'ecc', curve: 'curve25519', userIDs: [{ name: 'rea test' }], format: 'object',
});
const message = await openpgp.createMessage({ text: 'rea hopper' });
const armored = await openpgp.sign({ message, signingKeys: privateKey, detached: true });
const verified = await openpgp.verify({
  message,
  signature: await openpgp.readSignature({ armoredSignature: armored }),
  verificationKeys: publicKey,
});
if (!(await verified.signatures[0].verified)) throw Error('OpenPGP.js signature verification failed');
NODE
)

%files
%license LICENSE THIRD_PARTY_NOTICES.md bundled-licenses.txt
%doc README.md DISCLAIMER.md
%{_bindir}/rea
%{_libexecdir}/%{name}

%changelog
* Fri Nov 13 2026 Zeldris <80939130+zeldrisho@users.noreply.github.com> - 6.9.0-1
- Initial package
