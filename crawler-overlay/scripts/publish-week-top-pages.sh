#!/usr/bin/env bash
# Publish peiwan heat pages to GitHub repo + ECS static root.
# Expects hub HTML already built into PEIWAN_PAGES_REPO (index.html / week.html / *.html).
set -euo pipefail

PRIMARY_URL="${PRIMARY_URL:-https://top.xuheos.com/}"
WEEK_URL="${WEEK_URL:-https://top.xuheos.com/week.html}"
CF_BACKUP_URL="${CF_BACKUP_URL:-https://peiwan-week-top.daibiao9333.workers.dev/}"
PAGES_REPO="${PEIWAN_PAGES_REPO:-$HOME/Projects/peiwan-dy-week-top}"
ECS_HOST="${ECS_HOST:-xos-ecs}"
ECS_DIR="${ECS_DIR:-/var/www/top-peiwan-week}"

if [[ ! -d "$PAGES_REPO/.git" ]]; then
  echo "PEIWAN_PAGES_REPO not a git repo: $PAGES_REPO" >&2
  exit 1
fi

cd "$PAGES_REPO"
# sync built files from MediaCrawler data hub if provided
if [[ -n "${HUB_HTML_DIR:-}" ]]; then
  cp -f "$HUB_HTML_DIR"/index.html "$HUB_HTML_DIR"/kuaishou.html "$HUB_HTML_DIR"/bilibili.html .
  [[ -f "$HUB_HTML_DIR/week.html" ]] && cp -f "$HUB_HTML_DIR/week.html" .
  mkdir -p docs
  cp -f index.html kuaishou.html bilibili.html docs/
  [[ -f week.html ]] && cp -f week.html docs/
fi

git add index.html week.html kuaishou.html bilibili.html docs 2>/dev/null || true
if ! git diff --cached --quiet; then
  git commit -m "publish peiwan heat $(date +%Y-%m-%d-%H%M)"
  git push origin HEAD
fi

echo "Primary: $PRIMARY_URL"
echo "Week:    $WEEK_URL"
echo "CF backup: $CF_BACKUP_URL"

if ssh -o ConnectTimeout=30 "$ECS_HOST" "test -d '$ECS_DIR'"; then
  rsync -avz index.html week.html kuaishou.html bilibili.html "$ECS_HOST:$ECS_DIR/"
  echo "Synced to $ECS_HOST:$ECS_DIR"
else
  echo "WARN: cannot reach $ECS_HOST:$ECS_DIR — skipped rsync" >&2
fi
