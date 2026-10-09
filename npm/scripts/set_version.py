"""Synchronize Python, CLI and npm release versions."""

import json
import re
import sys

from check_release import PACKAGES, ROOT, check


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
        raise SystemExit("Usage: python npm/scripts/set_version.py major.minor.patch")
    version = sys.argv[1]
    for filename, pattern, replacement in [
        (ROOT / "pyproject.toml", r'^version = "[^\"]+"$', f'version = "{version}"'),
        (ROOT / "wechat_cli/main.py", r'^_VERSION = "[^\"]+"$', f'_VERSION = "{version}"'),
    ]:
        text, count = re.subn(pattern, replacement, filename.read_text(encoding="utf-8"), flags=re.M)
        if count != 1:
            raise SystemExit(f"Expected one version field in {filename.name}.")
        filename.write_text(text, encoding="utf-8")
    for package in PACKAGES:
        filename = package / "package.json"
        data = json.loads(filename.read_text(encoding="utf-8"))
        data["version"] = version
        if "optionalDependencies" in data:
            data["optionalDependencies"] = {name: version for name in data["optionalDependencies"]}
        filename.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    check()


if __name__ == "__main__":
    main()
