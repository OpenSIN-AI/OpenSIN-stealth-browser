import json, time; from pathlib import Path
class ProfileManager:
    def __init__(self): self.path = Path("data/profiles.json"); self.profiles = self._load()
    def _load(self): 
        if self.path.exists():
            with open(self.path) as f: return json.load(f)
        return {"default": {"last": 0}}
    def add_profile(self, name, chrome="Default"): self.profiles[name] = {"chrome": chrome, "last": 0}; self._save()
    def _save(self): self.path.parent.mkdir(parents=True, exist_ok=True); with open(self.path, "w") as f: json.dump(self.profiles, f)
