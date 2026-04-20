import nodriver as uc; import asyncio, random; from config import Config; from fingerprint import FingerprintGenerator
class StealthBrowser:
    def __init__(self): self.browser = None; self.page = None
    async def start(self, profile_name="default"):
        fg = FingerprintGenerator(profile_name); js = fg.get_stealth_js(); args = ["--no-first-run", "--disable-blink-features=AutomationControlled"]
        self.browser = await uc.start(headless=False, user_data_dir=Config.CHROME_PATH, browser_args=args); self.page = await self.browser.get("about:blank"); await self.page.evaluate(js); return self
    async def goto(self, url): self.page = await self.browser.get(url); await asyncio.sleep(random.uniform(2, 4)); return self.page
    async def click(self, text): from vision_click import vision_find_and_click; return await vision_find_and_click(self.page, text)
    async def close(self): self.browser.stop()
