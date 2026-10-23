#!/usr/bin/env python3
"""写一份合成 fixture jsonl，供「云端没爬到数据」时做模板自检。

为什么需要：daily-douyin.yml 原来是「没有 jsonl ⇒ exit 0」，于是模板里任何运行期错误
（例如 2026-10-22 那次 f-string 内 CSS 花括号未转义 ⇒ NameError: name 'bg'）只有等云端
真的爬到数据那天才会暴露，中间几天每天都是假绿。改成无数据时用本 fixture 跑一遍
build_week_top_html.py，模板坏了当天就红；产物与 fixture 由 workflow 清理，不进 Pages。

用法：python3 make_selfcheck_fixture.py <输出 jsonl 路径>
"""
import json
import sys
import time
from pathlib import Path


def main(argv):
    if len(argv) != 2:
        raise SystemExit("usage: make_selfcheck_fixture.py <out.jsonl>")
    out = Path(argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    now = int(time.time())
    rows = [
        {
            "aweme_id": "9001",
            "create_time": now - 3600,
            "liked_count": 1234,
            "title": "自检样本A",
            "nickname": "样本甲",
            "aweme_url": "https://example.invalid/9001",
            "source_keyword": "陪玩",
            "cover_url": "",
        },
        {
            "aweme_id": "9002",
            "create_time": now - 7200,
            "liked_count": 88,
            "title": "自检样本B",
            "nickname": "样本乙",
            "aweme_url": "https://example.invalid/9002",
            "source_keyword": "开黑",
            "cover_url": "",
        },
    ]
    out.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    print(f"fixture: {out} rows={len(rows)}")


if __name__ == "__main__":
    main(sys.argv)
