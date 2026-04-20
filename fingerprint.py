import hashlib
import json
from pathlib import Path
GPU_PROFILES = [{"vendor": "Intel Inc.", "renderer": "Intel(R) UHD Graphics 630"}, {"vendor": "Apple", "renderer": "Apple M1"}, {"vendor": "Apple", "renderer": "Apple M2"}, {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA GeForce RTX 3060)"}]
SCREEN_PROFILES = [{"width": 1920, "height": 1080, "depth": 24, "dpr": 1}, {"width": 1440, "height": 900, "depth": 24, "dpr": 2}]
TIMEZONE_PROFILES = [{"tz": "Europe/Berlin", "offset": -60}, {"tz": "America/New_York", "offset": 300}]
FONT_SETS = [["Arial", "Helvetica", "SF Pro Text"], ["Arial", "Calibri", "Segoe UI"], ["Arial", "DejaVu Sans", "Ubuntu"]]
class FingerprintGenerator:
    CACHE_FILE = Path("data/fingerprints.json")
    def __init__(self, profile_name):
        self.profile_name = profile_name
        self.seed = int(hashlib.sha256(profile_name.encode()).hexdigest(), 16)
        self.fingerprint = self._load_or_generate()
    def _deterministic_choice(self, lst, extra_seed=0):
        return lst[(self.seed + extra_seed) % len(lst)]
    def _load_or_generate(self):
        if self.CACHE_FILE.exists():
            with open(self.CACHE_FILE) as f: all_fps = json.load(f); return all_fps.get(self.profile_name, self._generate())
        return self._generate()
    def _generate(self):
        gpu = self._deterministic_choice(GPU_PROFILES, 1)
        screen = self._deterministic_choice(SCREEN_PROFILES, 2)
        tz = self._deterministic_choice(TIMEZONE_PROFILES, 3)
        fonts = self._deterministic_choice(FONT_SETS, 4)
        fp = {"gpu_vendor": gpu["vendor"], "gpu_renderer": gpu["renderer"], "screen_width": screen["width"], "screen_height": screen["height"], "color_depth": screen["depth"], "device_pixel_ratio": screen["dpr"], "timezone": tz["tz"], "timezone_offset": tz["offset"], "fonts": fonts, "canvas_noise": (self.seed % 1000) / 100000.0, "audio_sample_rate": self._deterministic_choice([44100, 48000], 5), "hardware_concurrency": self._deterministic_choice([4, 8, 12, 16], 6), "device_memory": self._deterministic_choice([4, 8, 16, 32], 7), "max_touch_points": 0, "languages": ["de-DE", "de", "en-US", "en"], "platform": self._deterministic_choice(["MacIntel", "Win32", "Linux x86_64"], 9)}
        return fp
    def get_stealth_js(self):
        fp = self.fingerprint; langs = json.dumps(fp["languages"]); fonts = json.dumps(fp["fonts"])
        return "Object.defineProperty(navigator, "webdriver", {get: () => false}); window.chrome = {runtime: {}}; Object.defineProperty(navigator, "languages", {get: () => "+langs+"}); Object.defineProperty(navigator, "platform", {get: () => ""+fp["platform"]+""}); Object.defineProperty(navigator, "hardwareConcurrency", {get: () => "+str(fp["hardware_concurrency"])+"}); Object.defineProperty(navigator, "deviceMemory", {get: () => "+str(fp["device_memory"])+"}); Object.defineProperty(screen, "width", {get: () => "+str(fp["screen_width"])+"}); Object.defineProperty(screen, "height", {get: () => "+str(fp["screen_height"])+"}); console.log("[STEALTH] Loaded: "+fp["gpu_renderer"]);"
