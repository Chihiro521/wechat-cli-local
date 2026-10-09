# npm 首次发布和自动发包

包名：`wechat-cli-local` 和 `wechat-cli-local-win32-x64`。
仓库：`Chihiro521/wechat-cli-local`。
流水线文件：`publish.yml`。

## 首次设置

1. 注册 npm 账号并在本机执行 `npm login --registry=https://registry.npmjs.org/`。
2. 按 README 构建、打包并验证，在项目根目录执行 `python npm/scripts/publish.py` 完成首次发布。npm 可能要求浏览器验证。
3. 对两个 npm 包分别配置 GitHub Actions Trusted Publisher：用户 `Chihiro521`、仓库 `wechat-cli-local`、工作流文件 `publish.yml`，允许 `npm publish`，环境名称留空。
4. 配置后发布一个新版本标签，检查 GitHub Actions 的实际发包结果。首次 OIDC 发布需在创建配置的两天内完成。

可以在每个包的 npm 页面 Settings 中设置 Trusted Publisher。
支持 `npm trust` 的 npm CLI（11.15.0 或更新版本）也可以运行以下命令；账号需启用双因素认证，可能弹出浏览器验证：

```powershell
npm trust github wechat-cli-local-win32-x64 --repo Chihiro521/wechat-cli-local --file publish.yml --allow-publish --yes
npm trust github wechat-cli-local --repo Chihiro521/wechat-cli-local --file publish.yml --allow-publish --yes
```

流水线使用 Node.js 24 和固定版本 npm，通过 OIDC 发包。GitHub 仓库无需配置长期 npm token。
首次 npm 授权与包的 Trusted Publisher 配置完成前，标签流水线的发布步骤会返回授权错误。

## 后续发布

```powershell
python npm/scripts/set_version.py 0.3.1
python npm/scripts/check_release.py v0.3.1
git add pyproject.toml wechat_cli/main.py npm
git commit -m "Release 0.3.1"
git tag v0.3.1
git push origin main
git push origin v0.3.1
```

发布工作流会测试、构建、检查压缩包、实际安装验证，然后依次发布 Windows 包和启动器包。
如仅部分包发布成功，可以重新运行工作流；已存在的版本会跳过。
也可以从 Actions 手动运行 `Publish npm` 并输入已有版本标签。

仓库和 npm 包均公开，npm OIDC 发布会自动生成来源证明。

官方参考：[npm Trusted Publishing](https://docs.npmjs.com/trusted-publishers/)、[npm trust](https://docs.npmjs.com/cli/v11/commands/npm-trust/)。
