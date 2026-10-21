# 陪玩行业三天热度 · 抖音 / 快手 / B站

**统一总页（推荐）**：https://top.xuheos.com/

- 默认首页：近 **3 天**热度（周一 / 周四飞书推送）
- 一周页：https://top.xuheos.com/week.html（周日飞书推送，近 7 天）
- 备份：Cloudflare `https://peiwan-week-top.daibiao9333.workers.dev/`（国内部分网络不稳定，以 ECS 为准）

同一页用顶部 Tab 切换抖音 / 快手 / B站，支持话题筛选。Hash 直达：`#dy` `#ks` `#bili`。

旧跳转仍可用：

- https://top.xuheos.com/kuaishou.html → `#ks`
- https://top.xuheos.com/bilibili.html → `#bili`

## 怎么更新

### 推荐：Mac 本地爬 → 发布到 GitHub Pages 源 + ECS

Mac 上 MediaCrawler 每晚爬取后：

```bash
cd ~/Projects/MediaCrawler   # 若目录已迁走，改成实际路径
python3 scripts/build_week_top_html.py --platform all --days 3
# 周日另建一周页：
# python3 scripts/build_week_top_html.py --platform all --days 7
bash scripts/publish-week-top-pages.sh
```

`publish-week-top-pages.sh` 会 git push 本仓库，并用 `ssh xos-ecs` rsync HTML 到 `/var/www/top-peiwan-week/`。

### 半自动：GitHub Actions

见 `.github/workflows/daily-douyin.yml`。云端 IP 常被风控；更靠谱 self-hosted runner。

## 关键词

陪玩, 陪玩店, 打手, 趣味单, 猛攻, 陪玩售后, 陪玩开庭, 陪玩系统, 订单系统, 俱乐部系统, 陪玩日常, 陪玩团, 护航, 护子
