#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_ROOT = Path("/Users/yuanyouhe/projects/blog_src/content")
TARGET_POSTS_DIR = ROOT / "posts"
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)
ALIASES = {
    "go": "golang",
    "postgres": "postgresql",
    "k8s": "kubernetes",
}
MAIN_RULES = [
    ("面试", {"interview"}),
    ("Web3", {"solidity", "ethereum", "wallet", "web3", "blockchain", "crypto", "amm", "trading", "market-making", "hd-wallet", "bip32", "bip39", "bip44"}),
    ("数据库", {"mysql", "postgres", "postgresql", "redis", "database", "sql", "nosql", "cache", "binlog"}),
    ("中间件", {"grpc", "protobuf", "rpc", "kafka", "canal", "cdc", "message-queue", "streaming"}),
    ("分布式", {"raft", "distributed-systems", "microservices", "service-discovery", "consensus", "eureka", "nacos", "consul", "high-availability", "kubernetes", "k8s", "container-orchestration", "stateful", "statefulset"}),
    ("算法", {"algorithm", "data-structure", "linked-list", "circular-queue", "skiplist", "ring-buffer"}),
    ("语言", {"golang", "go", "rust", "programming", "systems-programming", "memory-safety", "concurrency"}),
    ("运维", {"devops", "supervisor", "linux", "gitlab-ci"}),
]
GENERIC_SUB_TAGS = {
    "algorithm",
    "interview",
    "database",
    "distributed-systems",
    "programming",
    "blockchain",
    "crypto",
    "sql",
    "cache",
    "microservices",
}


def parse_frontmatter(text: str) -> tuple[dict[str, str | list[str]], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
      return {}, text

    raw_meta, body = match.groups()
    meta: dict[str, str | list[str]] = {}

    for line in raw_meta.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            items = [
                item.strip().strip("\"'")
                for item in value[1:-1].split(",")
                if item.strip()
            ]
            meta[key] = items
        else:
            meta[key] = value.strip("\"'")

    return meta, body


def slugify_path(path: Path) -> str:
    parts = list(path.parts)
    if parts and parts[0] == "posts":
        parts = parts[1:]
    parts[-1] = path.stem
    slug = "-".join(part.replace("_", "-") for part in parts if part and part != "_index")
    slug = re.sub(r"[^A-Za-z0-9\-]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-").lower()
    return slug


def build_summary(meta: dict[str, str | list[str]], body: str) -> str:
    summary = meta.get("summary")
    if isinstance(summary, str) and summary.strip():
        return summary.strip()

    description = meta.get("description")
    if isinstance(description, str) and description.strip():
        return description.strip()

    for line in body.splitlines():
        text = line.strip()
        if not text or text.startswith("#") or text.startswith(">") or text.startswith("```"):
            continue
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        return text[:140]

    return ""


def format_tags(tags: str | list[str] | None) -> str:
    if isinstance(tags, list):
        return "[" + ", ".join(f'"{tag}"' for tag in tags) + "]"
    if isinstance(tags, str) and tags:
        return f'["{tags}"]'
    return "[]"


def determine_main(tags: list[str]) -> str:
    tag_set = set(tags)
    for main, rules in MAIN_RULES:
        if tag_set & rules:
            return main
    return "其他"


def normalize_sub(tags: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    for tag in tags:
        normalized = ALIASES.get(tag, tag)
        if normalized in GENERIC_SUB_TAGS:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)

    return out


def write_post(source_file: Path) -> None:
    raw = source_file.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)

    raw_date_value = str(meta.get("date", "")).strip()
    date_value = raw_date_value[:10] if len(raw_date_value) >= 10 else "1970-01-01"
    date_prefix = date_value
    slug = slugify_path(source_file.relative_to(SOURCE_ROOT))
    target_file = TARGET_POSTS_DIR / f"{date_prefix}-{slug}.md"

    title = str(meta.get("title", slug)).strip()
    raw_tags = meta.get("tags", [])
    tags = raw_tags if isinstance(raw_tags, list) else [str(raw_tags)] if raw_tags else []
    main = determine_main(tags)
    sub = normalize_sub(tags)
    summary = build_summary(meta, body)

    content = (
        "---\n"
        f'title: "{title.replace(chr(34), chr(92) + chr(34))}"\n'
        f"date: {date_value}\n"
        f'main: "{main}"\n'
        "sub: [" + ", ".join(f'"{tag}"' for tag in sub) + "]\n"
        f'summary: "{summary.replace(chr(34), chr(92) + chr(34))}"\n'
        "---\n\n"
        + body.lstrip()
    )
    target_file.write_text(content, encoding="utf-8")


def main() -> None:
    source_files = sorted(SOURCE_ROOT.joinpath("posts").rglob("*.md"))
    source_files += sorted(SOURCE_ROOT.joinpath("interview").glob("*.md"))
    source_files = [path for path in source_files if path.name != "_index.md"]

    for path in TARGET_POSTS_DIR.glob("*.md"):
        path.unlink()

    for source_file in source_files:
        write_post(source_file)

    print(f"migrated {len(source_files)} legacy posts")


if __name__ == "__main__":
    main()
