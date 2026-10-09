#!/usr/bin/env python3
"""Build and smoke-test the Windows x64 npm executable."""

import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    target = sys.argv[1] if len(sys.argv) == 2 else "win32-x64"
    if target != "win32-x64" or sys.platform != "win32" or platform.machine().lower() not in ("amd64", "x86_64"):
        raise SystemExit("Build win32-x64 on Windows x64 with Python x64.")

    output = ROOT / "npm" / "platforms" / target / "bin"
    output.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--name", "wechat-cli", "--noconfirm", "--clean",
        "--distpath", str(output),
        "--workpath", str(ROOT / "build" / target),
        "--specpath", str(ROOT / "build"),
        "--collect-all", "Crypto",
        "--hidden-import", "zstandard",
        str(ROOT / "entry.py"),
    ], cwd=ROOT)

    executable = output / "wechat-cli.exe"
    subprocess.check_call([str(executable), "--version"], cwd=ROOT)
    subprocess.check_call([str(executable), "--help"], cwd=ROOT)
    print(f"Built and checked: {executable.name} ({executable.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
