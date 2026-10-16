import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate = load_script("validate", "validate.py")
check_nvr = load_script("check_nvr", "check_nvr.py")
changed_packages = load_script("changed_packages", "changed_packages.py")


class ValidationTests(unittest.TestCase):
    def fixture(self, root: Path) -> Path:
        package = root / "demo"
        package.mkdir()
        (package / "demo.spec").write_text("Name: demo\nSource0: source.tar.gz\n", encoding="utf-8")
        (package / "source.tar.gz").write_text("source", encoding="utf-8")
        return package

    def test_srpm_build_uses_temporary_copy_and_preserves_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.fixture(root)
            original = {p.name: p.read_bytes() for p in package.iterdir()}

            def fake_run(command, *, cwd=None, capture=False):
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

    def test_rejects_multiple_srpms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = self.fixture(root)

            def fake_run(command, *, cwd=None, capture=False):
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
        with patch.object(check_nvr, "git", side_effect=RuntimeError("dubious ownership")) as git:
            with self.assertRaisesRegex(RuntimeError, "dubious ownership"):
                check_nvr.check("base")
        git.assert_called_once_with("merge-base", "base", "HEAD")

    def test_release_values_require_literal_fields(self):
        self.assertEqual(check_nvr.spec_values("Version: 1.2\nRelease: 3%{?dist}\n"),
                         ("1.2", "3%{?dist}"))
        with self.assertRaises(ValueError):
            check_nvr.spec_values("Version: 1\n")

    def test_initial_release_reset_requires_same_version_release_one_and_marker(self):
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

    def test_initial_release_reset_is_not_reusable_after_it_lands(self):
        spec = (
            "Version: 1.7.12\nRelease: 1%{?dist}\n%changelog\n"
            f"- {check_nvr.INITIAL_RELEASE_RESET_MARKER}\n"
        )
        self.assertFalse(check_nvr.is_authorized_initial_release_reset(spec, spec))

    def test_check_accepts_verified_initial_release_reset(self):
        current = (
            "Version: 1.7.12\nRelease: 1%{?dist}\n%changelog\n"
            f"- {check_nvr.INITIAL_RELEASE_RESET_MARKER}\n"
        )
        previous = "Version: 1.7.12\nRelease: 2%{?dist}\n"
        outputs = iter(("mergebase", "packages/actionlint/actionlint.spec", current, previous))
        with patch.object(check_nvr, "git", side_effect=lambda *args, **kwargs: next(outputs)):
            with patch.object(check_nvr, "rpmvercmp", return_value=-1):
                self.assertEqual(check_nvr.check("base"), 0)

    def test_changed_package_selection_ignores_readme_and_includes_shared_changes(self):
        with patch.object(changed_packages, "package_names", return_value=["demo", "other"]):
            with patch.object(changed_packages, "git", return_value="packages/demo/README.md\n"):
                self.assertEqual(changed_packages.changed_packages("base"), [])
            with patch.object(changed_packages, "git", return_value=".copr/Makefile\n"):
                self.assertEqual(changed_packages.changed_packages("base"), ["demo", "other"])
            with patch.object(changed_packages, "git", return_value="packages/other/other.spec\n"):
                self.assertEqual(changed_packages.changed_packages("base"), ["other"])

    def test_initial_push_selects_all_packages(self):
        with patch.object(changed_packages, "package_names", return_value=["demo"]):
            self.assertEqual(changed_packages.changed_packages("0" * 40), ["demo"])


if __name__ == "__main__":
    unittest.main()
