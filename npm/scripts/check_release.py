"""Check release metadata before building or publishing."""

import ast
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = [ROOT / "npm/wechat-cli", ROOT / "npm/platforms/win32-x64"]


def check(tag=None):
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Release versions must use major.minor.patch.")
    if tag is not None and tag != f"v{version}":
        raise ValueError(f"Tag {tag!r} does not match package version v{version}.")
    manifests = [json.loads((p / "package.json").read_text(encoding="utf-8")) for p in PACKAGES]
    for manifest in manifests:
        if manifest["version"] != version:
            raise ValueError(f"Version mismatch in {manifest['name']}.")
        if manifest["repository"]["url"] != "git+https://github.com/Chihiro521/wechat-cli-local.git":
            raise ValueError("Package repository does not match the publishing repository.")
    if manifests[0]["optionalDependencies"] != {manifests[1]["name"]: version}:
        raise ValueError("Launcher dependency does not match the platform package.")
    tree = ast.parse((ROOT / "wechat_cli/main.py").read_text(encoding="utf-8"))
    cli_versions = [ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "_VERSION" for t in n.targets)]
    if cli_versions != [version]:
        raise ValueError("CLI version does not match package version.")
    print(f"Release metadata verified: {version}")
    return version


if __name__ == "__main__":
    check(sys.argv[1] if len(sys.argv) > 1 else None)
