"""
Zentrale Konfiguration - Einmal anpassen, fertig.
"""
from pathlib import Path
import platform
import os

class Config:
    # ============================================================
    # SYSTEM-ERKENNUNG (automatisch)
    # ============================================================
    SYSTEM = platform.system()
    
    if SYSTEM == "Darwin":  # Mac
        CHROME_PATH = str(Path.home() / "Library/Application Support/Google/Chrome")
        CHROME_BINARY = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif SYSTEM == "Windows":
        CHROME_PATH = str(Path.home() / "AppData/Local/Google/Chrome/User Data")
        CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    else:  # Linux
        CHROME_PATH = str(Path.home() / ".config/google-chrome")
        CHROME_BINARY = "/usr/bin/google-chrome"
    
    # ============================================================
    # PROFIL - Dein echtes Chrome Profil
    # ============================================================
    PROFILE_NAME = "Default"  # "Default", "Profile 1", "Profile 2" etc.
    
    # ============================================================
    # MENSCHLICHES VERHALTEN
    # ============================================================
    # Maus
    MOUSE_SPEED_MIN = 0.4        # Sekunden für Mausbewegung (min)
    MOUSE_SPEED_MAX = 1.2        # Sekunden für Mausbewegung (max)
    MOUSE_CURVE_POINTS = 50      # Bezier-Auflösung (mehr = smoother)
    MOUSE_JITTER_PX = 3          # Pixel-Zittern (menschliche Hand)
    MOUSE_OVERSHOOT_CHANCE = 0.15  # 15% Chance leicht über Ziel hinauszuschießen
    
    # Tippen
    TYPE_SPEED_MIN = 0.035       # Sekunden pro Zeichen (min)
    TYPE_SPEED_MAX = 0.155       # Sekunden pro Zeichen (max)
    TYPE_PAUSE_CHANCE = 0.09     # 9% Chance auf Denkpause beim Tippen
    TYPE_PAUSE_MIN = 0.3
    TYPE_PAUSE_MAX = 0.9
    TYPE_TYPO_CHANCE = 0.02      # 2% Chance auf Tippfehler + Korrektur
    
    # Allgemein
    THINK_TIME_MIN = 1.5
    THINK_TIME_MAX = 4.5
    
    # ============================================================
    # VISION / OCR
    # ============================================================
    USE_VISION_CLICKS = True     # OS-Level Mausklicks statt DOM-Klicks
    OCR_LANGUAGES = ['en', 'de']
    OCR_CONFIDENCE = 0.55
    SCREENSHOT_DIR = Path("data/screenshots")
    
    # ============================================================
    # PROXY (optional)
    # ============================================================
    USE_PROXY = False
    PROXY_LIST = [
        # "socks5://user:pass@host:port",
        # "http://user:pass@host:port",
    ]
    PROXY_ROTATE_AFTER = 10      # Nach X Requests rotieren
    
    # ============================================================
    # SESSION
    # ============================================================
    SESSION_DIR = Path("data/sessions")
    SESSION_ENCRYPT_KEY = os.getenv("SESSION_KEY", "change-this-to-random-key-32!!")
    
    # ============================================================
    # FINGERPRINT
    # ============================================================
    FINGERPRINT_CONSISTENT = True  # Gleicher Fingerprint pro Profil
    
    @classmethod
    def init_dirs(cls):
        """Erstelle benötigte Verzeichnisse"""
        cls.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        cls.SESSION_DIR.mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(exist_ok=True)

Config.init_dirs()
