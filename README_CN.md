# WeChat CLI Local

[![CI](https://github.com/Chihiro521/wechat-cli-local/actions/workflows/ci.yml/badge.svg)](https://github.com/Chihiro521/wechat-cli-local/actions/workflows/ci.yml)

命令行查询、统计和导出本地微信数据，支持 JSON 输出。
本仓库保留本地修改版，npm 独立使用 `wechat-cli-local` 包名。

**[打开中文安装与使用页面](https://chihiro521.github.io/wechat-cli-local/)** · 三步安装、命令复制、使用示例与常见问题。

## 安装

npm 包提供 Windows x64 独立程序，Node.js 22 或更新版本即可，无需安装 Python。
安装：

```powershell
npm install -g wechat-cli-local
wechat-cli --version
wechat-cli --help
```

也可以通过 `wechat-cli-local` 命令调用同一程序。更新：

```powershell
npm update -g wechat-cli-local
```

源码安装需要 Python 3.10 或更新版本：

```powershell
git clone https://github.com/Chihiro521/wechat-cli-local.git
cd wechat-cli-local
python -m pip install -e .
wechat-cli --help
```

npm 发行版当前支持 Windows x64。macOS 的初始化依赖额外的密钥扫描程序，本仓库没有打包该程序。

## 使用

先启动并登录本机微信，然后在有进程读取权限的终端中初始化：

```powershell
wechat-cli init
# 也可以指定数据库目录
wechat-cli init --db-dir "D:\WeChatData\xwechat_files\wxid_example\db_storage"
```

配置、数据库密钥和临时解密文件保存在用户目录 `~/.wechat-cli/`。
目录示例、联系人和群名均为占位内容。

```powershell
wechat-cli sessions --limit 20
wechat-cli contacts --query "张三"
wechat-cli contacts --detail "wxid_example"
wechat-cli history "示例群" --limit 50
wechat-cli history "示例群" --start-time "2026-01-01" --end-time "2026-01-31"
wechat-cli search "关键词" --chat "示例群" --limit 20
wechat-cli members "示例群"
wechat-cli stats "示例群"
wechat-cli favorites --limit 20
wechat-cli unread
wechat-cli new-messages
wechat-cli export "示例群" --format markdown --output "exports/example.md"
```

默认查询输出是 JSON；多数查询支持 `--format text`。用 `wechat-cli <命令> --help` 查看完整参数。
可通过 `--config` 或 `WECHAT_CLI_CONFIG` 指定配置文件。

## 本地构建与验证

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[build]"
.\.venv\Scripts\python -m unittest discover -s tests -v
.\.venv\Scripts\python npm/scripts/check_release.py
.\.venv\Scripts\python npm/scripts/build.py win32-x64
.\.venv\Scripts\python npm/scripts/pack.py --smoke
```

`dist/` 中会生成启动器包和 Windows 二进制包。打包检查限定允许的文件列表，并在隔离目录中安装两个真实压缩包、验证启动器。

## GitHub Actions 与 npm 发布

推送 main 分支或提交 PR 会执行测试、版本一致性检查、Windows 构建和实际 npm 安装验证。
推送 `v版本号` 标签会执行相同验证，然后先发布平台包，再发布启动器包。

首次发布及 npm OIDC 配置见 [发布说明](docs/PUBLISHING.md)。
后续发布先用 `python npm/scripts/set_version.py 0.3.1` 同步所有版本，再提交并推送标签：

```powershell
git add pyproject.toml wechat_cli/main.py npm
git commit -m "Release 0.3.1"
git tag v0.3.1
git push origin main
git push origin v0.3.1
```

## 仓库内容

本地聊天导出 `artifacts/`、账户状态、数据库、密钥、环境配置、截图目录、缓存和构建产物均被排除。
Git 仓库只收录源码、文档、许可证、测试和发布配置。npm 压缩包使用明确的文件白名单。

## 来源与许可证

本项目包含 [WeChat CLI](https://github.com/huohuoer/wechat-cli) 的修改版代码，原仓库曾使用 `freestylefly/wechat-cli` 地址。
上游基于 [wechat-decrypt](https://github.com/ylytdeng/wechat-decrypt) 提供数据库解密和解析能力。

本地修改包含 Windows 数据目录识别、独立包命名和发布流程。详见 [NOTICE](NOTICE) 与 [Apache-2.0 许可证](LICENSE)。
