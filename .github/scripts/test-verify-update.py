#!/usr/bin/env python3
"""Offline tests for the staged package-update check."""
import importlib.util
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
