"""输出格式化 — JSON (大模型友好) / Text (人类可读)。"""

import json
import sys


def _ensure_utf8_stream(file):
    """Use UTF-8 for real console/stdout streams on Windows when possible."""
    if file in (sys.stdout, sys.stderr) and hasattr(file, "reconfigure"):
        enc = (getattr(file, "encoding", "") or "").lower().replace("_", "-")
        if enc not in ("utf-8", "utf8"):
            try:
                file.reconfigure(encoding="utf-8", errors="replace")
            except (AttributeError, OSError, ValueError):
                pass
    return file


def output_json(data, file=None):
    file = _ensure_utf8_stream(file or sys.stdout)
    json.dump(data, file, ensure_ascii=False, indent=2)
    file.write("\n")


def output_text(text, file=None):
    file = _ensure_utf8_stream(file or sys.stdout)
    file.write(text)
    if not text.endswith("\n"):
        file.write("\n")


def output(data, fmt="json", file=None):
    if fmt == "json":
        output_json(data, file)
    else:
        if isinstance(data, str):
            output_text(data, file)
        elif isinstance(data, dict) and "text" in data:
            output_text(data["text"], file)
        else:
            output_json(data, file)
