# Henry Blog

这是一个纯静态个人博客仓库。日常只需要维护 `posts/*.md`。

## 日常流程

1. 在 [posts](/Users/yuanyouhe/projects/blog/posts) 下新增或修改 `.md` 文件
2. `git add . && git commit && git push`
3. GitHub Actions 自动更新 `posts/manifest.json`
4. GitHub Pages 自动发布站点

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
tags: ["Golang", "Gin"]
summary: "一句话摘要"
---

正文内容
```

## 自动化

- [scripts/update_manifest.py](/Users/yuanyouhe/projects/blog/scripts/update_manifest.py:1)
  扫描 `posts/*.md` 并生成 [posts/manifest.json](/Users/yuanyouhe/projects/blog/posts/manifest.json:1)
- [.github/workflows/update-post-manifest.yml](/Users/yuanyouhe/projects/blog/.github/workflows/update-post-manifest.yml:1)
  在文章变更后自动回写 `manifest.json`
- [.github/workflows/deploy-pages.yml](/Users/yuanyouhe/projects/blog/.github/workflows/deploy-pages.yml:1)
  自动发布到 GitHub Pages

## 站点入口

- [index.html](/Users/yuanyouhe/projects/blog/index.html:1)
- [Blog.dc.html](/Users/yuanyouhe/projects/blog/Blog.dc.html:1)
- [support.js](/Users/yuanyouhe/projects/blog/support.js:1)
