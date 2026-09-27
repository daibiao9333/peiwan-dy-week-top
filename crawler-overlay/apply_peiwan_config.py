#!/usr/bin/env python3
"""Patch MediaCrawler configs for peiwan week-top CI run."""
from pathlib import Path
import re
import os
import runpy

root = Path(os.environ.get("MEDIACRAWLER_ROOT", "."))
base = root / "config" / "base_config.py"
text = base.read_text(encoding="utf-8")
replacements = {
    r"^PLATFORM = .*": 'PLATFORM = "dy"',
    r"^KEYWORDS = .*": 'KEYWORDS = "陪玩,陪玩店,打手,趣味单,猛攻,陪玩售后,陪玩开庭"',
    r"^LOGIN_TYPE = .*": 'LOGIN_TYPE = "cookie"',
    r"^HEADLESS = .*": "HEADLESS = True",
    r"^ENABLE_CDP_MODE = .*": "ENABLE_CDP_MODE = False",
    r"^ENABLE_GET_COMMENTS = .*": "ENABLE_GET_COMMENTS = False",
    r"^SAVE_DATA_OPTION = .*": 'SAVE_DATA_OPTION = "jsonl"',
    r"^CRAWLER_MAX_NOTES_COUNT = .*": "CRAWLER_MAX_NOTES_COUNT = 40",
    r"^MAX_CONCURRENCY_NUM = .*": "MAX_CONCURRENCY_NUM = 1",
}
for pat, rep in replacements.items():
    text, n = re.subn(pat, rep, text, count=1, flags=re.M)
    print(pat, "->", n)
cookie = os.environ.get("DY_COOKIES", "").strip()
if not cookie:
    raise SystemExit("DY_COOKIES env empty")
cookie_lit = cookie.replace("\\", "\\\\").replace('"', '\\"')
text, n = re.subn(r"^COOKIES = .*", f'COOKIES = "{cookie_lit}"', text, count=1, flags=re.M)
print("COOKIES ->", n)
base.write_text(text, encoding="utf-8")

dy = root / "config" / "dy_config.py"
if dy.exists():
    d = dy.read_text(encoding="utf-8")
    d, n = re.subn(r"^PUBLISH_TIME_TYPE = .*", "PUBLISH_TIME_TYPE = 7", d, count=1, flags=re.M)
    print("PUBLISH_TIME_TYPE ->", n)
    dy.write_text(d, encoding="utf-8")

core = root / "media_platform" / "douyin" / "core.py"
c = core.read_text(encoding="utf-8")

m = re.search(r"from \.field import ([^\n]+)", c)
if not m:
    raise SystemExit("cannot find field import in core.py")
names = [x.strip() for x in m.group(1).split(",") if x.strip()]
if "SearchSortType" not in names:
    names.append("SearchSortType")
    c = c[: m.start(1)] + ", ".join(names) + c[m.end(1) :]
    print("added SearchSortType import")
else:
    print("SearchSortType import ok")

if "sort_type=SearchSortType.MOST_LIKE" not in c:
    c2, n = re.subn(r"sort_type\s*=\s*SearchSortType\.GENERAL", "sort_type=SearchSortType.MOST_LIKE", c)
    if n:
        c = c2
        print("patched MOST_LIKE", n)
    else:
        c2, n = re.subn(
            r"(publish_time=PublishTimeType\(config\.PUBLISH_TIME_TYPE\),)",
            r"\1\n                        sort_type=SearchSortType.MOST_LIKE,",
            c,
        )
        c = c2
        print("injected MOST_LIKE", n)
else:
    print("MOST_LIKE already present")
core.write_text(c, encoding="utf-8")
print("ok")

runpy.run_path(str(Path(__file__).resolve().parent / "patches" / "skip_cookie_login_dialog.py"))
runpy.run_path(str(Path(__file__).resolve().parent / "patches" / "cookie_before_goto.py"))
