"""Pack allowlisted release files and test installation of the actual tarballs."""

import argparse
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

from check_release import PACKAGES, ROOT, check


def verify_archive(filename, binary=False):
    required = {"package/package.json", "package/LICENSE", "package/NOTICE", "package/README.md"}
    required.add("package/bin/wechat-cli.exe" if binary else "package/bin/wechat-cli.js")
    with tarfile.open(filename, "r:gz") as archive:
        members = archive.getmembers()
        if {m.name for m in members} != required or any(not m.isfile() for m in members):
            raise ValueError(f"Unexpected or missing files in {filename.name}.")
        if binary and archive.extractfile("package/bin/wechat-cli.exe").read(2) != b"MZ":
            raise ValueError("Platform package does not contain a Windows executable.")
    print(f"Verified {filename.name}: {len(required)} allowed files")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    version = check()
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    node = shutil.which("node")
    if not npm or not node:
        raise SystemExit("Node.js and npm are required.")
    destination = ROOT / "dist"
    destination.mkdir(exist_ok=True)
    tarballs = []
    for index, package in enumerate(PACKAGES):
        for filename in ("LICENSE", "NOTICE", "README.md"):
            shutil.copyfile(ROOT / filename, package / filename)
        result = subprocess.run([npm, "pack", "--json", "--pack-destination", str(destination)],
                                cwd=package, text=True, capture_output=True, check=True)
        metadata = json.loads(result.stdout)[0]
        tarball = destination / metadata["filename"]
        verify_archive(tarball, binary=index == 1)
        tarballs.append(tarball)
    if args.smoke:
        with tempfile.TemporaryDirectory(prefix="wechat-cli-install-") as temporary:
            subprocess.check_call([npm, "install", "--prefix", temporary, "--no-save",
                                   "--package-lock=false", "--ignore-scripts", "--no-audit", "--no-fund",
                                   *[str(p) for p in reversed(tarballs)]])
            main_manifest = json.loads((PACKAGES[0] / "package.json").read_text(encoding="utf-8"))
            launcher = Path(temporary) / "node_modules" / main_manifest["name"] / "bin/wechat-cli.js"
            result = subprocess.check_output([node, str(launcher), "--version"], text=True)
            if result.strip() != f"wechat-cli, version {version}":
                raise ValueError("Installed launcher reported an unexpected version.")
            help_output = subprocess.check_output([node, str(launcher), "--help"]).decode("utf-8")
            if "微信" not in help_output or "new-messages" not in help_output:
                raise ValueError("Installed launcher did not return complete UTF-8 help.")
            print("Installed tarballs passed launcher smoke tests.")


if __name__ == "__main__":
    main()
