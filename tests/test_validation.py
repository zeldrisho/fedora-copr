import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, filename: str):
    """Load a repository script as a module without running its CLI entry point."""
    script_path = ROOT / filename if filename.startswith(".github/") else ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate = load_script("validate", "validate.py")
check_nvr = load_script("check_nvr", "check_nvr.py")
select_packages = load_script("select_packages", ".github/scripts/select_packages.py")
check_upstream = load_script("check_upstream", ".github/scripts/check_upstream.py")


class ValidationTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        """Create a demo package with a minimal spec and source file under root."""
        package = root / "demo"
        package.mkdir()
        (package / "demo.spec").write_text("Name: demo\nSource0: source.tar.gz\n", encoding="utf-8")
        (package / "source.tar.gz").write_text("source", encoding="utf-8")
        return package

    def test_srpm_build_uses_temporary_copy_and_preserves_package(self):
        """Verify SRPM validation builds in a copy and preserves package inputs."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.fixture(root)
            original = {p.name: p.read_bytes() for p in package.iterdir()}

            def fake_run(command, *, cwd=None, capture=False):
                """Simulate RPM queries and create a source RPM in the requested output directory."""
                if command[0] == "rpmspec" and "--qf" in command:
                    return "demo\n"
                if command[0] == "make":
                    self.assertNotEqual(cwd, package)
                    self.assertTrue((cwd / "source.tar.gz").is_file())
                    output = Path(command[-1].split("=", 1)[1])
                    (output / "demo-1-1.src.rpm").touch()
                return ""

            with patch.object(validate, "run", side_effect=fake_run):
                with patch.object(validate, "fail", side_effect=AssertionError):
                    validate.validate_package(package, root / "temporary")
            self.assertEqual(original, {p.name: p.read_bytes() for p in package.iterdir()})

    def test_validation_can_retain_srpm_in_package_directory(self):
        """Verify validation retains the SRPM in the requested package output directory."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.fixture(root)
            workspace = root / "workspace"
            output = root / "srpms" / "demo"

            def fake_run(command, *, cwd=None, capture=False):
                """Simulate RPM queries and write an SRPM to the requested output directory."""
                if command[0] == "rpmspec" and "--qf" in command:
                    return "demo\n"
                if command[0] == "make":
                    target = Path(command[-1].split("=", 1)[1])
                    (target / "demo-1-1.src.rpm").touch()
                return ""

            with patch.object(validate, "run", side_effect=fake_run):
                validate.validate_package(package, workspace, output)
            self.assertTrue((output / "demo-1-1.src.rpm").is_file())

    def test_main_uses_fresh_workspace_when_retaining_srpms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package_root = root / "packages"
            package_root.mkdir()
            self.fixture(package_root)
            srpm_root = root / "retained"
            workspaces = []

            def fake_validate(package_dir, workspace, srpm_output=None):
                self.assertEqual(package_dir.name, "demo")
                self.assertNotEqual(workspace, srpm_output)
                self.assertTrue(workspace.is_dir())
                workspaces.append(workspace)
                srpm_output.mkdir(parents=True, exist_ok=True)
                (srpm_output / "demo-1-1.src.rpm").touch()

            for _ in range(2):
                with patch.object(validate, "PACKAGES", package_root), \
                     patch.object(validate, "TOOLS", ()), \
                     patch.object(validate.sys, "argv", ["validate", "--srpm-dir", str(srpm_root)]), \
                     patch.object(validate, "validate_package", side_effect=fake_validate):
                    validate.main()

            self.assertNotEqual(workspaces[0], workspaces[1])
            self.assertTrue(all(not workspace.exists() for workspace in workspaces))
            self.assertTrue((srpm_root / "demo" / "demo-1-1.src.rpm").is_file())

    def test_rejects_multiple_srpms(self):
        """Verify validation rejects a build that produces more than one SRPM."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.fixture(root)

            def fake_run(command, *, cwd=None, capture=False):
                """Simulate RPM queries and create two source RPMs to test rejection."""
                if command[0] == "rpmspec" and "--qf" in command:
                    return "demo\n"
                if command[0] == "make":
                    output = Path(command[-1].split("=", 1)[1])
                    (output / "one.src.rpm").touch()
                    (output / "two.src.rpm").touch()
                return ""

            with patch.object(validate, "run", side_effect=fake_run):
                with patch.object(validate, "fail", side_effect=SystemExit) as fail:
                    with self.assertRaises(SystemExit):
                        validate.validate_package(package, root / "temporary")
            self.assertIn("exactly one SRPM", str(fail.call_args.args[0]))

    def test_merge_base_errors_are_not_hidden(self):
        """Verify Git merge-base failures propagate to the caller."""
        with patch.object(check_nvr, "git", side_effect=RuntimeError("dubious ownership")) as git:
            with self.assertRaisesRegex(RuntimeError, "dubious ownership"):
                check_nvr.check("base")
        git.assert_called_once_with("merge-base", "base", "HEAD")

    def test_release_values_require_literal_fields(self):
        """Verify literal Version and Release fields are required and parsed."""
        self.assertEqual(check_nvr.spec_values("Version: 1.2\nRelease: 3%{?dist}\n"),
                         ("1.2", "3%{?dist}"))
        with self.assertRaises(ValueError):
            check_nvr.spec_values("Version: 1\n")

    def test_initial_release_reset_requires_same_version_release_one_and_marker(self):
        """Verify a reset requires an unchanged Version, Release 1, and the marker."""
        previous = "Version: 1.7.12\nRelease: 2%{?dist}\n"
        authorized = (
            "Version: 1.7.12\nRelease: 1%{?dist}\n%changelog\n"
            f"- {check_nvr.INITIAL_RELEASE_RESET_MARKER}\n"
        )
        self.assertTrue(check_nvr.is_authorized_initial_release_reset(authorized, previous))
        self.assertFalse(check_nvr.is_authorized_initial_release_reset(
            authorized.replace(check_nvr.INITIAL_RELEASE_RESET_MARKER, "Initial release"), previous
        ))
        self.assertFalse(check_nvr.is_authorized_initial_release_reset(
            authorized.replace("Release: 1", "Release: 2"), previous
        ))
        self.assertFalse(check_nvr.is_authorized_initial_release_reset(
            authorized.replace("Version: 1.7.12", "Version: 1.7.13"), previous
        ))

    def check_with(self, current: str, previous: str, evr_comparison: int, files: str = "packages/demo/demo.spec"):
        """Run the EVR check with mocked Git outputs and an RPM comparison result."""
        outputs = iter(("mergebase", files, "", current, previous))
        with patch.object(check_nvr, "git", side_effect=lambda *args, **kwargs: next(outputs)):
            with patch.object(check_nvr, "rpmvercmp", return_value=evr_comparison):
                return check_nvr.check("base")

    def test_packager_only_spec_changes_need_no_bump(self):
        """Verify comments, check commands, and changelog edits need no EVR bump."""
        previous = (
            "Version: 1\nRelease: 1%{?dist}\n%build\nmake\n%check\nmake test\n"
            "%changelog\n* Fri Oct 16 2026 A <a@example.com> - 1-1\n- Old\n"
        )
        current = (
            "Version: 1\nRelease: 1%{?dist}\n# note\n%build\nmake\n%check\nmake check\n"
            "%changelog\n* Fri Oct 16 2026 B <b@example.com> - 1-1\n- Initial package\n"
        )
        self.assertEqual(self.check_with(current, previous, 0), 0)

    def test_packager_only_build_requirement_does_not_change_user_facing_spec(self):
        """Ignore explicitly marked test-only BuildRequires while checking EVR."""
        previous = "Version: 1\nRelease: 1%{?dist}\nBuildRequires: cargo\n"
        current = previous + "# packager-only: BuildRequires\nBuildRequires: procps-ng\n"
        self.assertEqual(check_nvr.user_facing_spec(current), check_nvr.user_facing_spec(previous))

    def test_comment_only_buildrequires_marker_change_needs_no_bump(self):
        """Adding the exemption marker above an existing requirement is comment-only."""
        previous = "Version: 1\nRelease: 1%{?dist}\nBuildRequires: cargo\n"
        current = previous.replace(
            "BuildRequires: cargo", "# packager-only: BuildRequires\nBuildRequires: cargo")
        self.assertEqual(self.check_with(current, previous, 0), 0)

    def test_remote_source_cache_detection_requires_matching_source_url(self):
        """Only classify a matching remote Source archive as a removable cache."""
        spec = ("Name: herdr\nVersion: 0.9.5\nRelease: 1%{?dist}\n"
                "URL: https://example.test/project\n"
                "Source0: %{url}/v%{version}.tar.gz#/%{name}-%{version}.tar.gz\n")
        self.assertTrue(check_nvr.is_remote_source_cache(
            "packages/herdr/herdr-0.9.5.tar.gz", spec))
        self.assertFalse(check_nvr.is_remote_source_cache(
            "packages/herdr/herdr-0.9.5-vendor.tar.gz", spec))
        mismatched_fragment = spec.replace(
            "#/%{name}-%{version}.tar.gz", "#/different.tar.gz")
        self.assertFalse(check_nvr.is_remote_source_cache(
            "packages/herdr/herdr-0.9.5.tar.gz", mismatched_fragment))
        local_source = spec + "Source1: herdr-0.9.5.tar.gz\n"
        self.assertFalse(check_nvr.is_remote_source_cache(
            "packages/herdr/herdr-0.9.5.tar.gz", local_source))

    def test_user_facing_spec_changes_still_need_a_bump(self):
        """Verify a build command change requires an EVR increase."""
        previous = "Version: 1\nRelease: 1%{?dist}\n%build\nmake\n"
        current = "Version: 1\nRelease: 1%{?dist}\n%build\nmake -j1\n"
        self.assertEqual(self.check_with(current, previous, 0), 1)

    def test_other_package_files_still_need_a_bump(self):
        """Verify changes to other package inputs require an EVR increase."""
        spec = "Version: 1\nRelease: 1%{?dist}\n%check\nmake test\n"
        files = "packages/demo/demo.spec\npackages/demo/demo-vendor.tar.bz2"
        self.assertEqual(self.check_with(spec, spec, 0, files), 1)

    def test_deleted_remote_tar_xz_cache_needs_no_bump(self):
        """Recognize deleted remote archives regardless of their extension."""
        spec = (
            "Name: demo\nVersion: 1\nRelease: 1%{?dist}\n"
            "Source0: https://example.test/archive.tar.xz#/demo-1.tar.xz\n"
        )
        deleted = "packages/demo/demo-1.tar.xz"
        outputs = iter(("mergebase", deleted, deleted, spec, spec))
        with patch.object(check_nvr, "git", side_effect=lambda *args, **kwargs: next(outputs)):
            with patch.object(check_nvr, "rpmvercmp", return_value=0):
                self.assertEqual(check_nvr.check("base"), 0)

    def test_package_docs_do_not_require_bump_but_build_inputs_still_do(self):
        """Ignore package docs while preserving checks for real package inputs."""
        spec = "Version: 1\nRelease: 1%{?dist}\n%build\nmake\n"
        docs = "packages/demo/docs/audit.md\npackages/demo/docs/review.md"
        self.assertEqual(self.check_with(spec, spec, 0, docs), 0)
        mixed = docs + "\npackages/demo/demo-vendor.tar.bz2"
        self.assertEqual(self.check_with(spec, spec, 0, mixed), 1)

    def test_initial_release_reset_is_not_reusable_after_it_lands(self):
        """Verify an existing reset marker cannot authorize another reset."""
        spec = (
            "Version: 1.7.12\nRelease: 1%{?dist}\n%changelog\n"
            f"- {check_nvr.INITIAL_RELEASE_RESET_MARKER}\n"
        )
        self.assertFalse(check_nvr.is_authorized_initial_release_reset(spec, spec))

    def test_check_accepts_verified_initial_release_reset(self):
        """Verify the EVR check accepts a newly authorized initial-release reset."""
        current = (
            "Version: 1.7.12\nRelease: 1%{?dist}\n%changelog\n"
            f"- {check_nvr.INITIAL_RELEASE_RESET_MARKER}\n"
        )
        previous = "Version: 1.7.12\nRelease: 2%{?dist}\n"
        outputs = iter(("mergebase", "packages/actionlint/actionlint.spec", "", current, previous))
        with patch.object(check_nvr, "git", side_effect=lambda *args, **kwargs: next(outputs)):
            with patch.object(check_nvr, "rpmvercmp", return_value=-1):
                self.assertEqual(check_nvr.check("base"), 0)

    def test_upstream_version_comparison_handles_numeric_components(self):
        """Verify numeric version ordering, optional v prefixes, and empty-tag rejection."""
        self.assertGreater(check_upstream.version_key("v1.10.0"), check_upstream.version_key("1.9.9"))
        self.assertEqual(check_upstream.version_key("v2.0.0"), check_upstream.version_key("2.0.0"))
        self.assertEqual(check_upstream.version_key("1.2"), check_upstream.version_key("1.2.0"))
        self.assertLess(check_upstream.version_key("1.2.3rc1"), check_upstream.version_key("1.2.3"))
        self.assertLess(check_upstream.version_key("1.2.3-rc.1"), check_upstream.version_key("1.2.3"))
        with self.assertRaises(ValueError):
            check_upstream.version_key("v")

    def test_explicit_package_selection_is_sorted_and_validated(self):
        """Validate explicit manual COPR package selections."""
        available = ["actionlint", "herdr", "yazi"]
        self.assertEqual(select_packages.selected_packages("yazi, herdr,herdr", available),
                         ["herdr", "yazi"])
        with self.assertRaisesRegex(ValueError, "unknown package.*missing"):
            select_packages.selected_packages("herdr,missing", available)
        with self.assertRaisesRegex(ValueError, "at least one package"):
            select_packages.selected_packages(" , ", available)


if __name__ == "__main__":
    unittest.main()
