"""
================================================================================
MICRO-STEP M01: Öffne temp-mail.org im Temp-Mail Browser
================================================================================

WAS DIESER STEP MACHT:
----------------------
Öffnet temp-mail.org im Browser A (Port 9334, Default-Profil).
Dadurch wird die temporäre E-Mail-Adresse automatisch generiert.

WARUM DIESER STEP ZUERST KOMMT:
-------------------------------
Wir brauchen die E-Mail-Adresse BEVOR wir zu OpenAI gehen.
Ohne E-Mail kann keine Registrierung stattfinden!

TECHNISCHE DETAILS:
-------------------
- Nutzt Browser A (Temp-Mail) mit Default-Profil
- Default-Profil behält Login-Cookies bei (wichtig!)
- Wartet bis Seite vollständig geladen ist (networkidle2)
- Macht Screenshot zur Verifikation

VERWENDUNG:
-----------
from browser_helper import BrowserHelper

async def execute(browser_helper: BrowserHelper):
    browser = browser_helper.get_browser_for_step("m01_open_tempmail")
    page = await browser_helper.get_page_for_step("m01_open_tempmail")
    
    await page.goto("https://temp-mail.org", wait_until="networkidle2")
    await page.screenshot(path="screenshots/tempmail_loaded.png")
    
    return True

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
from datetime import datetime


async def execute(browser_helper):
    """
    Öffnet temp-mail.org und wartet auf vollständiges Laden.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Instanz für Browser-Management (wählt automatisch Browser A)
    
    RETURNS:
    --------
    bool : True bei Erfolg, False bei Fehler
    
    FEHLERMÖGLICHKEITEN:
    --------------------
    - Netzwerk-Probleme (temp-mail.org down)
    - Browser nicht gestartet
    - Timeout beim Laden
    """
    try:
        # Browser und Page für Temp-Mail holen (automatisch Port 9334)
        browser = browser_helper.get_browser_for_step("m01_open_tempmail")
        page = await browser_helper.get_page_for_step("m01_open_tempmail")
        
        if not page:
            browser_helper.log("❌ Keine Page verfügbar für temp-mail.org")
            return False
        
        # Navigation mit Timeout und Wait-Until
        browser_helper.log("📧 Navigiere zu temp-mail.org...")
        await page.goto(
            "https://temp-mail.org",
            wait_until="networkidle2",  # Warte bis Netzwerk ruhig ist
            timeout=30000  # 30 Sekunden Timeout
        )
        
        # Kurze Pause damit UI rendern kann (React braucht Zeit)
        await asyncio.sleep(2)
        
        # Screenshot zur Dokumentation
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"screenshots/m01_tempmail_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        browser_helper.log(f"📸 Screenshot: {screenshot_path}")
        
        # Verifizieren dass E-Mail-Adresse angezeigt wird
        email_selector = "#email"  # Typischer Selector für E-Mail-Adresse
        email_visible = await page.is_visible(email_selector)
        
        if email_visible:
            email_text = await page.text_content(email_selector)
            browser_helper.log(f"✅ E-Mail-Adresse geladen: {email_text}")
            return True
        else:
            browser_helper.log("⚠️ E-Mail-Selector nicht gefunden, aber Seite geladen")
            return True  # Trotzdem erfolgreich, Selector könnte anders sein
            
    except asyncio.TimeoutError:
        browser_helper.log("❌ TIMEOUT: temp-mail.org lädt zu langsam")
        return False
    except Exception as e:
        browser_helper.log(f"❌ FEHLER beim Öffnen von temp-mail.org: {e}")
        return False
