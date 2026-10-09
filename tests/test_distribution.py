import io
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
from wechat_cli.main import cli

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "npm/scripts"))
from check_release import check
from pack import verify_archive


class DistributionTests(unittest.TestCase):
    def test_help_does_not_initialize_account(self):
        with patch("wechat_cli.main.AppContext", side_effect=AssertionError("Account access")):
            result = CliRunner().invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn("new-messages", result.output)
        self.assertIn("favorites", result.output)

    def test_version_does_not_initialize_account(self):
        with patch("wechat_cli.main.AppContext", side_effect=AssertionError("Account access")):
            result = CliRunner().invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output.strip(), f"wechat-cli, version {check()}")

    def test_tag_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            check("v9999.0.0")

    def _archive(self, additional=None, omit=None, binary=b"MZexample", symlink=False):
        required = {"package/package.json": b"{}", "package/LICENSE": b"example",
                    "package/NOTICE": b"example", "package/README.md": b"example",
                    "package/bin/wechat-cli.exe": binary}
        if additional:
            required.update(additional)
        if omit:
            required.pop(omit)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        filename = Path(temporary.name) / "synthetic.tgz"
        with tarfile.open(filename, "w:gz") as archive:
            for name, data in required.items():
                info = tarfile.TarInfo(name)
                if symlink and name == "package/NOTICE":
                    info.type = tarfile.SYMTYPE
                    info.linkname = "../../example"
                    archive.addfile(info)
                else:
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
        return filename

    def test_allowlisted_archive_passes(self):
        verify_archive(self._archive(), binary=True)

    def test_export_file_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            verify_archive(self._archive({"package/artifacts/example.txt": b"synthetic"}), binary=True)

    def test_missing_binary_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            verify_archive(self._archive(omit="package/bin/wechat-cli.exe"), binary=True)

    def test_symlink_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            verify_archive(self._archive(symlink=True), binary=True)

    def test_non_executable_payload_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Windows executable"):
            verify_archive(self._archive(binary=b"example"), binary=True)


if __name__ == "__main__":
    unittest.main()
