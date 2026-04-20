"""
Proxy-Rotation und -Management
Rotiert automatisch zwischen Proxies um IP-basiertes Tracking zu vermeiden.
"""
import random
import time
import json
from pathlib import Path
from config import Config


class ProxyManager:
    STATE_FILE = Path("data/proxy_state.json")
    
    def __init__(self):
        self.proxies = list(Config.PROXY_LIST)
        self.current_index = 0
        self.request_count = 0
        self.failed_proxies = set()
        self._load_state()
    
    def _load_state(self):
        if self.STATE_FILE.exists():
            with open(self.STATE_FILE) as f:
                state = json.load(f)
                self.current_index = state.get("current_index", 0)
                self.request_count = state.get("request_count", 0)
                self.failed_proxies = set(state.get("failed_proxies", []))
    
    def _save_state(self):
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.STATE_FILE, "w") as f:
            json.dump({
                "current_index": self.current_index,
                "request_count": self.request_count,
                "failed_proxies": list(self.failed_proxies),
                "last_updated": time.time(),
            }, f, indent=2)
    
    def get_current(self) -> str | None:
        """Gibt den aktuellen Proxy zurück"""
        if not Config.USE_PROXY or not self.proxies:
            return None
        
        available = [p for p in self.proxies if p not in self.failed_proxies]
        if not available:
            print("⚠️  Alle Proxies fehlgeschlagen, Reset...")
            self.failed_proxies.clear()
            available = self.proxies
        
        idx = self.current_index % len(available)
        return available[idx]
    
    def rotate(self):
        """Wechsle zum nächsten Proxy"""
        self.current_index += 1
        self.request_count = 0
        self._save_state()
        proxy = self.get_current()
        print(f"🔄 Proxy rotiert → {self._mask(proxy)}")
        return proxy
    
    def mark_failed(self, proxy: str):
        """Markiere einen Proxy als fehlgeschlagen"""
        self.failed_proxies.add(proxy)
        self._save_state()
        print(f"❌ Proxy fehlgeschlagen: {self._mask(proxy)}")
    
    def should_rotate(self) -> bool:
        """Prüfe ob rotiert werden sollte"""
        self.request_count += 1
        self._save_state()
        return self.request_count >= Config.PROXY_ROTATE_AFTER
    
    def get_chrome_args(self) -> list:
        """Gibt Chrome-Argumente für den aktuellen Proxy zurück"""
        proxy = self.get_current()
        if proxy:
            return [f'--proxy-server={proxy}']
        return []
    
    @staticmethod
    def _mask(proxy: str | None) -> str:
        """Proxy-Adresse für Logs maskieren"""
        if not proxy:
            return "DIRECT"
        parts = proxy.split("@")
        if len(parts) > 1:
            return f"***@{parts[-1]}"
        return proxy[:20] + "..."
