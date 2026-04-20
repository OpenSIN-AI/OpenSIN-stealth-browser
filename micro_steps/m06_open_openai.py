"""
================================================================================
MICRO-STEP M06: Öffne OpenAI im Incognito Browser
================================================================================

WAS DIESER STEP MACHT:
----------------------
Öffnet openai.com/signup im Browser B (Port 9335, Incognito-Modus).
Dies startet den Registrierungsprozess für ein neues OpenAI-Konto.

WARUM INCOGNITO HIER KRITISCH IST:
----------------------------------
- Incognito = frische Session ohne alte Cookies
- Verhindert dass OpenAI vorherige Registrierungen trackt
- Jede Registration sieht aus wie von einem neuen User
- Default-Profil würde Fingerprint mit alten Sessions verknüpfen

TECHNISCHE DETAILS:
-------------------
- Nutzt Browser B (OpenAI) auf Port 9335
- Geht direkt zu /signup (spart Redirects)
- Wartet auf vollständiges Laden (networkidle2)
- Wendet STEALTH ENGINE an (Anti-Detection!)

VERWENDUNG:
-----------
async def execute(browser_helper):
    success = await execute(browser_helper)
    # OpenAI Signup-Seite ist jetzt geladen

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
from datetime import datetime


async def execute(browser_helper):
    """
    Öffnet OpenAI Signup im Incognito Browser mit Stealth.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Instanz für Browser-Management (wählt automatisch Browser B)
    
    RETURNS:
    --------
    bool : True bei Erfolg, False bei Fehler
    
    ANTI-DETECTION:
    ---------------
    - Stealth Engine wird automatisch angewendet
    - Fingerprint-Spoofing aktiv
    - Human-Timing eingebaut
    """
    try:
        # Browser und Page für OpenAI holen (automatisch Port 9335, Incognito)
        browser = browser_helper.get_browser_for_step("m06_open_openai")
        page = await browser_helper.get_page_for_step("m06_open_openai")
        
        if not page:
            browser_helper.log("❌ Keine Page verfügbar für OpenAI")
            return False
        
        browser_helper.log("🤖 Navigiere zu OpenAI Signup (Incognito)...")
        
        # STEALTH ENGINE anwenden BEVOR wir interagieren!
        # Das setzt alle Anti-Detection Scripts
        try:
            from stealth_engine import StealthEngine
            engine = StealthEngine()
            await engine.apply_stealth(page)
            browser_helper.log("🕵️ Stealth Engine angewendet!")
        except ImportError:
            browser_helper.log("⚠️ Stealth Engine nicht gefunden (optional)")
        
        # Direkt zur Signup-Seite navigieren (spart Redirects)
        await page.goto(
            "https://auth.openai.com/signup",
            wait_until="networkidle2",
            timeout=30000
        )
        
        # Kurze Pause für React Rendering
        await asyncio.sleep(2)
        
        # Screenshot zur Dokumentation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/m06_openai_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        browser_helper.log(f"📸 Screenshot: {screenshot_path}")
        
        # Verifizieren dass Signup-Formular geladen ist
        signup_indicators = [
            "input[type='email']",      # E-Mail Input
            "button[type='submit']",    # Submit Button
            "#email",                   # Email Feld ID
            "[name='email']",           # Email Field Name
        ]
        
        form_found = False
        for selector in signup_indicators:
            try:
                is_visible = await page.is_visible(selector)
                if is_visible:
                    browser_helper.log(f"✅ Signup-Formular erkannt: {selector}")
                    form_found = True
                    break
            except:
                continue
        
        if not form_found:
            browser_helper.log("⚠️ Signup-Formular nicht eindeutig erkannt, aber Seite geladen")
        
        # Prüfen ob wir schon eingeloggt sind (Session von früher)
        try:
            current_url = page.url
            if "chat.openai.com" in current_url:
                browser_helper.log("⚠️ Bereits eingeloggt! Vielleicht alte Session?")
                # In Incognito sollte das nicht passieren
        except:
            pass
        
        browser_helper.log("✅ OpenAI Signup-Seite erfolgreich geladen")
        return True
        
    except asyncio.TimeoutError:
        browser_helper.log("❌ TIMEOUT: OpenAI lädt zu langsam (>30s)")
        return False
    except Exception as e:
        browser_helper.log(f"❌ FEHLER beim Öffnen von OpenAI: {e}")
        return False
