#!/usr/bin/env python3
"""Offline tests for the advisory source impact report."""
import importlib.util
import io
from pathlib import Path
import tarfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("report", Path(__file__).with_name("livecheck-report.py"))
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


def tar(files):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    return output.getvalue()


class ReportTest(unittest.TestCase):
    def test_comparison_normalizes_root_and_reports_changes(self):
        old = report.archive_files(tar({"project-1/go.mod": b"old", "project-1/LICENSE": b"same", "project-1/src/code": b"old"}))
        new = report.archive_files(tar({"project-2/go.mod": b"new", "project-2/LICENSE": b"same", "project-2/Cargo.lock": b"new"}))
        text = report.report(old, new)
        self.assertIn("changed: `go.mod`", text)
        self.assertIn("added: `Cargo.lock`", text)
        self.assertNotIn("LICENSE`", text)
        self.assertNotIn("src/code", text)
        self.assertIn("removed: `go.mod`", report.report(old, {}))

    def test_zip_and_invalid_paths(self):
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            archive.writestr("package/package.json", "{}")
        self.assertIn("package.json", report.archive_files(output.getvalue()))
        with self.assertRaises(ValueError):
            report.archive_files(tar({"root/../LICENSE": b"bad"}))

    def test_duplicate_normalized_paths_rejected(self):
        with self.assertRaises(ValueError):
            report.archive_files(tar({"one/LICENSE": b"a", "two/LICENSE": b"b"}))


if __name__ == "__main__":
    unittest.main()
