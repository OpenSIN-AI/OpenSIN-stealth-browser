"""
Fingerprint Consistency Layer
Generiert einen konsistenten Hardware-Fingerprint pro Profil.
Gleicher Profil-Name = gleicher Fingerprint. Immer.
"""
import hashlib
import json
from pathlib import Path


# Realistische GPU/Renderer Kombinationen (echte Hardware)
GPU_PROFILES = [
    {"vendor": "Intel Inc.", "renderer": "Intel(R) UHD Graphics 630"},
    {"vendor": "Intel Inc.", "renderer": "Intel(R) Iris(TM) Plus Graphics 655"},
    {"vendor": "Apple", "renderer": "Apple M1"},
    {"vendor": "Apple", "renderer": "Apple M2"},
    {"vendor": "Apple", "renderer": "Apple M3 Pro"},
    {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA GeForce RTX 3060)"},
    {"vendor": "Google Inc. (NVIDIA)", "renderer": "ANGLE (NVIDIA GeForce RTX 4070)"},
    {"vendor": "Google Inc. (AMD)", "renderer": "ANGLE (AMD Radeon RX 6700 XT)"},
]

SCREEN_PROFILES = [
    {"width": 1920, "height": 1080, "depth": 24, "dpr": 1},
    {"width": 2560, "height": 1440, "depth": 24, "dpr": 1},
    {"width": 1440, "height": 900, "depth": 24, "dpr": 2},    # MacBook
    {"width": 1512, "height": 982, "depth": 30, "dpr": 2},    # MacBook Pro 14"
    {"width": 1728, "height": 1117, "depth": 30, "dpr": 2},   # MacBook Pro 16"
    {"width": 3840, "height": 2160, "depth": 24, "dpr": 1.5}, # 4K
]

TIMEZONE_PROFILES = [
    {"tz": "Europe/Berlin", "offset": -60},
    {"tz": "Europe/London", "offset": 0},
    {"tz": "America/New_York", "offset": 300},
    {"tz": "America/Los_Angeles", "offset": 480},
    {"tz": "Asia/Tokyo", "offset": -540},
]

FONT_SETS = [
    # Mac
    ["Arial", "Helvetica", "Helvetica Neue", "Times New Roman", "Courier New",
     "Georgia", "Palatino", "Bookman", "Comic Sans MS", "Trebuchet MS",
     "Arial Black", "Impact", "Lucida Grande", "Tahoma", "Verdana",
     "Monaco", "Menlo", "SF Pro Text", "SF Pro Display"],
    # Windows
    ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia",
     "Lucida Console", "Microsoft Sans Serif", "Segoe UI", "Tahoma",
     "Times New Roman", "Trebuchet MS", "Verdana", "Webdings", "Wingdings"],
    # Linux
    ["Arial", "DejaVu Sans", "DejaVu Serif", "FreeMono", "Liberation Mono",
     "Liberation Sans", "Liberation Serif", "Noto Sans", "Ubuntu", "Cantarell"],
]


class FingerprintGenerator:
    """Generiert konsistenten Fingerprint basierend auf Profil-Seed"""
    
    CACHE_FILE = Path("data/fingerprints.json")
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.seed = int(hashlib.sha256(profile_name.encode()).hexdigest(), 16)
        self.fingerprint = self._load_or_generate()
    
    def _deterministic_choice(self, lst, extra_seed=0):
        """Wählt deterministisch basierend auf Seed"""
        idx = (self.seed + extra_seed) % len(lst)
        return lst[idx]
    
    def _load_or_generate(self) -> dict:
        """Lade existierenden Fingerprint oder generiere neuen"""
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE) as f:
                    all_fps = json.load(f)
                    if self.profile_name in all_fps:
                        return all_fps[self.profile_name]
            except Exception:
                pass
        
        fp = self._generate()
        self._save(fp)
        return fp
    
    def _generate(self) -> dict:
        gpu = self._deterministic_choice(GPU_PROFILES, 1)
        screen = self._deterministic_choice(SCREEN_PROFILES, 2)
        tz = self._deterministic_choice(TIMEZONE_PROFILES, 3)
        fonts = self._deterministic_choice(FONT_SETS, 4)
        
        # Canvas-Noise: Konsistenter kleiner Offset
        canvas_noise = (self.seed % 1000) / 100000.0
        
        fp = {
            "gpu_vendor": gpu["vendor"],
            "gpu_renderer": gpu["renderer"],
            "screen_width": screen["width"],
            "screen_height": screen["height"],
            "color_depth": screen["depth"],
            "device_pixel_ratio": screen["dpr"],
            "timezone": tz["tz"],
            "timezone_offset": tz["offset"],
            "fonts": fonts,
            "canvas_noise": canvas_noise,
            "audio_sample_rate": self._deterministic_choice([44100, 48000], 5),
            "hardware_concurrency": self._deterministic_choice([4, 8, 10, 12, 16], 6),
            "device_memory": self._deterministic_choice([4, 8, 16, 32], 7),
            "max_touch_points": 0,
            "languages": self._deterministic_choice(
                [["de-DE", "de", "en-US", "en"], ["en-US", "en"], ["en-GB", "en"]], 8
            ),
            "platform": self._deterministic_choice(
                ["MacIntel", "Win32", "Linux x86_64"], 9
            ),
        }
        return fp
    
    def _save(self, fp: dict):
        all_fps = {}
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE) as f:
                    all_fps = json.load(f)
            except Exception:
                all_fps = {}
        all_fps[self.profile_name] = fp
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CACHE_FILE, "w") as f:
            json.dump(all_fps, f, indent=2)
    
    def get_stealth_js(self) -> str:
        """Generiert das komplette Stealth-Injection-JavaScript"""
        fp = self.fingerprint
        fonts_js = json.dumps(fp["fonts"])
        langs_js = json.dumps(fp["languages"])
        
        return f"""
        // ========== WEBDRIVER ==========
        Object.defineProperty(navigator, 'webdriver', {{get: () => false}});
        delete navigator.__proto__.webdriver;
        
        // ========== CHROME RUNTIME ==========
        window.chrome = {{
            runtime: {{
                onMessage: undefined,
                sendMessage: undefined,
                connect: undefined,
                getManifest: function() {{ return {{}}; }}
            }},
            loadTimes: function() {{ return {{}}; }},
            csi: function() {{ return {{}}; }}
        }};
        
        // ========== PERMISSIONS ==========
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: Notification.permission }}) :
                originalQuery(parameters)
        );
        
        // ========== PLUGINS ==========
        Object.defineProperty(navigator, 'plugins', {{
            get: () => [
                {{ name: "Chrome PDF Plugin", filename: "internal-pdf-viewer" }},
                {{ name: "Chrome PDF Viewer", filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai" }},
                {{ name: "Native Client", filename: "internal-nacl-plugin" }}
            ]
        }});
        
        // ========== LANGUAGES ==========
        Object.defineProperty(navigator, 'languages', {{
            get: () => {langs_js}
        }});
        
        // ========== PLATFORM ==========
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{fp["platform"]}'
        }});
        
        // ========== HARDWARE ==========
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {fp["hardware_concurrency"]}
        }});
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {fp["device_memory"]}
        }});
        Object.defineProperty(navigator, 'maxTouchPoints', {{
            get: () => {fp["max_touch_points"]}
        }});
        
        // ========== SCREEN ==========
        Object.defineProperty(screen, 'width', {{ get: () => {fp["screen_width"]} }});
        Object.defineProperty(screen, 'height', {{ get: () => {fp["screen_height"]} }});
        Object.defineProperty(screen, 'availWidth', {{ get: () => {fp["screen_width"]} }});
        Object.defineProperty(screen, 'availHeight', {{ get: () => {fp["screen_height"] - 40} }});
        Object.defineProperty(screen, 'colorDepth', {{ get: () => {fp["color_depth"]} }});
        Object.defineProperty(window, 'devicePixelRatio', {{ get: () => {fp["device_pixel_ratio"]} }});
        
        // ========== WEBGL ==========
        const getParameterOrig = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{fp["gpu_vendor"]}';
            if (param === 37446) return '{fp["gpu_renderer"]}';
            return getParameterOrig.apply(this, arguments);
        }};
        
        const getParameterOrig2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{fp["gpu_vendor"]}';
            if (param === 37446) return '{fp["gpu_renderer"]}';
            return getParameterOrig2.apply(this, arguments);
        }};
        
        // ========== CANVAS FINGERPRINT NOISE ==========
        const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {{
            const ctx = this.getContext('2d');
            if (ctx) {{
                const imgData = ctx.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imgData.data.length; i += 4) {{
                    imgData.data[i] = imgData.data[i] + ({fp["canvas_noise"]} * (i % 3));
                }}
                ctx.putImageData(imgData, 0, 0);
            }}
            return origToDataURL.apply(this, arguments);
        }};
        
        // ========== AUDIO CONTEXT ==========
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {{
            const origCreateOscillator = AudioCtx.prototype.createOscillator;
            Object.defineProperty(AudioCtx.prototype, 'sampleRate', {{
                get: () => {fp["audio_sample_rate"]}
            }});
        }}
        
        // ========== BATTERY API (verbergen) ==========
        delete navigator.getBattery;
        Object.defineProperty(navigator, 'getBattery', {{
            value: undefined
        }});
        
        // ========== SPEECH SYNTHESIS ==========
        if (window.speechSynthesis) {{
            Object.defineProperty(window.speechSynthesis, 'getVoices', {{
                value: () => []
            }});
        }}
        
        // ========== FONT DETECTION BLOCKER ==========
        const knownFonts = new Set({fonts_js});
        const origOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth');
        
        // ========== IFRAME CONTENTWINDOW ==========
        const origContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
        if (origContentWindow) {{
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {{
                get: function() {{
                    const win = origContentWindow.get.call(this);
                    if (win) {{
                        try {{
                            Object.defineProperty(win.navigator, 'webdriver', {{get: () => false}});
                        }} catch(e) {{}}
                    }}
                    return win;
                }}
            }});
        }}
        
        console.log('[STEALTH] Fingerprint loaded: {fp["gpu_renderer"]}');
        """