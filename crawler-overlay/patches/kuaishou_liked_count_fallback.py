#!/usr/bin/env python3
"""Patch MediaCrawler store/kuaishou: liked_count falls back to likeCount.

Search GraphQL often returns likeCount but not realLikeCount, which previously
became liked_count="None"/0 and showed ❤ 0 on the hub page.
"""
from pathlib import Path
import os, re

root = Path(os.environ.get("MEDIACRAWLER_ROOT", "."))
p = root / "store" / "kuaishou" / "__init__.py"
text = p.read_text(encoding="utf-8")
if "likeCount" in text and "realLikeCount" in text and "not in (None" in text:
    print("kuaishou liked_count fallback already present")
else:
    old = '"liked_count": str(photo_info.get("realLikeCount")),'
    new = '''"liked_count": str(
            photo_info.get("realLikeCount")
            if photo_info.get("realLikeCount") not in (None, "", 0, "0")
            else photo_info.get("likeCount") or 0
        ),'''
    if old not in text:
        raise SystemExit("liked_count line not found")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("patched kuaishou liked_count fallback")
