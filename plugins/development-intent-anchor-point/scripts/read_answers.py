#!/usr/bin/env python3
"""Print a readable summary of an exported answers.json file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def mark_for(a: dict) -> str:
    if not a.get("answered"):
        return "○"
    if a.get("type") == "not_needed":
        return "×"
    if a.get("type") == "defer":
        return "→"
    return "✓"


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="以可读格式输出 answers.json 的答案摘要。")
    parser.add_argument("path", help="answers.json 路径")
    args = parser.parse_args()

    path = Path(args.path)
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        sys.exit(f"无法读取 {path}: {exc}")

    answers = data.get("answers")
    if not isinstance(answers, list):
        sys.exit("answers.json 缺少 \"answers\" 数组。")

    print(f"# {data.get('title', '需求确认问卷')}")
    if data.get("savedAt"):
        print(f"保存时间: {data['savedAt']}")
    answered = sum(1 for a in answers if a.get("answered"))
    print(f"已回答: {answered}/{len(answers)}\n")

    groups: dict[str, list] = {}
    for a in answers:
        groups.setdefault(a.get("group") or "通用问题", []).append(a)

    status_names = {
        "option": "选择",
        "multiple": "多选",
        "custom": "自定义",
        "not_needed": "不需要",
        "defer": "后续再定",
    }

    for group, items in groups.items():
        print(f"## {group}")
        for a in items:
            print(f"{mark_for(a)} {a.get('id', '?')} {a.get('question', '')}")
            if not a.get("answered"):
                print("    [未回答]")
                continue
            status = status_names.get(a.get("type"), a.get("type") or "未回答")
            if a.get("type") == "multiple":
                labels = a.get("labels") or []
                if labels:
                    parts = []
                    for item in labels:
                        if isinstance(item, dict):
                            parts.append(item.get("label", "") + (" ★推荐" if item.get("recommended") else ""))
                        else:
                            parts.append(str(item))
                    print(f"    [{status}] {'、'.join(parts)}")
                else:
                    print(f"    [{status}] （未选择任何选项）")
            elif a.get("type") == "custom":
                print(f"    [自定义] {a.get('customText') or '（空）'}")
            else:
                rec = " [推荐]" if a.get("recommended") else ""
                note = f"（适合：{a['note']}）" if a.get("note") and a.get("type") == "option" else ""
                print(f"    [{status}{rec}] {a.get('label', '')}{note}")
        print()


if __name__ == "__main__":
    main()
