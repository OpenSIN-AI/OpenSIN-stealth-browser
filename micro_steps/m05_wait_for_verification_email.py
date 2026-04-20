"""
================================================================================
MICRO-STEP M05: Warte auf Verifizierungs-E-Mail von OpenAI
================================================================================

WAS DIESER STEP MACHT:
----------------------
Überwacht den Temp-Mail Posteingang und wartet auf die Bestätigungs-E-Mail
von OpenAI mit dem Verifizierungscode.

WARUM DIESER STEP ZEITKRITISCH IST:
-----------------------------------
- OpenAI sendet die Mail innerhalb von 5-60 Sekunden
- Wir müssen regelmäßig den Posteingang refreshen
- Timeout nach 90 Sekunden (danach Retry oder Abbruch)
- E-Mail kann im Spam landen (bei temp-mail.org selten)

TECHNISCHE DETAILS:
-------------------
- Polling alle 3 Sekunden
- Erkennt E-Mail an Absender "OpenAI" oder Betreff "Verify"
- Extrahiert automatisch den 6-stelligen Code
- Refresh-Inbox Button wird geklickt wenn keine Mail da ist

VERWENDUNG:
-----------
async def execute(browser_helper):
    code = await execute(browser_helper)
    # code ist jetzt z.B. "123456"

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
import re


# Globale Variable für den Code (wird von anderen Steps gelesen)
VERIFICATION_CODE = None


async def execute(browser_helper):
    """
    Überwacht Temp-Mail Posteingang bis Verifizierungs-Mail kommt.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Browser-Management-Instanz
    
    RETURNS:
    --------
    str or None : Verifizierungscode bei Erfolg, None bei Timeout
    
    TIMEOUT:
    --------
    90 Sekunden maximal (typisch: 10-30 Sekunden)
    """
    global VERIFICATION_CODE
    
    try:
        page = await browser_helper.get_page_for_step("m05_wait_for_verification_email")
        
        if not page:
            browser_helper.log("❌ Keine Page verfügbar")
            return None
        
        browser_helper.log("📬 Warte auf Verifizierungs-E-Mail von OpenAI...")
        
        max_wait_time = 90  # Sekunden
        poll_interval = 3   # Sekunden
        elapsed = 0
        
        while elapsed < max_wait_time:
            elapsed += poll_interval
            
            # Prüfen ob E-Mail da ist
            code = await check_for_verification_email(page, browser_helper)
            
            if code:
                VERIFICATION_CODE = code
                browser_helper.log(f"✅ Verifizierungscode erhalten: {code}")
                return code
            
            # Noch keine Mail - Inbox refreshen
            browser_helper.log(f"⏳ Noch keine E-Mail ({elapsed}s/{max_wait_time}s), refresh...")
            await refresh_inbox(page, browser_helper)
            
            await asyncio.sleep(poll_interval)
        
        # Timeout erreicht
        browser_helper.log(f"❌ TIMEOUT: Keine E-Mail nach {max_wait_time}s")
        return None
        
    except Exception as e:
        browser_helper.log(f"❌ FEHLER beim Warten auf E-Mail: {e}")
        return None


async def check_for_verification_email(page, browser_helper):
    """
    Prüft ob Verifizierungs-E-Mail im Posteingang ist.
    
    Sucht nach:
    - E-Mail von "OpenAI" oder "no-reply@openai.com"
    - Betreff mit "verify", "confirm", "code"
    - 6-stelliger Code im Inhalt
    
    RETURNS: str (Code) oder None
    """
    try:
        # Selektoren für E-Mail-Liste
        email_selectors = [
            ".email-item",           # Typische E-Mail-Kachel
            ".message",              # Alternative Klasse
            "[data-message-id]",     # Data-Attribute
            ".inbox-item",           # Inbox Item
        ]
        
        for selector in email_selectors:
            try:
                emails = await page.query_selector_all(selector)
                if emails:
                    browser_helper.log(f"✅ {len(emails)} E-Mails gefunden")
                    
                    # Jede E-Mail prüfen
                    for email in emails:
                        # Textinhalt der E-Mail holen
                        email_text = await email.text_content()
                        
                        if email_text:
                            # Nach OpenAI suchen
                            if "openai" in email_text.lower():
                                browser_helper.log("🔍 OpenAI E-Mail gefunden!")
                                
                                # Nach 6-stelligem Code suchen
                                code_match = re.search(r'\b\d{6}\b', email_text)
                                if code_match:
                                    code = code_match.group()
                                    browser_helper.log(f"✅ Code extrahiert: {code}")
                                    return code
                                    
            except Exception as e:
                continue
        
        # Alternative: Nach Code direkt im Hauptbereich suchen
        try:
            page_content = await page.content()
            if "openai" in page_content.lower():
                code_match = re.search(r'\b\d{6}\b', page_content)
                if code_match:
                    code = code_match.group()
                    browser_helper.log(f"✅ Code im Page-Content: {code}")
                    return code
        except:
            pass
        
        return None
        
    except Exception as e:
        browser_helper.log(f"⚠️ Fehler beim Prüfen: {e}")
        return None


async def refresh_inbox(page, browser_helper):
    """
    Klickt den Refresh-Button um neue E-Mails zu laden.
    """
    try:
        refresh_selectors = [
            "#refresh",              # Refresh Button ID
            ".refresh-btn",          # Refresh Klasse
            "[aria-label*='refresh']",  # Aria Label
            "button:has-text('Refresh')",  # Text Button
        ]
        
        for selector in refresh_selectors:
            try:
                refresh_btn = await page.query_selector(selector)
                if refresh_btn:
                    await refresh_btn.click()
                    browser_helper.log("🔄 Inbox refreshed")
                    await asyncio.sleep(2)  # Warten auf Reload
                    return
            except:
                continue
        
        # Fallback: Seite neu laden
        browser_helper.log("⚠️ Kein Refresh-Button, lade Seite neu...")
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(2)
        
    except Exception as e:
        browser_helper.log(f"⚠️ Refresh fehlgeschlagen: {e}")


def get_current_code():
    """
    Helper um den gespeicherten Code abzurufen.
    """
    return VERIFICATION_CODE
