# 抖音陪玩 · 一周热度 Top

在线页（带话题筛选）：https://daibiao9333.github.io/peiwan-dy-week-top/

## 自动更新

- **GitHub Actions**（半自动）：每天 21:32（上海时间）用 Secrets 里的抖音 Cookie 爬取并发布本页。
- 也可在 Actions 页点 **Run workflow** 手动跑。
- Cookie 过期后，在 Mac 上执行：
  ```bash
  cd ~/Projects/MediaCrawler
  uv run python scripts/export-dy-cookies.py
  gh secret set DY_COOKIES --repo daibiao9333/peiwan-dy-week-top < data/douyin/dy_cookies.txt
  ```
- 本地 Mac LaunchAgent 仍可作为备份；两条线可并存。

## 注意

抖音可能对云端无头浏览器风控；失败时看 Actions 日志，通常需要重新扫码导出 Cookie。
