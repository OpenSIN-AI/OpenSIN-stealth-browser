"""
================================================================================
MICRO-STEP M04: E-Mail-Adresse extrahieren und speichern
================================================================================

WAS DIESER STEP MACHT:
----------------------
Liest die temporäre E-Mail-Adresse von temp-mail.org aus und speichert sie
für spätere Schritte (wird für OpenAI Registrierung benötigt).

WARUM DIESER STEP KRITISCH IST:
-------------------------------
- Ohne E-Mail-Adresse kann keine OpenAI Registrierung stattfinden
- Die Adresse muss exakt kopiert werden (kein Platz für Fehler)
- Wir müssen die Adresse zwischen Steps persistent speichern

TECHNISCHE DETAILS:
-------------------
- Extrahiert E-Mail aus dem UI-Element
- Speichert in globaler Variable für andere Steps
- Validiert E-Mail-Format mit Regex
- Fallback: Versucht mehrere Selektoren

VERWENDUNG:
-----------
async def execute(browser_helper):
    email = await execute(browser_helper)
    # email ist jetzt verfügbar für m08_enter_email.py

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
import re


# Globale Variable zum Speichern der E-Mail (wird von anderen Steps gelesen)
CURRENT_TEMP_EMAIL = None


async def execute(browser_helper):
    """
    Extrahiert die Temp-Mail-E-Mail-Adresse und speichert sie global.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Browser-Management-Instanz
    
    RETURNS:
    --------
    str or None : E-Mail-Adresse bei Erfolg, None bei Fehler
    
    GLOBAL STATE:
    -------------
    Setzt CURRENT_TEMP_EMAIL Variable für andere Steps
    """
    global CURRENT_TEMP_EMAIL
    
    try:
        page = await browser_helper.get_page_for_step("m04_get_email_address")
        
        if not page:
            browser_helper.log("❌ Keine Page verfügbar")
            return None
        
        browser_helper.log("📧 Extrahiere E-Mail-Adresse...")
        
        # Mehrere Selektoren versuchen (temp-mail.org ändert manchmal das Layout)
        selectors = [
            "#email",                    # Haupt-Selector
            ".email-address",            # Alternative Klasse
            "[data-email]",              # Data-Attribute
            "#copy",                     # Copy Button Text
            ".mailbox-name",             # Mailbox-Anzeige
        ]
        
        email_text = None
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    # Erst versuchen textContent zu holen
                    email_text = await element.text_content()
                    
                    # Falls leer, value Attribute versuchen (bei Input-Feldern)
                    if not email_text or not email_text.strip():
                        email_text = await element.get_attribute("value")
                    
                    if email_text:
                        email_text = email_text.strip()
                        browser_helper.log(f"✅ Kandidat gefunden mit {selector}: {email_text}")
                        break
            except Exception as e:
                browser_helper.log(f"⚠️ Selector {selector} fehlgeschlagen: {e}")
                continue
        
        if not email_text:
            browser_helper.log("❌ Keine E-Mail-Adresse gefunden!")
            return None
        
        # E-Mail validieren mit Regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email_text):
            browser_helper.log(f"⚠️ E-Mail sieht ungültig aus: {email_text}")
            # Trotzdem weitermachen, könnte false positive sein
        
        # Global speichern für andere Steps
        CURRENT_TEMP_EMAIL = email_text
        browser_helper.log(f"✅ E-Mail gespeichert: {CURRENT_TEMP_EMAIL}")
        
        # In Session Storage speichern als Backup
        try:
            await page.evaluate(f"sessionStorage.setItem('temp_email', '{email_text}')")
            browser_helper.log("💾 Auch in Session Storage gespeichert")
        except Exception as e:
            browser_helper.log(f"⚠️ Session Storage fehlgeschlagen: {e}")
        
        return email_text
        
    except Exception as e:
        browser_helper.log(f"❌ FEHLER beim Extrahieren der E-Mail: {e}")
        return None


def get_current_email():
    """
    Helper-Funktion um die gespeicherte E-Mail abzurufen.
    
    RETURNS:
    --------
    str or None : Die zuletzt extrahierte E-Mail-Adresse
    """
    return CURRENT_TEMP_EMAIL
