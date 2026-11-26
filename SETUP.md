# GitHub Pages 复盘归档 · 一次性设置

站点内容已全部准备就绪（46 篇复盘 + 列表页 + 自动同步脚本），只差在浏览器里创建仓库并首次推送。

## 你需要做的（约 2 分钟）

### 1. 创建仓库

打开 <https://github.com/new>，按如下填写：

- **Repository name**：`fu-pan-archive`
- **Description**（可选）：A 股短线交易复盘归档
- **Public / Private**：选 **Public**（Free 账户私有仓库无法启用 Pages；即使选私有，Pages 内容也会被公开访问）
- **Initialize this repository with**：**全部不要勾选**（不要加 README、.gitignore、license）
- 点击 **Create repository**

### 2. 回来告诉我

创建完成后，回来发一句「仓库建好了」，我会自动执行首次推送和 Pages 配置检查。

（首次推送时 Git Credential Manager 会弹出 GitHub 登录窗口，在浏览器里完成登录授权即可，之后会记住凭据、每天自动推送无需再登录。）

## 完成后的使用方式

- **站点地址**：<https://rufusvisaber.github.io/fu-pan-archive/>
- 列表页按年月分组、日期倒序，支持搜索和年份筛选，点击任意一条打开当天完整复盘。
- 每个交易日 17:30 的复盘任务生成 HTML 后，会自动复制进归档、重建列表页并推送更新，无需手动操作。
- 手动同步：`cd gh-pages && python sync.py`

## 目录说明

```
gh-pages/
├── index.html          # 列表页（脚本自动生成，勿手动改）
├── sync.py             # 同步脚本
├── posts/              # 46 篇复盘 HTML（自动复制）
└── SETUP.md            # 本说明
```
