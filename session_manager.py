import json, time, base64; from pathlib import Path; from cryptography.fernet import Fernet; from config import Config
class SessionManager:
    def __init__(self, name): self.name = name; self.file = Config.SESSION_DIR / f"{name}.session"
    async def restore(self, page): return False
    async def save_current(self, page): pass