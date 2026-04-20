from config import Config
class ProxyManager:
    def get_chrome_args(self): return []
    def should_rotate(self): return False
    def rotate(self): pass
    def get_current(self): return None
    def _mask(self, p): return "DIRECT"