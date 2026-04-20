import nodriver as uc, asyncio, random; from config import Config; from profile_manager import ProfileManager; from session_manager import SessionManager; from proxy_manager import ProxyManager
class StealthBrowser:
    def __init__(self): self.profile_mgr = ProfileManager(); self.proxy_mgr = ProxyManager()
    async def start(self, name=None):
        self.profile = self.profile_mgr.select_profile(name); self.session_mgr = SessionManager(self.profile["name"])
        args = ["--no-first-run", "--disable-blink-features=AutomationControlled"] + self.proxy_mgr.get_chrome_args()
        self.browser = await uc.start(headless=False, user_data_dir=Config.CHROME_PATH, browser_args=args)
        self.page = await self.browser.get("about:blank"); await self.page.evaluate(self.profile["stealth_js"]); return self
    async def goto(self, url): self.page = await self.browser.get(url); await asyncio.sleep(2); return self.page
    async def click(self, text): from vision_click import vision_find_and_click; return await vision_find_and_click(self.page, text)
    async def type(self, text, selector=None):
        if selector: el = await self.page.select(selector); await el.click()
        for c in text: await self.page.send_keys(c); await asyncio.sleep(random.uniform(0.05, 0.15))
    async def close(self): self.browser.stop()