#!/usr/bin/env python3
from pathlib import Path
import os
root = Path(os.environ["MEDIACRAWLER_ROOT"])
login = root / "media_platform/douyin/login.py"
text = login.read_text(encoding="utf-8")
if "CI/headless: skip login dialog" in text:
    print("already patched")
    raise SystemExit(0)
needle = """        # popup login dialog
        await self.popup_login_dialog()

        # select login type
        if config.LOGIN_TYPE == \"qrcode\":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == \"phone\":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == \"cookie\":
            await self.login_by_cookies()
        else:
            raise ValueError(\"[DouYinLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...\")
"""
repl = """        # select login type
        if config.LOGIN_TYPE == \"cookie\":
            # CI/headless: skip login dialog; inject cookies directly
            await self.login_by_cookies()
            try:
                await self.context_page.goto(\"https://www.douyin.com/\", wait_until=\"domcontentloaded\")
            except Exception:
                pass
            await asyncio.sleep(2)
        else:
            await self.popup_login_dialog()
            if config.LOGIN_TYPE == \"qrcode\":
                await self.login_by_qrcode()
            elif config.LOGIN_TYPE == \"phone\":
                await self.login_by_mobile()
            else:
                raise ValueError(\"[DouYinLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...\")
"""
if needle not in text:
    raise SystemExit("needle not found in login.py")
login.write_text(text.replace(needle, repl, 1), encoding="utf-8")
print("patched login.py")
