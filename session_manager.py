"""
Session-Management mit Verschlüsselung
Speichert und lädt Browser-Sessions (Cookies, Storage, etc.)
"""
import json
import time
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from config import Config


class SessionManager:
    def __init__(self, profile_name: str = "default"):
        self.profile_name = profile_name
        self.session_file = Config.SESSION_DIR / f"{profile_name}.session"
        self.cipher = self._create_cipher()
    
    def _create_cipher(self) -> Fernet:
        """Erstellt Verschlüsselungs-Cipher aus dem Key"""
        key_bytes = Config.SESSION_ENCRYPT_KEY.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"stealth_browser_salt_2025",
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        return Fernet(key)
    
    def save_session(self, cookies: list, local_storage: dict = None,
                     extra_data: dict = None):
        """Speichert Session-Daten verschlüsselt"""
        session_data = {
            "profile": self.profile_name,
            "timestamp": time.time(),
            "cookies": cookies,
            "local_storage": local_storage or {},
            "extra": extra_data or {},
        }
        
        json_bytes = json.dumps(session_data).encode()
        encrypted = self.cipher.encrypt(json_bytes)
        
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_file, "wb") as f:
            f.write(encrypted)
        
        print(f"💾 Session gespeichert: {self.profile_name} "
              f"({len(cookies)} Cookies)")
    
    def load_session(self) -> dict | None:
        """Lädt Session-Daten"""
        if not self.session_file.exists():
            print(f"ℹ️  Keine gespeicherte Session für: {self.profile_name}")
            return None
        
        try:
            with open(self.session_file, "rb") as f:
                encrypted = f.read()
            
            decrypted = self.cipher.decrypt(encrypted)
            session_data = json.loads(decrypted)
            
            age_hours = (time.time() - session_data["timestamp"]) / 3600
            print(f"📂 Session geladen: {self.profile_name} "
                  f"({len(session_data[\'cookies\'])} Cookies, {age_hours:.1f}h alt)")
            
            return session_data
        except Exception as e:
            print(f"❌ Session-Laden fehlgeschlagen: {e}")
            return None
    
    def delete_session(self):
        """Löscht gespeicherte Session"""
        if self.session_file.exists():
            self.session_file.unlink()
            print(f"🗑️  Session gelöscht: {self.profile_name}")
    
    async def extract_cookies(self, page) -> list:
        """Extrahiert Cookies aus dem Browser"""
        try:
            cookies = await page.send(
                page._tree.target,
                "Network.getAllCookies"
            )
            return cookies.get("cookies", [])
        except Exception as e:
            print(f"⚠️  Cookie-Extraktion fehlgeschlagen: {e}")
            return []
    
    async def inject_cookies(self, page, cookies: list):
        """Injiziert Cookies in den Browser"""
        for cookie in cookies:
            try:
                params = {
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": cookie.get("domain", ""),
                    "path": cookie.get("path", "/"),
                }
                if "expires" in cookie:
                    params["expires"] = cookie["expires"]
                if "httpOnly" in cookie:
                    params["httpOnly"] = cookie["httpOnly"]
                if "secure" in cookie:
                    params["secure"] = cookie["secure"]
                
                await page.send(
                    page._tree.target,
                    "Network.setCookie",
                    **params
                )
            except Exception:
                pass
        
        print(f"🍪 {len(cookies)} Cookies injiziert")
    
    async def save_current(self, page):
        """Shortcut: Aktuelle Session speichern"""
        cookies = await self.extract_cookies(page)
        self.save_session(cookies)
    
    async def restore(self, page):
        """Shortcut: Session wiederherstellen"""
        session = self.load_session()
        if session:
            await self.inject_cookies(page, session["cookies"])
            return True
        return False