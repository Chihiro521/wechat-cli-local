"""Check tracked source for excluded runtime data and credential literals."""

import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
RULES = {
    "credential literal": re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|npm_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{24,})"),
    "private key": re.compile(r"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----"),
    "personal Windows directory": re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+(?!Public(?:[\\/]|$)|Example(?:[\\/]|$))[^\s\"']+", re.I),
    "account identifier": re.compile(r"wxid_(?!example\b|xxx\b)[A-Za-z0-9_]{6,}|\b\d{6,}@chatroom\b"),
}
EXCLUDED = {"artifacts", "exports", "image", ".wechat-cli", "decrypted", "decoded_images", ".local", ".venv", "node_modules", "__pycache__"}


def main():
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8").split("\0")
    failures = []
    count = 0
    for filename in filter(None, files):
        path = PurePosixPath(filename)
        count += 1
        if EXCLUDED.intersection(path.parts) or path.name.startswith(".env") or path.name == ".npmrc" or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".pem", ".key", ".tgz", ".exe", ".png", ".jpg"}:
            failures.append((filename, "excluded file type or directory"))
            continue
        if path.suffix == ".json" and path.name != "package.json":
            failures.append((filename, "unexpected JSON data"))
        content = subprocess.check_output(["git", "show", f":{filename}"], cwd=ROOT).decode("utf-8")
        for rule, pattern in RULES.items():
            if pattern.search(content):
                failures.append((filename, rule))
    if failures:
        for filename, rule in failures:
            print(f"{filename}: {rule}")
        raise SystemExit("Tracked-source audit failed.")
    print(f"Tracked-source audit passed: {count} files; no excluded data or matching literals.")


if __name__ == "__main__":
    main()
