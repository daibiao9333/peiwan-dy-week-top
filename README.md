# 抖音陪玩 · 一周热度 Top

在线页（带话题筛选）：https://daibiao9333.github.io/peiwan-dy-week-top/

## 怎么更新

### 推荐（稳定）：Mac 本地爬 → 推 Pages

Mac LaunchAgent 每晚约 21:32 跑 MediaCrawler，再执行 `scripts/publish-week-top-pages.sh` 更新本站。飞书约 21:50 推链接。

### 半自动：GitHub Actions（已接好）

仓库已配置 `.github/workflows/daily-douyin.yml`，Secrets 名：`DY_COOKIES`。

实测：在 **GitHub 托管的 ubuntu runner** 上，Cookie 能注入，但搜索接口经常返回空列表（抖音对云端机房 IP 的风控）。空结果时工作流不会覆盖现有网页。

若要坚持「用 Actions 调度」，更靠谱的是把 Mac 注册成 **self-hosted runner**，让同样的 workflow 在你电脑上跑（用本机网络/登录态）。需要的话让 AI资讯帮你装。

刷新 Cookie（云端方案用）：

```bash
cd ~/Projects/MediaCrawler
uv run python scripts/export-dy-cookies.py
gh secret set DY_COOKIES --repo daibiao9333/peiwan-dy-week-top < data/douyin/dy_cookies.txt
```

手动触发：Actions → Douyin week-top crawl → Run workflow
