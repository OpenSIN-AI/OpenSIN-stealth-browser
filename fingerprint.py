"""
Fingerprint Consistency Layer
"""
import hashlib
import json
from pathlib import Path
GPU_PROFILES = [{"vendor": "Intel Inc.", "renderer": "Intel(R) UHD Graphics 630"}, {"vendor": "Apple", "renderer": "Apple M1"}]
SCREEN_PROFILES = [{"width": 1920, "height": 1080, "depth": 24, "dpr": 1}]
TIMEZONE_PROFILES = [{"tz": "Europe/Berlin", "offset": -60}]
FONT_SETS = [["Arial", "Helvetica", "SF Pro Text"]]
class FingerprintGenerator:
    CACHE_FILE = Path("data/fingerprints.json")
    def __init__(self, profile_name):
        self.profile_name = profile_name; self.seed = int(hashlib.sha256(profile_name.encode()).hexdigest(), 16)
        self.fingerprint = self._load_or_generate()
    def _deterministic_choice(self, lst, extra_seed=0): return lst[(self.seed + extra_seed) % len(lst)]
    def _load_or_generate(self):
        if self.CACHE_FILE.exists():
            with open(self.CACHE_FILE) as f: all_fps = json.load(f); return all_fps.get(self.profile_name, self._generate())
        fp = self._generate(); self._save(fp); return fp
    def _generate(self):
        return {"gpu_vendor": self._deterministic_choice(GPU_PROFILES, 1)["vendor"], "gpu_renderer": self._deterministic_choice(GPU_PROFILES, 1)["renderer"], "screen_width": 1920, "screen_height": 1080, "color_depth": 24, "device_pixel_ratio": 1, "timezone": "Europe/Berlin", "timezone_offset": -60, "fonts": FONT_SETS[0], "canvas_noise": 0.001, "audio_sample_rate": 48000, "hardware_concurrency": 8, "device_memory": 16, "max_touch_points": 0, "languages": ["de-DE", "de"], "platform": "MacIntel"}
    def _save(self, fp):
        all_fps = {}; 
        if self.CACHE_FILE.exists():
            with open(self.CACHE_FILE) as f: all_fps = json.load(f)
        all_fps[self.profile_name] = fp
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CACHE_FILE, "w") as f: json.dump(all_fps, f)
    def get_stealth_js(self):
        fp = self.fingerprint; langs = json.dumps(fp["languages"])
        return f"Object.defineProperty(navigator, \'webdriver\', {{get: () => false}}); Object.defineProperty(navigator, \'languages\', {{get: () => {langs}}}); console.log(\'[STEALTH] Loaded\');"