#!/usr/bin/env python3
"""Patch MediaCrawler configs for peiwan week-top CI run."""
from pathlib import Path
import re
import os

root = Path(os.environ.get("MEDIACRAWLER_ROOT", "."))
base = root / "config" / "base_config.py"
text = base.read_text(encoding="utf-8")
replacements = {
    r'^PLATFORM = .*': 'PLATFORM = "dy"',
    r'^KEYWORDS = .*': 'KEYWORDS = "陪玩,陪玩店,打手,趣味单,猛攻,陪玩售后,陪玩开庭"',
    r'^LOGIN_TYPE = .*': 'LOGIN_TYPE = "cookie"',
    r'^HEADLESS = .*': 'HEADLESS = True',
    r'^ENABLE_CDP_MODE = .*': 'ENABLE_CDP_MODE = False',
    r'^ENABLE_GET_COMMENTS = .*': 'ENABLE_GET_COMMENTS = False',
    r'^SAVE_DATA_OPTION = .*': 'SAVE_DATA_OPTION = "jsonl"',
    r'^CRAWLER_MAX_NOTES_COUNT = .*': 'CRAWLER_MAX_NOTES_COUNT = 40',
    r'^MAX_CONCURRENCY_NUM = .*': 'MAX_CONCURRENCY_NUM = 1',
}
for pat, rep in replacements.items():
    text, n = re.subn(pat, rep, text, count=1, flags=re.M)
    print(pat, "->", n)
# COOKIES from env
cookie = os.environ.get("DY_COOKIES", "").strip()
if not cookie:
    raise SystemExit("DY_COOKIES env empty")
# escape for python string
cookie_lit = cookie.replace("\\", "\\\\").replace('"', '\\"')
text, n = re.subn(r'^COOKIES = .*', f'COOKIES = "{cookie_lit}"', text, count=1, flags=re.M)
print("COOKIES ->", n)
base.write_text(text, encoding="utf-8")

dy = root / "config" / "dy_config.py"
if dy.exists():
    d = dy.read_text(encoding="utf-8")
    d, n = re.subn(r'^PUBLISH_TIME_TYPE = .*', 'PUBLISH_TIME_TYPE = 7', d, count=1, flags=re.M)
    print("PUBLISH_TIME_TYPE ->", n)
    dy.write_text(d, encoding="utf-8")

core = root / "media_platform" / "douyin" / "core.py"
c = core.read_text(encoding="utf-8")
# force MOST_LIKE if still GENERAL
if "SearchSortType.MOST_LIKE" not in c:
    c2, n = re.subn(
        r"sort_type\s*=\s*SearchSortType\.GENERAL",
        "sort_type=SearchSortType.MOST_LIKE",
        c,
    )
    if n:
        core.write_text(c2, encoding="utf-8")
        print("patched MOST_LIKE", n)
    else:
        # try inject near publish_time=
        c2, n = re.subn(
            r"(publish_time=PublishTimeType\(config\.PUBLISH_TIME_TYPE\),)",
            r"\1\n                        sort_type=SearchSortType.MOST_LIKE,",
            c,
        )
        core.write_text(c2, encoding="utf-8")
        print("injected MOST_LIKE", n)
else:
    print("MOST_LIKE already present")
print("ok")


# skip login dialog for cookie mode
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / "patches" / "skip_cookie_login_dialog.py"))
runpy.run_path(str(Path(__file__).resolve().parent / "patches" / "cookie_before_goto.py"))
