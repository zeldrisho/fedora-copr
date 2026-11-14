#!/usr/bin/env python3
"""Exercise initialization cleanup in a temporary, unprivileged fixture."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest


class InitializeTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.home = self.root / "linuxbrew"
        (self.root / "seed.tar.gz").touch()
        (self.root / "version").write_text("1.2.3\n")
        script = Path(__file__).with_name("brew").read_text()
        for old, new in {
            "/home/linuxbrew": str(self.home),
            "/usr/share/homebrew/seed.tar.gz": str(self.root / "seed.tar.gz"),
            "/usr/share/homebrew/version": str(self.root / "version"),
            "/var/lib/homebrew": str(self.root / "state"),
            "export PATH=/usr/sbin:/usr/bin:/sbin:/bin": f'export PATH="{self.bin}:/usr/bin:/bin"',
            "EUID != 0": "0 != 0",
        }.items():
            script = script.replace(old, new)
        self.launcher = self.root / "brew"
        self.launcher.write_text(script)
        self.tool("getent", "echo 'tester:x:123:123::/tmp:/bin/bash'\n")
        self.tool("install", 'for arg in "$@"; do case "$arg" in /*) mkdir -p "$arg";; esac; done\n')
        self.tool("rm", 'for arg in "$@"; do case "$arg" in /*) /bin/rm -rf "$arg";; esac; done\n')
        self.tool("runuser", 'exit "${MOCK_FAILURE:-0}"\n')

    def tool(self, name, body):
        path = self.bin / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)

    def initialize(self, failure):
        return subprocess.run(["bash", str(self.launcher), "--initialize-rpm-homebrew"],
                              env={**os.environ, "SUDO_UID": "123", "MOCK_FAILURE": str(failure)},
                              capture_output=True)

    def test_failure_cleans_up_and_retry_succeeds(self):
        self.assertNotEqual(self.initialize(1).returncode, 0)
        self.assertFalse(self.home.exists())
        self.assertEqual(self.initialize(0).returncode, 0)
        self.assertTrue((self.root / "state/rpm-initialized").exists())
        self.assertTrue(self.home.exists())

    def test_existing_directory_is_preserved(self):
        self.home.mkdir()
        (self.home / "important").write_text("keep")
        self.assertNotEqual(self.initialize(1).returncode, 0)
        self.assertEqual((self.home / "important").read_text(), "keep")


if __name__ == "__main__":
    unittest.main()
