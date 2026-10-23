#!/usr/bin/env python3
"""生成 GitHub Pages 站点到 _site/。

路由与生成的文件：
  /            -> index.html
  /list        -> list.html          （Pages 会把 /list 解析到 list.html）
  /post/<slug> -> post/<slug>.html
  其它路径     -> 404.html           （同一个页面，前端显示"文章不存在"）
  /Blog.dc.html#...                  -> 跳转到新地址，兼容旧链接

用法：BASE_PATH=/blog python3 scripts/build_site.py
BASE_PATH 不传时为 /，用于本地预览：npx serve _site
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

import update_manifest

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
OUT = ROOT / "_site"

REDIRECT_STUB = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>Henry Blog</title>
<script>window.location.replace("./" + window.location.hash);</script>
<meta http-equiv="refresh" content="0; url=./">
</head>
<body></body>
</html>
"""


def slug_of(md: Path) -> str:
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", md.stem)


def main() -> None:
    base = "/" + os.environ.get("BASE_PATH", "").strip("/")
    base = base.rstrip("/") + "/"

    update_manifest.main()

    shell = (ROOT / "Blog.dc.html").read_text(encoding="utf-8")
    shell = shell.replace("<head>", f'<head>\n<meta name="blog-base" content="{base}">', 1)

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "posts").mkdir(parents=True)
    (OUT / "post").mkdir()

    posts = sorted(POSTS_DIR.glob("*.md"))
    slugs = [slug_of(p) for p in posts]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup:
        raise SystemExit(f"duplicate slugs: {sorted(dup)}")

    pages = ["index.html", "list.html", "404.html"] + [f"post/{s}.html" for s in slugs]
    for page in pages:
        (OUT / page).write_text(shell, encoding="utf-8")

    (OUT / "Blog.dc.html").write_text(REDIRECT_STUB, encoding="utf-8")
    shutil.copy(ROOT / "support.js", OUT / "support.js")
    shutil.copy(POSTS_DIR / "manifest.json", OUT / "posts" / "manifest.json")
    for p in posts:
        shutil.copy(p, OUT / "posts" / p.name)
    (OUT / ".nojekyll").touch()

    print(f"built {OUT} (base={base}, {len(slugs)} posts)")


if __name__ == "__main__":
    main()
