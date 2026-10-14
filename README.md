# 陪玩一周热度 Top · 抖音 / 快手 / B站

**统一总页（推荐）**：https://daibiao9333.github.io/peiwan-dy-week-top/

同一页用顶部 Tab 切换抖音 / 快手 / B站，支持话题筛选。Hash 直达：`#dy` `#ks` `#bili`。

旧链接仍可用（自动跳到对应 Tab）：

- https://daibiao9333.github.io/peiwan-dy-week-top/kuaishou.html → `#ks`
- https://daibiao9333.github.io/peiwan-dy-week-top/bilibili.html → `#bili`

## 怎么更新

### 推荐（稳定）：Mac 本地爬 → 推 Pages

Mac LaunchAgent 每晚约 21:32 跑 MediaCrawler，再执行 `scripts/publish-week-top-pages.sh` 更新本站。飞书约 21:50 推链接。

本地重建并发布：

```bash
cd ~/Projects/MediaCrawler
python3 scripts/build_week_top_html.py --platform all
bash scripts/publish-week-top-pages.sh
```

### 半自动：GitHub Actions

仓库已配置 `.github/workflows/daily-douyin.yml`。云端 IP 常被抖音风控；更靠谱的是 self-hosted runner。
