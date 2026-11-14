#!/usr/bin/env python3
"""Offline tests for the staged package-update check."""
import importlib.util
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("verify", Path(__file__).with_name("verify-update.py"))
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

SPEC = "Name: example\nVersion: 2.0.0\nRelease: 1%{?dist}\n%changelog\n"


class VerifyUpdateTest(unittest.TestCase):
    def check(self, changed, spec=SPEC, proposal=False):
        return verify.check("example", "2.0.0", changed, spec, proposal)

    def test_accepts_package_changes(self):
        self.assertIn("2.0.0", self.check(["packages/example/example.spec"]))

    def test_rejects_unrelated_paths(self):
        with self.assertRaises(ValueError):
            self.check(["packages/example/example.spec", "README.md"])

    def test_rejects_similar_package_name(self):
        with self.assertRaises(ValueError):
            self.check(["packages/example-extra/example-extra.spec"])

    def test_rejects_empty_change(self):
        with self.assertRaises(ValueError):
            self.check([])

    def test_rejects_wrong_version(self):
        with self.assertRaises(ValueError):
            self.check(["packages/example/example.spec"], spec=SPEC.replace("2.0.0", "1.9.0"))

    def test_rejects_duplicate_version(self):
        with self.assertRaises(ValueError):
            self.check(["packages/example/example.spec"], spec=SPEC + "Version: 2.0.0\n")

    def test_skips_version_for_manual_proposal(self):
        self.assertIn("manual", self.check(["packages/example/livecheck-update.txt"], spec="", proposal=True))


class PatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run_git("init", "-q")
        self.run_git("config", "user.email", "test@example.com")
        self.run_git("config", "user.name", "Test")
        (self.root / "packages/example").mkdir(parents=True)
        (self.root / ".github/scripts").mkdir(parents=True)
        (self.root / "packages/example/example.spec").write_text(SPEC)
        (self.root / "README.md").write_text("original\n")
        (self.root / ".github/scripts/verify-update.py").write_text("trusted\n")
        self.run_git("add", ".")
        self.run_git("commit", "-qm", "base")

    def run_git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root)

    def verify_patch(self):
        self.run_git("add", "-A")
        patch = self.root / "changes.patch"
        patch.write_bytes(self.run_git("diff", "--cached", "--binary"))
        self.run_git("reset", "--hard", "-q", "HEAD")
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("verify-update.py").resolve()),
                                 "example", "2.0.0", str(patch)], cwd=self.root, capture_output=True)
        self.assertEqual((self.root / ".github/scripts/verify-update.py").read_text(), "trusted\n")
        self.assertEqual(self.run_git("diff", "--cached"), b"")
        return result

    def test_accepts_valid_patch(self):
        (self.root / "packages/example/new file").write_text("ok")
        self.assertEqual(self.verify_patch().returncode, 0)

    def test_rejects_verifier_replacement(self):
        (self.root / ".github/scripts/verify-update.py").write_text("malicious\n")
        self.assertNotEqual(self.verify_patch().returncode, 0)

    def test_rejects_move_from_outside(self):
        os.rename(self.root / "README.md", self.root / "packages/example/README.md")
        self.assertNotEqual(self.verify_patch().returncode, 0)

    def test_rejects_symlink(self):
        (self.root / "packages/example/link").symlink_to("../../README.md")
        self.assertNotEqual(self.verify_patch().returncode, 0)

    def test_rejects_traversal_patch(self):
        patch = self.root / "evil.patch"
        patch.write_text("diff --git a/../escape b/../escape\nnew file mode 100644\n"
                         "--- /dev/null\n+++ b/../escape\n@@ -0,0 +1 @@\n+bad\n")
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("verify-update.py").resolve()),
                                 "example", "2.0.0", str(patch)], cwd=self.root, capture_output=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
