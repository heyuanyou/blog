# Henry Blog

这是一个纯静态个人博客仓库。日常只需要维护 `posts/*.md`。

## 日常流程

1. 在 [posts](/Users/yuanyouhe/projects/blog/posts) 下新增或修改 `.md` 文件
2. `git add . && git commit && git push`
3. 合并到 `main` 后，GitHub Actions 自动构建并发布到 GitHub Pages

## 文章格式

文件名建议带日期，例如：

```text
2026-08-05-my-new-post.md
```

文章内容示例：

```md
---
title: "文章标题"
date: 2026-08-05
main: "语言"
sub: ["golang", "gin"]
summary: "一句话摘要"
---

正文内容
```

## 访问地址

| 页面 | URL |
|---|---|
| 首页 | `https://heyuanyou.github.io/blog/` |
| 文章列表 | `https://heyuanyou.github.io/blog/list`（筛选：`/list?main=面试&sub=mysql`、`?tag=`、`?q=`、`?page=`） |
| 文章 | `https://heyuanyou.github.io/blog/post/<slug>`，slug 为文件名去掉日期前缀和 `.md` |

旧的 `Blog.dc.html#list`、`Blog.dc.html#post/xxx` 链接会自动跳转到新地址。

## 本地启动

用构建产物预览，和线上行为一致（`serve` 支持 `/list` → `list.html` 这种无扩展名路径）：

```bash
python3 scripts/build_site.py   # 生成 _site/，同时更新 posts/manifest.json
npx serve _site
```

然后访问 http://localhost:3000 。

## 自动化

- `scripts/update_manifest.py`：扫描 `posts/*.md` 生成 `posts/manifest.json`
- `scripts/build_site.py`：生成 `_site/`，为首页、列表和每篇文章各生成一个入口页，部署时由 Actions 调用
- `.github/workflows/update-post-manifest.yml`：文章变更后回写仓库里的 `manifest.json`
- `.github/workflows/deploy-pages.yml`：合并到 `main` 后构建并发布到 GitHub Pages
