#!/usr/bin/env python3
"""Discover updates, refresh source checksums, or propose coordinated updates.

No RPM macros are executed. Unknown layouts fail closed; an explicit
`# livecheck: manual REASON` creates a proposal without modifying the spec.
"""
import argparse
import datetime
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

VERSION = r"\d+(?:\.\d+)*"


def version_key(version):
    if not isinstance(version, str) or not re.fullmatch(VERSION, version):
        raise ValueError(f"Unsupported stable version: {version!r}")
    return tuple(map(int, version.split(".")))


def tag_version(tag):
    # Accept v1.2, 1.2.3.4 and release-1.2.3, but not prerelease suffixes.
    if not isinstance(tag, str):
        return None
    match = re.fullmatch(rf"(?:[A-Za-z][A-Za-z_/-]*[-_/])?v?({VERSION})", tag)
    return match.group(1) if match else None


def field(spec, name):
    match = re.search(rf"^{re.escape(name)}:\s*(\S+)\s*$", spec, re.MULTILINE | re.IGNORECASE)
    if not match:
        raise ValueError(f"Missing or non-literal {name}")
    return match.group(1)


def expand(template, name, version):
    result = template.replace("%{name}", name).replace("%{version}", version)
    if re.search(r"%(?![0-9a-fA-F]{2})", result):
        raise ValueError(f"Unsupported source macro: {template}")
    return result


def filename(url):
    parsed = urllib.parse.urlsplit(url)
    name = Path(parsed.fragment or parsed.path).name
    if not re.fullmatch(r"[A-Za-z0-9_+.-]+", name) or name in {".", ".."}:
        raise ValueError(f"Unsafe or unsupported source filename: {name!r}")
    return name


def github_repo(url):
    match = re.match(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:/|$)", url)
    return match.group(1).removesuffix(".git") if match else None


def inspect_package(package):
    """Return a validated update plan without network access or file changes."""
    package = Path(package)
    if not re.fullmatch(r"[A-Za-z0-9_+.-]+", package.name) or package.name in {".", ".."}:
        raise ValueError("Invalid package name")
    spec_path = package / f"{package.name}.spec"
    spec = spec_path.read_text()
    manual = re.search(r"^# livecheck: manual\s+(.+)$", spec, re.MULTILINE)
    current = field(spec, "Version")
    version_key(current)
    name = field(spec, "Name")
    sources = {}
    for match in re.finditer(r"^Source(\d*):\s*(\S+)\s*$", spec, re.MULTILINE | re.IGNORECASE):
        number = int(match.group(1) or 0)
        if number in sources:
            raise ValueError(f"Duplicate Source{number}")
        sources[number] = match.group(2)
    source0 = sources.get(0, "")
    if not source0.startswith("https://") or "%{version}" not in source0:
        raise ValueError("Source0 needs an HTTPS URL containing %{version}")
    # Infer the release service, not the package name or distribution host.
    npm = re.fullmatch(r"https://registry\.npmjs\.org/((?:@[a-z0-9_.-]+/)?[a-z0-9_.-]+)/-/[^/]+", source0)
    if npm:
        provider = ("npm", npm.group(1))
    else:
        repo = github_repo(source0) or github_repo(field(spec, "URL"))
        if not repo:
            raise ValueError("Cannot infer a GitHub or npm version source")
        provider = ("github", repo)
    if manual:
        return dict(package=package, spec_path=spec_path, spec=spec, name=name, current=current,
                    provider=provider, manual=manual.group(1), tracked=[])
    manifests = [package / name for name in ("source.sha256", "checksums.sha256") if (package / name).is_file()]
    if len(manifests) != 1:
        raise ValueError("Need exactly one source.sha256 or checksums.sha256 file")
    checksum_path = manifests[0]
    text = checksum_path.read_text()
    remote = {}
    for number, template in sources.items():
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", template) and not template.startswith("https://"):
            raise ValueError(f"Unsupported remote Source{number}: {template}")
        if template.startswith("//"):
            raise ValueError(f"Unsupported remote Source{number}: {template}")
        if template.startswith("https://"):
            old_name = filename(expand(template, name, current))
            if old_name in remote:
                raise ValueError(f"Ambiguous source filename: {old_name}")
            remote[old_name] = template
    if checksum_path.name == "source.sha256":
        if not re.fullmatch(r"[0-9a-f]{64}\n?", text):
            raise ValueError("Unexpected single-source checksum")
        tracked = [source0]
    else:
        tracked = []
        for line in text.splitlines():
            match = re.fullmatch(r"[0-9a-f]{64} [ *]([A-Za-z0-9_+.-]+)", line)
            if not match or match.group(1) not in remote:
                raise ValueError("Manifest entry does not match an HTTPS Source URL")
            template = remote[match.group(1)]
            if template in tracked:
                raise ValueError("Duplicate checksum manifest entry")
            tracked.append(template)
        if source0 not in tracked:
            raise ValueError("Checksum manifest must cover Source0")
    uncovered = [template for template in remote.values() if "%{version}" in template and template not in tracked]
    if uncovered:
        raise ValueError("Versioned auxiliary sources need manifest checksums or a manual-update marker")
    if not re.search(r"^Release:\s*\d+%\{\?dist\}\s*$", spec, re.MULTILINE) or "%changelog\n" not in spec:
        raise ValueError("Need a numeric Release with %{?dist} and a %changelog section")
    return dict(package=package, spec_path=spec_path, spec=spec, name=name, current=current,
                provider=provider, checksum_path=checksum_path, tracked=tracked)


def fetch_json(url, github=False):
    headers = {"Accept": "application/json", "User-Agent": "copr-livecheck"}
    if github and os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def latest_version(plan):
    provider, identifier = plan["provider"]
    if provider == "npm":
        release = fetch_json(f"https://registry.npmjs.org/{urllib.parse.quote(identifier, safe='')}/latest")
        if release.get("name") != identifier:
            raise ValueError("Unexpected npm package name")
        version = release.get("version")
    else:
        api = f"https://api.github.com/repos/{identifier}"
        try:
            release = fetch_json(api + "/releases/latest", github=True)
        except urllib.error.HTTPError as error:
            error.close()
            if error.code != 404:
                raise
            # Repositories without GitHub Releases can still publish stable tags.
            tags = fetch_json(api + "/tags?per_page=100", github=True)
            versions = [version for tag in tags if (version := tag_version(tag.get("name")))]
            if not versions:
                raise ValueError("No stable numeric versions in the first 100 upstream tags")
            version = max(versions, key=version_key)
        else:
            if release.get("draft") or release.get("prerelease"):
                raise ValueError("Latest release must be stable and published")
            version = tag_version(release.get("tag_name"))
    version_key(version)
    return version


def hash_url(url):
    digest = hashlib.sha256()
    # Do not forward release API credentials to distribution/license hosts.
    with urllib.request.urlopen(url, timeout=60) as response:
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def update(plan):
    version = latest_version(plan)
    comparison = itertools.zip_longest(version_key(version), version_key(plan["current"]), fillvalue=0)
    new, old = zip(*comparison)
    if new <= old:
        print(f"{plan['package'].name}: already up to date ({plan['current']})")
        return None
    if plan.get("manual"):
        # Do not break coordinated inputs: propose a version for a human to finish.
        proposal = plan["package"] / "livecheck-update.txt"
        proposal.write_text(f"Proposed upstream version: {version}\nCurrent packaged version: {plan['current']}\nManual steps: {plan['manual']}\nRemove this file when the update is complete.\n")
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as output:
                print(f"version={version}\nmanual=true", file=output)
        print(f"{plan['package'].name}: proposed {version}; manual update required")
        return version
    entries = []
    # Fetch all inputs before modifying files; incomplete releases leave no edits.
    for template in plan["tracked"]:
        url = expand(template, plan["name"], version)
        entries.append((hash_url(url.split("#", 1)[0]), filename(url)))
    if plan["checksum_path"].name == "source.sha256":
        checksum_text = entries[0][0] + "\n"
    else:
        checksum_text = "".join(f"{digest}  {name}\n" for digest, name in entries)
    spec, replaced = re.subn(r"^(Version:\s*)\S+", lambda match: match.group(1) + version, plan["spec"], flags=re.MULTILINE | re.IGNORECASE)
    if replaced != 1:
        raise ValueError("Need exactly one Version field")
    spec = re.sub(r"^(Release:\s*)\d+(%\{\?dist\})", r"\g<1>1\2", spec, count=1, flags=re.MULTILINE)
    today = datetime.datetime.now(datetime.timezone.utc)
    date = f"{('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[today.weekday()]} {('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')[today.month - 1]} {today.day:02d} {today.year}"
    entry = f"* {date} github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com> - {version}-1\n- Update to {version}\n\n"
    spec = spec.replace("%changelog\n", "%changelog\n" + entry, 1)
    plan["spec_path"].write_text(spec)
    plan["checksum_path"].write_text(checksum_text)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as output:
            print(f"version={version}", file=output)
    print(f"{plan['package'].name}: {plan['current']} -> {version}")
    return version


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?")
    parser.add_argument("--discover", action="store_true", help="list supported packages as JSON, offline")
    parser.add_argument("--check", action="store_true", help="check update support without fetching or editing")
    args = parser.parse_args()
    if args.discover:
        packages = []
        for spec in sorted(Path("packages").glob("*/*.spec")):
            try:
                inspect_package(spec.parent)
            except (ValueError, OSError) as error:
                print(f"{spec.parent.name}: {error}", file=sys.stderr)
            else:
                packages.append(spec.parent.name)
        print(json.dumps(packages))
        return
    if not args.package or not re.fullmatch(r"[A-Za-z0-9_+.-]+", args.package) or args.package in {".", ".."}:
        parser.error("a valid package name is required")
    try:
        plan = inspect_package(Path("packages") / args.package)
        if args.check:
            detail = f"manual proposal: {plan['manual']}" if plan.get('manual') else f"{len(plan['tracked'])} checksummed source(s)"
            print(f"{args.package}: supported ({plan['provider'][0]}, {detail})")
        else:
            update(plan)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{args.package}: {error}\n")


if __name__ == "__main__":
    main()
