# 学术科研导航

这是从旧 WordPress 导航站迁移而来的 WebStack-Hugo 静态网站。导航数据位于 `data/webstack.yml`，包含 42 条链接；其中 1 条没有原始分类关系，归入“其他”。

## 本地预览

本项目使用 Git 子模块保存主题。首次克隆后，在项目根目录运行：

```bash
git submodule update --init --recursive
```

已验证的构建版本为 Hugo `0.166.0` extended。安装该版本后运行：

```bash
hugo server --disableFastRender
```

浏览器打开命令输出的本地地址即可预览。

## 更新导航数据

原始 WordPress SQL 备份位于项目同级目录，不能提交到 Git。使用隔离的 Python 环境重新导入数据：

```bash
python3 -m venv .migration/venv
.migration/venv/bin/python -m pip install -r tools/requirements.txt
.migration/venv/bin/python tools/import_wordpress.py ../db_daohang_bilunton_20241218_023001_5m3WTa.sql --output data/webstack.yml
```

备份没有包含 WordPress 上传图片，因此链接不使用旧站 Logo；主题会显示默认图标。

## Cloudflare Pages 部署

以下操作在你的 GitHub 与 Cloudflare 账户中完成：

1. 在 GitHub 创建一个空仓库。
2. 在项目根目录添加该仓库并推送 `main` 分支：

   ```bash
   git remote add origin https://github.com/<你的用户名>/<仓库名>.git
   git push -u origin main
   ```

3. 在 Cloudflare 控制台打开 **Workers & Pages**，创建 Pages 项目并导入该 GitHub 仓库。
4. 设置生产分支为 `main`，构建命令为 `hugo -b $CF_PAGES_URL`，发布目录为 `public`。
5. 将环境变量 `HUGO_VERSION` 设为 `0.166.0`，并在 Production 与 Preview 环境中都配置。

Cloudflare Pages 会在向 `main` 推送后自动构建站点。
