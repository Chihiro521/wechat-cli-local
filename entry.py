"""PyInstaller entry point — avoids relative import issues."""
import sys

from wechat_cli.main import cli
from wechat_cli.output.formatter import _ensure_utf8_stream

if __name__ == "__main__":
    _ensure_utf8_stream(sys.stdout)
    _ensure_utf8_stream(sys.stderr)
    cli()
