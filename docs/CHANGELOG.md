## [2026-09-21 13:08] 移除不需要的导航链接

- **需求/问题描述**：
  > 移除“百度一下”和“百度汉语”两个导航条目。

- **实际实现的功能与改动**：
  - 从“其他”分组移除两个条目，并在导入规则中排除其标题，避免以后从同一备份重导时重新出现。
  - 将真实数据测试更新为 42 条链接，验证两个条目不再存在且“其他”仅保留“中国知网个人查重”。
  - [测试/验证]：2 项真实数据测试通过；Hugo `v0.166.0+extended` 构建成功，生成页面不含两个已移除链接的 URL。

- **涉及文件**：
  - `data/webstack.yml` (+0 / -6)
  - `tools/import_wordpress.py` (+7)
  - `tools/test_import_wordpress.py` (+4 / -2)
  - `README.md` (+1 / -1)
  - `docs/CHANGELOG.md` (+20)

- **Git 提交**：`fe536fb fix: remove unwanted navigation links`

---

## [2026-09-21 12:56] 加固迁移站点交付

- **需求/问题描述**：
  > 复核 WebStack-Hugo 迁移结果，确保主题兼容，并完善部署指南。

- **实际实现的功能与改动**：
  - 将 4 个旧版 Font Awesome 图标转换为主题内置的 5.15.4 图标，并用真实备份测试固定转换结果、无分类链接顺序和提交的数据文件内容。
  - 显式以空天气 key 关闭天气组件，避免页面加载无效外部脚本；移除继承的 GitHub Pages 工作流，防止它自动更新主题、提交并推送到 `main`。
  - 补充子模块初始化步骤，并将 Cloudflare Pages 的 Hugo 版本固定为已验证的 `0.166.0`。
  - [测试/验证]：`tools/test_import_wordpress.py` 的 2 项真实数据测试通过；Hugo `v0.166.0+extended` 构建成功，生成页面含 44 条链接、兼容图标且不加载天气组件。上游主题仍使用已弃用的 `.Site.Data` 接口，当前 Hugo 版本仅输出兼容性警告。

- **涉及文件**：
  - `config.toml` (+3)
  - `data/webstack.yml` (+4 / -4)
  - `tools/import_wordpress.py` (+7 / -1)
  - `tools/test_import_wordpress.py` (+19)
  - `.github/workflows/HugoAction.yml` (-46)
  - `README.md` (+8 / -2)
  - `docs/CHANGELOG.md` (+22)

- **Git 提交**：`feb830b fix: harden migrated site configuration`；`d8abf8c chore: remove upstream deployment workflow`

---

## [2026-09-21 12:44] 迁移 WordPress 导航数据到 WebStack-Hugo

- **需求/问题描述**：
  > 从旧 WordPress 数据库提取导航信息，整理成 WebStack-Hugo 项目，并提供 Cloudflare Pages 部署指南。

- **实际实现的功能与改动**：
  - 从 SQL 备份导入 44 条导航链接，保留标题、链接、描述、分类图标与排序；12 个原始分类直接迁移，3 条没有分类关系的链接归入“其他”。
  - 新增可重复运行的 `sqlglot` 与 PyYAML 转换工具及真实备份测试。
  - 更新站点名称，移除上游站点的统计标识和天气 API 配置，添加本地预览、数据更新与 Cloudflare Pages 操作说明。
  - [测试/验证]：`tools/test_import_wordpress.py` 运行 2 项真实数据测试并通过；Hugo `v0.166.0+extended` 构建成功，生成 `public/index.html`，页面包含“论文查重”及 `https://cx.cnki.net/main.html#/login`。上游主题仍使用已弃用的 `.Site.Data` 接口，Hugo 当前版本输出兼容性警告。

- **涉及文件**：
  - `.gitignore` (+4)
  - `config.toml` (+15 / -20)
  - `data/webstack.yml` (+798 / -627)
  - `tools/import_wordpress.py` (+135)
  - `tools/requirements.txt` (+2)
  - `tools/test_import_wordpress.py` (+44)
  - `README.md` (+36 / -7)
  - `docs/CHANGELOG.md` (+24)

- **Git 提交**：`809eeca chore: initialize webstack hugo site`；`00ba95e feat: import wordpress navigation data`；`b457e81 docs: add site deployment guide`；`2872c1b fix: configure current hugo build`

---
