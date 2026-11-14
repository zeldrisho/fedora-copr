#!/usr/bin/env python3
"""Test the RPM launcher without downloading the upstream distribution."""
import hashlib
import io
import os
import re
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

package = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix="kotlin launcher ") as tmp:
    root = Path(tmp)
    # Exercise the actual RPM check fixture after RPM percent escaping.
    spec = (package / "kotlin-toolchain.spec").read_text()
    fixture_commands = [line for line in spec.splitlines() if line.endswith(' > fake-wrapper')]
    assert len(fixture_commands) == 1
    subprocess.run(["sh", "-c", fixture_commands[0].replace("%%", "%")], cwd=root, check=True)
    wrapper = root / "upstream wrapper"
    wrapper.write_text((root / "fake-wrapper").read_text())
    launcher = root / "kotlin"
    launcher.write_text((package / "kotlin.in").read_text().replace(
        "/usr/libexec/kotlin-toolchain/upstream-wrapper", str(wrapper)))
    for value, expected in [(None, "/usr/lib/jvm/java-25-openjdk"),
                            ("", "/usr/lib/jvm/java-25-openjdk"),
                            ("/custom java", "/custom java")]:
        env = dict(os.environ)
        env.pop("KOTLIN_CLI_JAVA_HOME", None)
        if value is not None:
            env["KOTLIN_CLI_JAVA_HOME"] = value
        output = subprocess.check_output(["sh", str(launcher), "two words", ""], env=env, text=True)
        assert output == f"{expected}\ntwo words\n\n", repr(output)
    if len(sys.argv) > 1:
        upstream = Path(sys.argv[1]).resolve()
        original = upstream.read_text()
        version = re.search(r'^kotlin_cli_version=([0-9.]+)$', original, re.MULTILINE).group(1)
        release_digest = re.search(r'^kotlin_cli_sha256=([0-9a-f]{64})$', original, re.MULTILINE).group(1)
        cache = root / "cache"
        dist = cache / f"kotlin-cli-{version}"
        (dist / "bin").mkdir(parents=True)
        (dist / ".flag").write_text(release_digest + "\n")
        (dist / "bin/launcher.sh").write_text('#!/bin/sh\nprintf "%s\\n" "$KOTLIN_CLI_JAVA_HOME" "$@"\n')
        launcher.write_text((package / "kotlin.in").read_text().replace(
            "/usr/libexec/kotlin-toolchain/upstream-wrapper", str(upstream)))
        env = dict(os.environ, KOTLIN_CLI_BOOTSTRAP_CACHE_DIR=str(cache), KOTLIN_CLI_JAVA_HOME="/test/java")
        env.pop("KOTLIN_CLI_WRAPPER_ALWAYS_USE_INTRINSIC_VERSION", None)
        output = subprocess.check_output(["sh", str(launcher), "two words"], env=env, text=True)
        assert output == "/test/java\ntwo words\n", repr(output)
        print("Released upstream wrapper uses a verified cached distribution: OK")

        # Exercise first-run verification with a generated archive and fake curl.
        # The altered checksum applies only to this disposable test wrapper.
        archive = root / "fixture.tgz"
        content = b'#!/bin/sh\nprintf "%s\\n" "$KOTLIN_CLI_JAVA_HOME" "$@"\n'
        with tarfile.open(archive, "w:gz") as tar:
            info = tarfile.TarInfo("bin/launcher.sh")
            info.mode, info.size = 0o755, len(content)
            tar.addfile(info, io.BytesIO(content))
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        assert original.count(release_digest) == 1
        test_wrapper = root / "fixture-wrapper"
        test_wrapper.write_text(original.replace(release_digest, digest))
        launcher.write_text((package / "kotlin.in").read_text().replace(
            "/usr/libexec/kotlin-toolchain/upstream-wrapper", str(test_wrapper)))
        tools = root / "tools"
        tools.mkdir()
        curl = tools / "curl"
        curl.write_text('#!/bin/sh\necho fetch >> "$FETCH_LOG"\nwhile [ "$#" -gt 0 ]; do\n  if [ "$1" = --output ]; then shift; cp "$FIXTURE" "$1"; exit; fi\n  shift\ndone\nexit 1\n')
        curl.chmod(0o755)
        env.update(PATH=f"{tools}:{os.environ['PATH']}", FIXTURE=str(archive),
                   FETCH_LOG=str(root / "fetch.log"), KOTLIN_CLI_NO_WELCOME_BANNER="1",
                   KOTLIN_CLI_BOOTSTRAP_CACHE_DIR=str(root / "first-cache"))
        output = subprocess.check_output(["sh", str(launcher), "two words"], env=env, text=True)
        assert output.endswith("/test/java\ntwo words\n"), repr(output)
        assert (root / "fetch.log").read_text() == "fetch\n"
        subprocess.check_output(["sh", str(launcher)], env=env, text=True)
        assert (root / "fetch.log").read_text() == "fetch\n", "cache miss on second launch"
        # A project-local wrapper selects its version and checksum via sed.
        project = root / "project"
        project.mkdir()
        (project / "project.yaml").write_text("# fixture\n")
        local_wrapper = project / "kotlin"
        local_wrapper.write_text(f"kotlin_cli_version=9.9.9\nkotlin_cli_sha256={digest}\n")
        local_wrapper.chmod(0o755)
        output = subprocess.check_output(["sh", str(launcher), "local"], env=env, cwd=project, text=True)
        assert output.endswith("/test/java\nlocal\n"), repr(output)
        assert (root / "first-cache/kotlin-cli-9.9.9/.flag").read_text().strip() == digest
        test_wrapper.write_text(original.replace(release_digest, "0" * 64))
        env["KOTLIN_CLI_BOOTSTRAP_CACHE_DIR"] = str(root / "bad-cache")
        failed = subprocess.run(["sh", str(launcher)], env=env, capture_output=True, text=True)
        assert failed.returncode != 0 and "Checksum mismatch" in failed.stderr, failed.stderr
        assert not (root / f"bad-cache/kotlin-cli-{version}/.flag").exists()
        print("Released wrapper mock download, cache reuse, and checksum rejection: OK")
print("Launcher default, override, and argument forwarding: OK (offline fixture)")
