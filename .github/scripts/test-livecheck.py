#!/usr/bin/env python3
"""Offline provider, source detection, version, and transactional-update tests."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

module = importlib.util.spec_from_file_location("livecheck", Path(__file__).with_name("livecheck.py"))
livecheck = importlib.util.module_from_spec(module)
module.loader.exec_module(livecheck)


class LivecheckTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.package = Path(self.tmp.name) / "example"
        self.package.mkdir()
        self.spec = self.package / "example.spec"
        self.source = "https://github.com/example/project/archive/refs/tags/v%{version}.tar.gz"
        self.create_package()

    def create_package(self, source=None, *, version="1.2.3", extra="", manifest=None):
        self.spec.write_text(
            f"Name: example\nVersion: {version}\nRelease: 2%{{?dist}}\n"
            f"URL: https://github.com/example/project\nSource0: {source or self.source}\n"
            f"{extra}%changelog\n"
        )
        for name in ("source.sha256", "checksums.sha256"):
            (self.package / name).unlink(missing_ok=True)
        path = self.package / ("checksums.sha256" if manifest is not None else "source.sha256")
        path.write_text(manifest if manifest is not None else "0" * 64 + "\n")

    def run_update(self, metadata=None, *, fail_suffix=None, fallback_tags=None):
        plan = livecheck.inspect_package(self.package)
        metadata = metadata if metadata is not None else {"tag_name": "v1.2.4"}
        urls = []

        def fetch(request, timeout):
            url = request.full_url if hasattr(request, "full_url") else request
            urls.append(url)
            if url.startswith("https://api.github.com/"):
                self.assertEqual(request.get_header("Authorization"), "Bearer test-token")
                if url.endswith("/releases/latest") and fallback_tags is not None:
                    raise urllib.error.HTTPError(url, 404, "no releases", {}, None)
                body = fallback_tags if "/tags?" in url else metadata
                return io.BytesIO(json.dumps(body).encode())
            if url.startswith("https://registry.npmjs.org/") and url.endswith("/latest"):
                self.assertIsNone(request.get_header("Authorization"))
                return io.BytesIO(json.dumps(metadata).encode())
            self.assertIsInstance(request, str, "API credentials must not reach source downloads")
            if fail_suffix and url.endswith(fail_suffix):
                raise OSError("source not available yet")
            return io.BytesIO(url.encode())

        self.urls = urls
        with patch.dict(os.environ, {"GH_TOKEN": "test-token", "GITHUB_OUTPUT": str(self.package / "output")}), \
             patch("urllib.request.urlopen", side_effect=fetch), contextlib.redirect_stdout(io.StringIO()):
            result = livecheck.update(plan)
        return result

    def assert_download(self, url, name=None):
        self.assertIn(url, self.urls)
        expected = hashlib.sha256(url.encode()).hexdigest()
        checksum = self.package / ("checksums.sha256" if name else "source.sha256")
        self.assertIn(expected + ("  " + name if name else "\n"), checksum.read_text())

    def test_coordinated_packages_are_discoverable(self):
        root = Path(__file__).resolve().parents[2] / "packages"
        for name, provider, count in [
            ("kotlin-toolchain", ("github", "JetBrains/kotlin-toolchain"), 2),
            ("morphe", ("github", "MorpheApp/morphe-desktop"), 5),
            ("pi-coding-agent", ("npm", "@earendil-works/pi-coding-agent"), 15),
            ("vite-plus", ("github", "voidzero-dev/vite-plus"), 3),
        ]:
            with self.subTest(package=name):
                plan = livecheck.inspect_package(root / name)
                self.assertEqual(plan["provider"], provider)
                self.assertEqual(len(plan["tracked"]), count)
                self.assertNotIn("manual", plan)

    def test_github_archive(self):
        self.assertEqual(self.run_update(), "1.2.4")
        self.assertEqual(self.urls[0], "https://api.github.com/repos/example/project/releases/latest")
        self.assert_download("https://github.com/example/project/archive/refs/tags/v1.2.4.tar.gz")
        self.assertIn("Release: 1%{?dist}", self.spec.read_text())
        self.assertEqual((self.package / "output").read_text(), "version=1.2.4\n")

    def test_npm_and_scoped_npm(self):
        for name in ("example", "@scope/example"):
            with self.subTest(name=name):
                source = f"https://registry.npmjs.org/{name}/-/example-%{{version}}.tgz"
                self.create_package(source)
                self.assertEqual(self.run_update({"name": name, "version": "1.2.4"}), "1.2.4")
                self.assert_download(f"https://registry.npmjs.org/{name}/-/example-1.2.4.tgz")

    def manifest_package(self):
        # Arbitrary HTTPS distribution host: no package/repository-specific branch.
        self.create_package(
            "https://downloads.example.org/engine/%{version}/engine-%{version}.tgz",
            extra="Source1: https://raw.githubusercontent.com/example/project/v%{version}/LICENSE\n"
                  "Source2: https://cdn.example.org/releases/%{version}/NOTICE\n",
            manifest="".join("0" * 64 + "  " + name + "\n" for name in ("engine-1.2.3.tgz", "LICENSE", "NOTICE")),
        )

    def test_generic_distribution_and_manifest(self):
        self.manifest_package()
        self.assertEqual(self.run_update(), "1.2.4")
        self.assert_download("https://downloads.example.org/engine/1.2.4/engine-1.2.4.tgz", "engine-1.2.4.tgz")
        self.assert_download("https://raw.githubusercontent.com/example/project/v1.2.4/LICENSE", "LICENSE")
        self.assert_download("https://cdn.example.org/releases/1.2.4/NOTICE", "NOTICE")
        self.assertFalse((self.package / "source.sha256").exists())

    def test_two_four_and_calendar_versions(self):
        for current, tag, expected in (("1.2", "v1.3", "1.3"), ("1.2.3.4", "release-1.2.3.5", "1.2.3.5"), ("2026.10", "2026.11", "2026.11")):
            with self.subTest(tag=tag):
                self.create_package(version=current)
                self.assertEqual(self.run_update({"tag_name": tag}), expected)
                self.assertIn(f"Version: {expected}", self.spec.read_text())

    def test_npm_version_not_selected_from_github(self):
        self.create_package("https://registry.npmjs.org/example/-/example-%{version}.tgz")
        self.assertEqual(self.run_update({"name": "example", "version": "2.0"}), "2.0")
        self.assertTrue(self.urls[0].endswith("registry.npmjs.org/example/latest"))

    def test_fallback_to_tags_when_no_releases(self):
        self.assertEqual(self.run_update(fallback_tags=[{"name": "v1.3.0-rc1"}, {"name": "v1.2.10"}, {"name": "v1.2.9"}]), "1.2.10")
        self.assertTrue(self.urls[1].endswith("/tags?per_page=100"))

    def test_same_older_or_trailing_zero_versions_leave_files_unchanged(self):
        for tag in ("v1.2.3", "v1.2.2", "v1.2.3.0"):
            with self.subTest(tag=tag):
                before = self.spec.read_text(), (self.package / "source.sha256").read_text()
                self.assertIsNone(self.run_update({"tag_name": tag}))
                self.assertEqual(len(self.urls), 1)
                self.assertEqual(before, (self.spec.read_text(), (self.package / "source.sha256").read_text()))

    def test_prerelease_or_invalid_versions_rejected(self):
        for metadata in ({"tag_name": "v1.2.4-rc1"}, {"tag_name": "v1.2.4", "draft": True}, {"tag_name": "v1.2.4", "prerelease": True}, {"tag_name": "not-a-version"}):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                self.run_update(metadata)

    def test_manual_marker_and_unknown_layout_rejected_offline(self):
        self.create_package(extra="# livecheck: manual lockfile and license need review\n")
        original = self.spec.read_text()
        self.assertEqual(self.run_update(), "1.2.4")
        self.assertEqual(self.spec.read_text(), original)
        self.assertIn("1.2.4", (self.package / "livecheck-update.txt").read_text())
        self.assertIn("manual=true", (self.package / "output").read_text())
        self.create_package("https://downloads.example.org/%{commit}.tgz")
        with self.assertRaises(ValueError):
            livecheck.inspect_package(self.package)

    def test_auxiliary_versioned_source_cannot_be_ignored(self):
        self.create_package(extra="Source1: https://example.org/%{version}/LICENSE\n")
        with self.assertRaisesRegex(ValueError, "auxiliary"):
            livecheck.inspect_package(self.package)

    def test_remote_schemes_and_local_sources(self):
        for source in ("http://example.org/%{version}/NOTICE", "ftp://example.org/file", "//example.org/file"):
            with self.subTest(source=source):
                self.create_package(extra=f"Source1: {source}\n")
                with self.assertRaisesRegex(ValueError, "Unsupported remote"):
                    livecheck.inspect_package(self.package)
        self.create_package(extra="Source1: %{name}-%{version}-deps.tar.gz\n")
        livecheck.inspect_package(self.package)

    def test_version_field_case_and_duplicates(self):
        self.spec.write_text(self.spec.read_text().replace("Version:", "version:"))
        self.run_update()
        self.assertIn("version: 1.2.4", self.spec.read_text())
        self.create_package(extra="version: 1.2.3\n")
        before = self.spec.read_text(), (self.package / "source.sha256").read_text()
        with self.assertRaisesRegex(ValueError, "exactly one Version"):
            self.run_update()
        self.assertEqual(before, (self.spec.read_text(), (self.package / "source.sha256").read_text()))

    def test_invalid_manifest_and_ambiguous_sources_rejected(self):
        for manifest in ("", "not a manifest\n", "0" * 64 + "  ../escape\n", "0" * 64 + "  missing.tgz\n"):
            with self.subTest(manifest=manifest):
                self.create_package(manifest=manifest)
                with self.assertRaises(ValueError):
                    livecheck.inspect_package(self.package)
        self.manifest_package()
        with self.spec.open("a") as stream:
            stream.write("Source9: https://elsewhere.example/LICENSE\n")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            livecheck.inspect_package(self.package)

    def test_all_downloads_finish_before_files_change(self):
        for suffix in (".tgz", "/LICENSE", "/NOTICE"):
            with self.subTest(suffix=suffix):
                self.manifest_package()
                before = self.spec.read_text(), (self.package / "checksums.sha256").read_text()
                with self.assertRaises(OSError):
                    self.run_update(fail_suffix=suffix)
                self.assertEqual(before, (self.spec.read_text(), (self.package / "checksums.sha256").read_text()))
                self.assertFalse((self.package / "output").exists())

    def test_renamed_sources_and_name_macros(self):
        self.create_package("https://github.com/example/project/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tgz", manifest="0" * 64 + "  example-1.2.3.tgz\n")
        self.run_update()
        self.assert_download("https://github.com/example/project/archive/refs/tags/v1.2.4.tar.gz", "example-1.2.4.tgz")


if __name__ == "__main__":
    unittest.main()
