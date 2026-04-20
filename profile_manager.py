import json, time; from pathlib import Path; from fingerprint import FingerprintGenerator
class ProfileManager:
    PROFILES_FILE = Path("data/profiles.json")
    def __init__(self): self.profiles = self._load()
    def _load(self):
        if self.PROFILES_FILE.exists():
            with open(self.PROFILES_FILE) as f: return json.load(f)
        return {"default": {"chrome_profile": "Default", "last_used": 0}}
    def select_profile(self, name=None):
        name = name or "default"; p = self.profiles[name]; p["last_used"] = time.time(); fg = FingerprintGenerator(name)
        return {"name": name, "chrome_profile": p["chrome_profile"], "stealth_js": fg.get_stealth_js()}
    def add_profile(self, name, chrome): self.profiles[name] = {"chrome_profile": chrome, "last_used": 0}; self._save()
    def _save(self): self.PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True); with open(self.PROFILES_FILE, "w") as f: json.dump(self.profiles, f)