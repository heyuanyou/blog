#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
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
            meta[key] = [
                item.strip().strip("\"'")
                for item in value[1:-1].split(",")
                if item.strip()
            ]
        else:
            meta[key] = value.strip("\"'")

    return meta, body


def determine_main(tags: list[str]) -> str:
    tag_set = set(tags)
    for main, rules in MAIN_RULES:
        if tag_set & rules:
            return main
    return "其他"


def normalize_sub(tags: list[str], main: str) -> list[str]:
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


def render_post(meta: dict[str, str | list[str]], body: str) -> str:
    title = str(meta.get("title", "")).strip()
    date = str(meta.get("date", "")).strip()
    summary = str(meta.get("summary", "")).strip()
    raw_tags = meta.get("tags", [])
    tags = raw_tags if isinstance(raw_tags, list) else [str(raw_tags)] if raw_tags else []
    raw_main = str(meta.get("main", "")).strip()
    raw_sub = meta.get("sub", [])
    sub_values = raw_sub if isinstance(raw_sub, list) else [str(raw_sub)] if raw_sub else []
    main = raw_main or determine_main(tags)
    sub = normalize_sub(tags, main) if tags else sub_values

    lines = [
        "---",
        f'title: "{title.replace(chr(34), chr(92) + chr(34))}"',
        f"date: {date}",
        f'main: "{main}"',
        "sub: [" + ", ".join(f'"{tag}"' for tag in sub) + "]",
        f'summary: "{summary.replace(chr(34), chr(92) + chr(34))}"',
        "---",
        "",
        body.lstrip(),
    ]
    return "\n".join(lines)


def main() -> None:
    count = 0
    for post_file in sorted(POSTS_DIR.glob("*.md")):
        raw = post_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        if not meta:
            continue
        post_file.write_text(render_post(meta, body), encoding="utf-8")
        count += 1
    print(f"normalized tags for {count} posts")


if __name__ == "__main__":
    main()
