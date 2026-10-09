"""Publish verified release tarballs in dependency order; allow partial retries."""

import json
import os
import shutil
import subprocess

from check_release import PACKAGES, ROOT, check
from pack import verify_archive


def main():
    version = check()
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm")
    if not npm:
        raise SystemExit("npm is required.")
    for package in reversed(PACKAGES):
        data = json.loads((package / "package.json").read_text(encoding="utf-8"))
        name = data["name"]
        tarball = ROOT / "dist" / f"{name.replace('@', '').replace('/', '-')}-{version}.tgz"
        verify_archive(tarball, binary=package == PACKAGES[1])
        result = subprocess.run([npm, "view", f"{name}@{version}", "version", "--json",
                                 "--registry=https://registry.npmjs.org/"],
                                capture_output=True, text=True)
        if result.returncode == 0:
            if json.loads(result.stdout) != version:
                raise SystemExit("Registry returned an unexpected version.")
            print(f"Already published: {name}@{version}")
            continue
        try:
            code = json.loads(result.stdout)["error"]["code"]
        except (ValueError, KeyError, TypeError):
            code = None
        if code != "E404":
            raise SystemExit(f"Could not check registry state for {name} ({code or 'unknown error'}).")
        subprocess.check_call([npm, "publish", str(tarball), "--access=public",
                               "--registry=https://registry.npmjs.org/"])


if __name__ == "__main__":
    main()
