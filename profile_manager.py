"""
Profil-Rotation und -Management
Verwaltet mehrere Chrome-Profile für Rotation.
"""
import json
import random
import time
from pathlib import Path
from config import Config
from fingerprint import FingerprintGenerator


class ProfileManager:
    PROFILES_FILE = Path("data/profiles.json")
    
    def __init__(self):
        self.profiles = self._load_profiles()
        self.current_profile = None
    
    def _load_profiles(self) -> dict:
        """Lade Profil-Datenbank"""
        if self.PROFILES_FILE.exists():
            with open(self.PROFILES_FILE) as f:
                return json.load(f)
        
        # Standard-Profile erstellen
        default_profiles = {
            "default": {
                "chrome_profile": "Default",
                "created": time.time(),
                "last_used": 0,
                "use_count": 0,
                "cooldown_hours": 2,
                "notes": "Hauptprofil"
            }
        }
        self._save_profiles(default_profiles)
        return default_profiles
    
    def _save_profiles(self, profiles=None):
        profiles = profiles or self.profiles
        self.PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=2)
    
    def add_profile(self, name: str, chrome_profile: str, cooldown_hours=2):
        """Neues Profil hinzufügen"""
        self.profiles[name] = {
            "chrome_profile": chrome_profile,
            "created": time.time(),
            "last_used": 0,
            "use_count": 0,
            "cooldown_hours": cooldown_hours,
            "notes": ""
        }
        self._save_profiles()
        
        # Fingerprint generieren
        FingerprintGenerator(name)
        print(f"✅ Profil '{name}' hinzugefügt (Chrome: {chrome_profile})")
    
    def get_available_profiles(self) -> list:
        """Profile die nicht im Cooldown sind"""
        available = []
        now = time.time()
        
        for name, data in self.profiles.items():
            cooldown_seconds = data.get("cooldown_hours", 2) * 3600
            time_since_use = now - data.get("last_used", 0)
            
            if time_since_use >= cooldown_seconds:
                available.append(name)
        
        return available
    
    def select_profile(self, name: str = None) -> dict:
        """
        Wählt ein Profil aus.
        Ohne Name: Wählt das am längsten nicht benutzte verfügbare Profil.
        """
        if name:
            if name not in self.profiles:
                raise ValueError(f"Profil '{name}' nicht gefunden")
            profile = self.profiles[name]
        else:
            available = self.get_available_profiles()
            if not available:
                print("⚠️  Alle Profile im Cooldown! Nehme das älteste...")
                available = list(self.profiles.keys())
            
            # Wähle das am längsten nicht benutzte
            available.sort(key=lambda n: self.profiles[n].get("last_used", 0))
            name = available[0]
            profile = self.profiles[name]
        
        # Update Usage
        profile["last_used"] = time.time()
        profile["use_count"] = profile.get("use_count", 0) + 1
        self._save_profiles()
        
        # Fingerprint laden
        fp_gen = FingerprintGenerator(name)
        
        c_prof = profile["chrome_profile"]
        gpu = fp_gen.fingerprint["gpu_renderer"]
        
        self.current_profile = {
            "name": name,
            "chrome_profile": c_prof,
            "fingerprint": fp_gen.fingerprint,
            "stealth_js": fp_gen.get_stealth_js(),
        }
        
        print(f"👤 Profil gewählt: {name} (Chrome: {c_prof}, GPU: {gpu})")
        
        return self.current_profile
    
    def get_chrome_profile_dir(self) -> str:
        """Gibt den Chrome Profile Directory Namen zurück"""
        if self.current_profile:
            return self.current_profile["chrome_profile"]
        return Config.PROFILE_NAME
    
    def list_profiles(self):
        """Zeigt alle Profile"""
        print("\n📋 Profile:")
        print("-" * 60)
        now = time.time()
        for name, data in self.profiles.items():
            last_used = data.get("last_used", 0)
            if last_used > 0:
                ago = (now - last_used) / 3600
                last_str = f"vor {ago:.1f}h"
            else:
                last_str = "nie"
            
            available = self.get_available_profiles()
            status = "✅" if name in available else "⏳"
            
            cp = data["chrome_profile"]
            uc = data.get("use_count", 0)
            
            print(f"  {status} {name:20s} Chrome:{cp:15s} "
                  f"Benutzt:{uc:3d}x  Zuletzt:{last_str}")
        print("-" * 60)