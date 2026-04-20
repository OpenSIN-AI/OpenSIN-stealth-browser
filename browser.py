"""
Hauptklasse: Stealth Browser
Kombiniert alle Module zu einem einzigen Interface.
"""
import nodriver as uc
import asyncio
import random
import time

from config import Config
from fingerprint import FingerprintGenerator
from human_mouse import human_click, move_mouse_human, human_scroll
from vision_click import vision_find_and_click, vision_find_and_click_with_retry
from profile_manager import ProfileManager
from session_manager import SessionManager
from proxy_manager import ProxyManager


class StealthBrowser:
    def __init__(self):
        self.browser = None
        self.page = None
        self.profile_mgr = ProfileManager()
        self.proxy_mgr = ProxyManager()
        self.session_mgr = None
        self.profile = None
        self._pages_visited = 0
    
    async def start(self, profile_name: str = None):
        """
        Startet den Browser mit vollem Stealth.
        """
        # 1. Profil wählen
        self.profile = self.profile_mgr.select_profile(profile_name)
        
        # 2. Session Manager initialisieren
        self.session_mgr = SessionManager(self.profile["name"])
        
        # 3. Chrome Args zusammenbauen
        chrome_args = [
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process',
            '--disable-site-isolation-trials',
            f'--profile-directory={self.profile["chrome_profile"]}',
        ]
        
        # Proxy hinzufügen falls aktiv
        chrome_args.extend(self.proxy_mgr.get_chrome_args())
        
        # 4. Browser starten
        self.browser = await uc.start(
            headless=False,
            user_data_dir=Config.CHROME_PATH,
            browser_args=chrome_args,
        )
        
        # 5. Erste Seite öffnen
        self.page = await self.browser.get('about:blank')
        
        # 6. Stealth-JS injizieren
        await self._inject_stealth()
        
        # 7. Session wiederherstellen
        await self.session_mgr.restore(self.page)
        
        print(f"\n🚀 STEALTH BROWSER GESTARTET")
        print(f"   Profil: {self.profile[\'name\']}")
        print(f"   Chrome: {self.profile[\'chrome_profile\']}")
        print(f"   GPU: {self.profile[\'fingerprint\'][\'gpu_renderer\']}")
        print(f"   Proxy: {self.proxy_mgr._mask(self.proxy_mgr.get_current())}")
        print(f"   Vision: {'AN' if Config.USE_VISION_CLICKS else 'AUS'}")
        print()
        
        return self
    
    async def _inject_stealth(self):
        """Injiziert Stealth-JavaScript"""
        try:
            await self.page.evaluate(self.profile["stealth_js"])
            print("🛡️  Stealth-JS injiziert")
        except Exception as e:
            print(f"⚠️  Stealth-Injection Warnung: {e}")
    
    async def _on_navigation(self):
        """Nach jeder Navigation: Re-Inject + Proxy-Check"""
        await self._inject_stealth()
        self._pages_visited += 1
        
        # Proxy-Rotation prüfen
        if self.proxy_mgr.should_rotate():
            self.proxy_mgr.rotate()
    
    # ============================================================
    # NAVIGATION
    # ============================================================
    
    async def goto(self, url: str, wait=True):
        """Navigiert zu einer URL"""
        print(f"🌐 → {url}")
        self.page = await self.browser.get(url)
        
        if wait:
            await self.think(2.0, 4.0)
        
        await self._on_navigation()
        return self.page
    
    # ============================================================
    # KLICKEN
    # ============================================================
    
    async def click(self, text: str, use_vision=None):
        """
        Klickt auf ein Element.
        use_vision=True:  OS-Level Mausklick (unsichtbar für Browser)
        use_vision=False: DOM-Level Klick (schneller, aber detectable)
        use_vision=None:  Nutzt Config.USE_VISION_CLICKS
        """
        vision = use_vision if use_vision is not None else Config.USE_VISION_CLICKS
        
        if vision:
            return await vision_find_and_click_with_retry(self.page, text)
        else:
            return await self._dom_click(text)
    
    async def _dom_click(self, text: str) -> bool:
        """Fallback: DOM-basierter Klick"""
        await self.think(0.3, 0.8)
        try:
            element = await self.page.find(text, best_match=True)
            if element:
                await element.scroll_into_view()
                await self.think(0.2, 0.5)
                await element.click()
                print(f"🖱️  DOM-Klick auf: '{text}'")
                return True
        except Exception as e:
            print(f"❌ DOM-Klick fehlgeschlagen: {text} ({e})")
        return False
    
    async def click_selector(self, css: str, use_vision=False):
        """Klickt per CSS-Selector"""
        await self.think(0.3, 0.8)
        try:
            element = await self.page.select(css)
            if element:
                if use_vision:
                    box = await element.get_position()
                    if box:
                        await human_click(
                            box[0] + random.randint(5, 20),
                            box[1] + random.randint(5, 10)
                        )
                        return True
                else:
                    await element.click()
                    return True
        except Exception as e:
            print(f"❌ Selector-Klick fehlgeschlagen: {css} ({e})")
        return False
    
    # ============================================================
    # TIPPEN
    # ============================================================
    
    async def type(self, text: str, selector: str = None):
        """
        Tippt Text menschlich.
        Mit Tippfehlern + Korrekturen für maximalen Realismus.
        """
        # Feld anklicken falls Selector gegeben
        if selector:
            try:
                element = await self.page.select(selector)
                if element:
                    await element.click()
                    await self.think(0.3, 0.6)
            except:
                pass
        
        for i, char in enumerate(text):
            # Tippfehler-Simulation
            if random.random() < Config.TYPE_TYPO_CHANCE and len(text) > 5:
                # Falschen Buchstaben tippen
                wrong_char = chr(ord(char) + random.choice([-1, 1]))
                await self.page.send_keys(wrong_char)
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # Backspace + richtigen Buchstaben
                await self.page.send_keys('\b')
                await asyncio.sleep(random.uniform(0.05, 0.15))
            
            await self.page.send_keys(char)
            
            # Timing
            delay = random.uniform(Config.TYPE_SPEED_MIN, Config.TYPE_SPEED_MAX)
            
            # Denkpause
            if random.random() < Config.TYPE_PAUSE_CHANCE:
                delay = random.uniform(Config.TYPE_PAUSE_MIN, Config.TYPE_PAUSE_MAX)
            
            await asyncio.sleep(delay)
    
    # ============================================================
    # WARTEN
    # ============================================================
    
    async def think(self, min_sec=None, max_sec=None):
        """Menschliche Denkpause"""
        mn = min_sec or Config.THINK_TIME_MIN
        mx = max_sec or Config.THINK_TIME_MAX
        await asyncio.sleep(random.uniform(mn, mx))
    
    async def wait_for(self, text_or_selector: str, timeout=30):
        """Wartet bis Element erscheint"""
        start = time.time()
        while time.time() - start < timeout:
            try:
                if text_or_selector.startswith(('.', '#', '[', 'input', 'button', 'div', 'a')):
                    el = await self.page.select(text_or_selector)
                else:
                    el = await self.page.find(text_or_selector, best_match=True)
                if el:
                    return el
            except:
                pass
            await asyncio.sleep(0.5)
        print(f"⏰ Timeout beim Warten auf: {text_or_selector}")
        return None
    
    # ============================================================
    # SCROLLEN
    # ============================================================
    
    async def scroll_down(self, amount=None):
        """Menschliches Scrollen nach unten"""
        await human_scroll("down", amount)
    
    async def scroll_up(self, amount=None):
        """Menschliches Scrollen nach oben"""
        await human_scroll("up", amount)
    
    async def scroll_to_element(self, text: str):
        """Scrollt zu einem Element"""
        try:
            el = await self.page.find(text, best_match=True)
            if el:
                await el.scroll_into_view()
                await self.think(0.3, 0.8)
                return True
        except:
            pass
        return False
    
    # ============================================================
    # SESSION
    # ============================================================
    
    async def save_session(self):
        """Aktuelle Session speichern"""
        await self.session_mgr.save_current(self.page)
    
    async def screenshot(self, name=None):
        """Screenshot machen"""
        fname = name or f"manual_{int(time.time())}"
        path = Config.SCREENSHOT_DIR / f"{fname}.png"
        await self.page.save_screenshot(str(path))
        print(f"📸 Screenshot: {path}")
        return str(path)
    
    # ============================================================
    # INFORMATIONEN
    # ============================================================
    
    async def get_url(self) -> str:
        """Aktuelle URL"""
        try:
            return await self.page.evaluate("window.location.href")
        except:
            return "unknown"
    
    async def get_text(self, selector: str = None) -> str:
        """Text auslesen"""
        try:
            if selector:
                el = await self.page.select(selector)
                if el:
                    return el.text
            return await self.page.evaluate("document.body.innerText")
        except:
            return ""
    
    async def get_html(self, selector: str = None) -> str:
        """HTML auslesen"""
        try:
            if selector:
                return await self.page.evaluate(
                    f"document.querySelector('{selector}').innerHTML"
                )
            return await self.page.evaluate("document.documentElement.outerHTML")
        except:
            return ""
    
    # ============================================================
    # STEALTH CHECKS
    # ============================================================
    
    async def check_stealth(self):
        """Prüft ob der Browser als Bot erkannt wird"""
        print("\n🔍 STEALTH CHECK:")
        
        checks = {
            "navigator.webdriver": await self.page.evaluate("navigator.webdriver"),
            "chrome.runtime": await self.page.evaluate("!!window.chrome && !!window.chrome.runtime"),
            "plugins.length": await self.page.evaluate("navigator.plugins.length"),
            "languages": await self.page.evaluate("navigator.languages"),
            "platform": await self.page.evaluate("navigator.platform"),
            "hardwareConcurrency": await self.page.evaluate("navigator.hardwareConcurrency"),
            "deviceMemory": await self.page.evaluate("navigator.deviceMemory"),
            "webgl_vendor": await self.page.evaluate("""
                (function() {{
                    var c = document.createElement('canvas');
                    var gl = c.getContext('webgl');
                    if (!gl) return 'no webgl';
                    var ext = gl.getExtension('WEBGL_debug_renderer_info');
                    return ext ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) : 'no ext';
                }})()
            """),
            "webgl_renderer": await self.page.evaluate("""
                (function() {{
                    var c = document.createElement('canvas');
                    var gl = c.getContext('webgl');
                    if (!gl) return 'no webgl';
                    var ext = gl.getExtension('WEBGL_debug_renderer_info');
                    return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'no ext';
                }})()
            """),
        }
        
        for key, value in checks.items():
            status = "✅" if key != "navigator.webdriver" or not value else "❌"
            if key == "navigator.webdriver" and value:
                status = "❌ DETECTED!"
            print(f"  {status} {key}: {value}")
        
        print()
        return checks
    
    # ============================================================
    # CLEANUP
    # ============================================================
    
    async def close(self, save=True):
        """Browser schließen"""
        if save and self.session_mgr:
            await self.save_session()
        
        if self.browser:
            self.browser.stop()
            print("👋 Browser geschlossen")