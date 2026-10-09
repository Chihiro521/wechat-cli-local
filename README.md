# WeChat CLI Local

[![CI](https://github.com/Chihiro521/wechat-cli-local/actions/workflows/ci.yml/badge.svg)](https://github.com/Chihiro521/wechat-cli-local/actions/workflows/ci.yml)

Query, search, analyze and export local WeChat data from the command line.
This distribution preserves local modifications and uses its own npm package name.

[中文文档与完整命令示例](README_CN.md)

[Chinese installation guide](https://chihiro521.github.io/wechat-cli-local/) — setup steps, copyable commands, usage examples and FAQs.

## Install

The npm distribution supports Windows x64 and requires Node.js 22 or newer.
It includes a standalone executable; Python is not required.
Install from npm:

```powershell
npm install -g wechat-cli-local
wechat-cli --version
wechat-cli --help
```

Both `wechat-cli` and `wechat-cli-local` launch the same executable.

For source installation (Python 3.10 or newer):

```powershell
git clone https://github.com/Chihiro521/wechat-cli-local.git
cd wechat-cli-local
python -m pip install -e .
```

The macOS key-scanning helper is not included in this distribution.

## Usage

Start WeChat, then initialize in a terminal with process-read permissions:

```powershell
wechat-cli init
wechat-cli sessions --limit 20
wechat-cli contacts --query "Example"
wechat-cli history "Example group" --limit 50
wechat-cli search "keyword" --chat "Example group"
wechat-cli members "Example group"
wechat-cli stats "Example group"
wechat-cli favorites
wechat-cli unread
wechat-cli new-messages
wechat-cli export "Example group" --format markdown --output "exports/example.md"
```

Configuration, keys and temporary decrypted files live in `~/.wechat-cli/`.
Queries default to JSON. Use `wechat-cli <command> --help` for all options.
`--config` and `WECHAT_CLI_CONFIG` select a custom configuration file.
All names and paths in documentation are placeholders.

## Build and release

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[build]"
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python npm/scripts/check_release.py
.\.venv\Scripts\python npm/scripts/build.py win32-x64
.\.venv\Scripts\python npm/scripts/pack.py --smoke
```

CI tests each main push and pull request, builds the executable and installs the actual npm tarballs in a temporary directory.
A `v*` tag runs the same checks, then publishes the platform package before the launcher using npm OIDC.
See [publishing setup](docs/PUBLISHING.md) for the first publication and authorization.
Update all version fields with `python npm/scripts/set_version.py 0.3.1` before tagging.

Local exports, account state, keys, databases, screenshots and caches are excluded from Git.
The npm packages use file allowlists and contain only the launcher or executable plus package metadata and license documentation.

## Attribution

Contains modified code from [WeChat CLI](https://github.com/huohuoer/wechat-cli), formerly referenced as `freestylefly/wechat-cli`.
The upstream project credits [wechat-decrypt](https://github.com/ylytdeng/wechat-decrypt) for database decryption and parsing.
Local changes include Windows directory detection, independent package naming and publication automation.

[Apache-2.0](LICENSE) · [NOTICE](NOTICE)
