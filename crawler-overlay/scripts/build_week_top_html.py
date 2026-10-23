#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from html import escape
from collections import OrderedDict, Counter

ROOT = Path(__file__).resolve().parents[1]
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
day = now.strftime("%Y-%m-%d")
parser = argparse.ArgumentParser(description='Build peiwan heat HTML')
parser.add_argument('--days', type=int, default=3, help='heat window days (3=default Mon/Thu, 7=Sunday week)')
parser.add_argument('--platform', default='dy', help='legacy single-platform builder; hub page built elsewhere')
args = parser.parse_args()
DAYS = max(1, int(args.days))
cutoff = now - timedelta(days=DAYS)
src = ROOT / "data" / "douyin" / "jsonl" / f"search_contents_{day}.jsonl"
if not src.exists():
    files = sorted((ROOT / "data" / "douyin" / "jsonl").glob("search_contents_*.jsonl"))
    files = [f for f in files if "week_top" not in f.name and "today_top" not in f.name]
    if not files:
        raise SystemExit("no jsonl")
    src = files[-1]

by_id = OrderedDict()
kwc = Counter()
for line in src.read_text(encoding="utf-8", errors="ignore").splitlines():
    if not line.strip():
        continue
    o = json.loads(line)
    aid = str(o.get("aweme_id") or "")
    ts = int(o.get("create_time") or 0)
    if ts > 10_000_000_000:
        ts //= 1000
    dt = datetime.fromtimestamp(ts, TZ) if ts else None
    try:
        like = int(o.get("liked_count") or 0)
    except Exception:
        like = 0
    if not dt or dt < cutoff:
        continue
    sk = o.get("source_keyword") or ""
    if sk:
        kwc[sk] += 1
    if aid in by_id and by_id[aid]["like"] >= like:
        continue
    cover = o.get("cover_url") or ""
    by_id[aid] = {
        "o": o,
        "dt": dt,
        "like": like,
        "cover": cover,
        "title": (o.get("title") or o.get("desc") or "").replace("\n", " "),
        "author": o.get("nickname") or "",
        "url": o.get("aweme_url") or "",
        "kw": sk,
    }
rows = sorted(by_id.values(), key=lambda r: r["like"], reverse=True)
out_dir = ROOT / "data" / "douyin"
(out_dir / "jsonl").mkdir(parents=True, exist_ok=True)
(out_dir / "jsonl" / f"search_contents_week_top_{day}.jsonl").write_text(
    "\n".join(json.dumps(r["o"], ensure_ascii=False) for r in rows) + ("\n" if rows else ""),
    encoding="utf-8",
)

def fmt_num(n):
    try:
        n = int(n)
    except Exception:
        return str(n)
    if n >= 10000:
        s = f"{n/10000:.1f}万"
        return s.replace(".0万", "万")
    return f"{n:,}"

kws = ["陪玩", "陪玩店", "打手", "趣味单", "猛攻", "陪玩售后", "陪玩开庭", "陪玩系统", "订单系统", "俱乐部系统", "陪玩日常", "陪玩团", "护航", "护子"]
kw_chips = [
    f'<button type="button" class="chip active" data-filter="all">全部 <b>{len(rows)}</b></button>'
]
for k in kws:
    kw_chips.append(
        f'<button type="button" class="chip" data-filter="{escape(k)}">{escape(k)} <b>{kwc.get(k, 0)}</b></button>'
    )
kw_chips_html = "".join(kw_chips)

cards = []
for i, r in enumerate(rows, 1):
    title = escape(str(r["title"])[:160])
    author = escape(str(r["author"]))
    kw = escape(str(r["kw"] or "—"))
    tm = r["dt"].strftime("%m-%d %H:%M")
    like = fmt_num(r["like"])
    href = escape(str(r["url"])) if r["url"] else "#"
    cover = escape(str(r["cover"])) if r["cover"] else ""
    if cover:
        media = f'<img class="cover" src="{cover}" alt="" loading="lazy" referrerpolicy="no-referrer">'
    else:
        media = '<div class="cover placeholder">无封面</div>'
    cards.append(
        f'<a class="card" href="{href}" target="_blank" rel="noopener" data-kw="{kw}">'
        f'<div class="rank">{i}</div><div class="media">{media}</div><div class="body">'
        f'<div class="kw">{kw}</div><h2 class="title">{title}</h2>'
        f'<div class="meta-row"><span class="author">{author}</span><span class="time">{tm}</span></div>'
        f'<div class="stats"><span class="like">❤ {like}</span></div></div></a>'
    )

top_like = fmt_num(rows[0]["like"]) if rows else "0"
cards_html = "".join(cards)
html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>抖音 · {"三天" if DAYS == 3 else "一周"}热度 Top</title>
<style>
:root {{
  --bg: #070B14; --panel: #0A1020; --panel2: #10182A; --preview: #10182A;
  --text: #E8ECF2; --muted: #8B96A8; --soft: #C8D0DC;
  --primary: #5B8DEF; --primary-fg: #E8ECF2; --ice: #A8C4F0;
  --accent: #5B8DEF; --accent2: #A8C4F0;
  --line: rgba(148, 163, 184, 0.18); --dim: rgba(91, 141, 239, 0.35);
  --shadow: 0 12px 40px rgba(0,0,0,.45);
  --radius: .625rem; --radius-lg: calc(var(--radius) + 4px);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", system-ui, sans-serif;
  background:
    radial-gradient(1000px 520px at 8% -12%, rgba(91,141,239,.18) 0%, transparent 55%),
    radial-gradient(800px 480px at 100% 0%, rgba(168,196,240,.08) 0%, transparent 50%),
    var(--bg);
  color: var(--text); min-height: 100vh; -webkit-font-smoothing: antialiased;
}}
.wrap {{ max-width: 1180px; margin: 0 auto; padding: 28px 20px 60px; }}
.brand-line {{
  margin: 0 0 14px; font-size: 12px; color: var(--muted); letter-spacing: .02em;
}}
.brand-line a {{ color: var(--ice); text-decoration: none; border-bottom: 1px solid var(--dim); }}
.brand-line a:hover {{ color: var(--primary); }}
.hero {{
  background: linear-gradient(135deg, rgba(91,141,239,.14), rgba(16,24,42,.9));
  border: 1px solid var(--line); border-radius: 20px; padding: 24px 26px; box-shadow: var(--shadow);
  margin-bottom: 22px;
}}
.hero h1 {{ margin: 0 0 10px; font-size: 28px; font-weight: 700; letter-spacing: -0.02em; color: var(--text); }}
.hero .sub {{ color: var(--muted); font-size: 14px; line-height: 1.6; margin-bottom: 14px; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.chip {{
  background: rgba(255,255,255,.04); border: 1px solid var(--line); border-radius: 999px;
  padding: 7px 14px; font-size: 13px; color: var(--muted); cursor: pointer;
  font-family: inherit; transition: .15s ease;
}}
.chip:hover {{ border-color: var(--dim); color: var(--text); }}
.chip.active {{
  background: linear-gradient(135deg, #5B8DEF, #3d6fd4);
  border-color: transparent; color: #fff;
}}
.chip.active b {{ color: #fff; }}
.chip b {{ color: var(--ice); font-weight: 600; margin-left: 4px; }}
.summary {{ display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px; }}
.stat {{
  background: var(--panel); border: 1px solid var(--line); border-radius: 14px;
  padding: 12px 16px; min-width: 120px;
}}
.stat .v {{ font-size: 22px; font-weight: 700; letter-spacing: -0.02em; }}
.stat .l {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
#visibleCount {{ color: var(--ice); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
.card {{
  display: flex; flex-direction: column; text-decoration: none; color: inherit;
  background: var(--panel); border: 1px solid var(--line); border-radius: 18px;
  overflow: hidden; position: relative; transition: transform .18s ease, border-color .18s;
  box-shadow: 0 8px 24px rgba(0,0,0,.28);
}}
.card.hidden {{ display: none; }}
.card:hover {{ transform: translateY(-3px); border-color: var(--dim); box-shadow: var(--shadow); }}
.rank {{
  position: absolute; z-index: 2; top: 10px; left: 10px;
  background: rgba(7,11,20,.78); color: #fff; font-weight: 700; font-size: 12px;
  width: 28px; height: 28px; border-radius: 9px; display: grid; place-items: center;
}}
.card:nth-child(-n+3) .rank {{ background: linear-gradient(135deg, #5B8DEF, #3d6fd4); }}
.media {{ aspect-ratio: 3/4; background: var(--panel2); overflow: hidden; }}
.cover {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.cover.placeholder {{ display: grid; place-items: center; width: 100%; height: 100%; color: var(--muted); font-size: 13px; }}
.body {{ padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 8px; flex: 1; }}
.kw {{
  align-self: flex-start; font-size: 11px; color: var(--ice);
  background: rgba(91,141,239,.16); border: 1px solid var(--dim);
  border-radius: 999px; padding: 2px 8px; font-weight: 600;
}}
.title {{
  margin: 0; font-size: 14px; line-height: 1.45; font-weight: 600;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}}
.meta-row {{ display: flex; justify-content: space-between; gap: 8px; font-size: 12px; color: var(--muted); }}
.author {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 55%; }}
.stats {{ margin-top: auto; }}
.like {{ color: var(--primary); font-weight: 700; font-variant-numeric: tabular-nums; font-size: 14px; }}
.foot {{ margin-top: 28px; text-align: center; color: var(--muted); font-size: 12px; line-height: 1.7; }}
.foot a {{ color: var(--ice); text-decoration: none; border-bottom: 1px solid var(--dim); }}
.foot a:hover {{ color: var(--primary); }}
.empty {{ display: none; text-align: center; color: var(--muted); padding: 40px; grid-column: 1 / -1; }}
.empty.show {{ display: block; }}
</style>
</head>
<body>
<div class="wrap">
  <p class="brand-line">信息来源于序核 OS 官方网站 <a href="https://www.xuheos.com" target="_blank" rel="noopener">www.xuheos.com</a></p>
  <header class="hero">
    <h1>抖音 · {"三天内" if DAYS == 3 else "一周内"} · 热度 Top</h1>
    <p class="sub">近 {DAYS} 天至 {now.strftime('%Y-%m-%d %H:%M')} · 按点赞降序 · 点击上方话题筛选</p>
    <div class="chips" id="filters">{kw_chips_html}</div>
    <div class="summary">
      <div class="stat"><div class="v"><span id="visibleCount">{len(rows)}</span><span style="font-size:14px;color:var(--muted)"> / {len(rows)}</span></div><div class="l">当前显示</div></div>
      <div class="stat"><div class="v">{top_like}</div><div class="l">最高点赞</div></div>
      <div class="stat"><div class="v">{DAYS}天</div><div class="l">发布窗口</div></div>
    </div>
  </header>
  <section class="grid" id="grid">
    {cards_html}
    <p class="empty" id="empty">这个话题下暂时没有内容</p>
  </section>
  <p class="foot">信息来源于序核 OS 官方网站 <a href="https://www.xuheos.com" target="_blank" rel="noopener">www.xuheos.com</a><br>MediaCrawler · 本地生成 · {escape(src.name)}</p>
</div>
<script>
(function() {{
  const chips = document.querySelectorAll('.chip');
  const cards = document.querySelectorAll('.card');
  const countEl = document.getElementById('visibleCount');
  const empty = document.getElementById('empty');
  chips.forEach(chip => {{
    chip.addEventListener('click', () => {{
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const f = chip.dataset.filter;
      let n = 0;
      cards.forEach(card => {{
        const show = f === 'all' || card.dataset.kw === f;
        card.classList.toggle('hidden', !show);
        if (show) n++;
      }});
      countEl.textContent = n;
      empty.classList.toggle('show', n === 0);
    }});
  }});
}})();
</script>
</body>
</html>
"""
label = "三天" if DAYS == 3 else "一周"
html_path = out_dir / f"陪玩抖音-{label}热度Top-{day}.html"
latest = out_dir / f"陪玩抖音-{label}热度Top-latest.html"
html_path.write_text(html, encoding="utf-8")
latest.write_text(html, encoding="utf-8")
if DAYS == 3:
    # compatibility alias used by older publish/workflow paths
    (out_dir / "陪玩抖音-一周热度Top-latest.html").write_text(html, encoding="utf-8")
print(html_path)
print("days", DAYS, "rows", len(rows))
