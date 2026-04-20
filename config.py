"""
Zentrale Konfiguration - Einmal anpassen, fertig.
"""
from pathlib import Path
import platform
import os

class Config:
    SYSTEM = platform.system()
    if SYSTEM == "Darwin":
        CHROME_PATH = str(Path.home() / "Library/Application Support/Google/Chrome")
        CHROME_BINARY = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    elif SYSTEM == "Windows":
        CHROME_PATH = str(Path.home() / "AppData/Local/Google/Chrome/User Data")
        CHROME_BINARY = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    else:
        CHROME_PATH = str(Path.home() / ".config/google-chrome")
        CHROME_BINARY = "/usr/bin/google-chrome"
    PROFILE_NAME = "Default"
    MOUSE_SPEED_MIN = 0.4
    MOUSE_SPEED_MAX = 1.2
    MOUSE_CURVE_POINTS = 50
    MOUSE_JITTER_PX = 3
    MOUSE_OVERSHOOT_CHANCE = 0.15
    TYPE_SPEED_MIN = 0.035
    TYPE_SPEED_MAX = 0.155
    TYPE_PAUSE_CHANCE = 0.09
    TYPE_PAUSE_MIN = 0.3
    TYPE_PAUSE_MAX = 0.9
    TYPE_TYPO_CHANCE = 0.02
    THINK_TIME_MIN = 1.5
    THINK_TIME_MAX = 4.5
    USE_VISION_CLICKS = True
    OCR_LANGUAGES = [\'en\', \'de\']
    OCR_CONFIDENCE = 0.55
    SCREENSHOT_DIR = Path("data/screenshots")
    USE_PROXY = False
    PROXY_LIST = []
    PROXY_ROTATE_AFTER = 10
    SESSION_DIR = Path("data/sessions")
    SESSION_ENCRYPT_KEY = os.getenv("SESSION_KEY", "change-this-to-random-key-32!!")
    FINGERPRINT_CONSISTENT = True
    @classmethod
    def init_dirs(cls):
        cls.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        cls.SESSION_DIR.mkdir(parents=True, exist_ok=True)
        Path("data").mkdir(exist_ok=True)
Config.init_dirs()