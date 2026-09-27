#!/usr/bin/env python3
"""Inject cookies before first Douyin navigation (needed for CI cookie login)."""
from pathlib import Path
import os
root = Path(os.environ["MEDIACRAWLER_ROOT"])
core = root / "media_platform/douyin/core.py"
text = core.read_text(encoding="utf-8")
if "peiwan: inject cookies before goto" in text:
    print("core already patched")
    raise SystemExit(0)
needle = """            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)

            self.dy_client = await self.create_douyin_client(httpx_proxy_format)
"""
repl = """            self.context_page = await self.browser_context.new_page()
            # peiwan: inject cookies before goto
            if config.LOGIN_TYPE == \"cookie\" and config.COOKIES:
                for key, value in utils.convert_str_cookie_to_dict(config.COOKIES).items():
                    await self.browser_context.add_cookies([{
                        \"name\": key,
                        \"value\": value,
                        \"domain\": \".douyin.com\",
                        \"path\": \"/\",
                    }])
            await self.context_page.goto(self.index_url, wait_until=\"domcontentloaded\")
            await asyncio.sleep(2)
            try:
                self.dy_client = await self.create_douyin_client(httpx_proxy_format)
            except Exception:
                # navigation race: reload once
                await self.context_page.goto(self.index_url, wait_until=\"domcontentloaded\")
                await asyncio.sleep(2)
                self.dy_client = await self.create_douyin_client(httpx_proxy_format)
"""
if needle not in text:
    raise SystemExit("core needle not found")
# ensure asyncio imported in core
if "import asyncio" not in text:
    text = text.replace("import sys\n", "import sys\nimport asyncio\n", 1)
core.write_text(text.replace(needle, repl, 1), encoding="utf-8")
print("patched core.py")
