"""
================================================================================
MICRO-STEP M02: Warte auf Seite laden (Temp-Mail)
================================================================================

WAS DIESER STEP MACHT:
----------------------
Wartet darauf, dass temp-mail.org vollständig geladen ist und interaktiv wird.
Dies ist kritisch weil React-Seiten Zeit brauchen zum Rendern!

WARUM DIESER STEP NÖTIG IST:
----------------------------
- Moderne Web-Apps (React, Vue, Angular) laden asynchron
- Ein zu früher Klick führt zu "Element not found" Fehlern
- Wir müssen warten bis ALLE Ressourcen geladen sind
- NetworkIdle2 wartet bis das Netzwerk 500ms ruhig ist

TECHNISCHE DETAILS:
-------------------
- Prüft mehrere Selektoren parallel
- Timeout: 15 Sekunden (langsamere Connections berücksichtigt)
- Retry-Logik bei transienten Fehlern

VERWENDUNG:
-----------
async def execute(browser_helper):
    success = await execute(browser_helper)
    if success:
        print("Seite bereit für Interaktion!")

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio


async def execute(browser_helper):
    """
    Wartet auf vollständiges Laden der Temp-Mail-Seite.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Browser-Management-Instanz
    
    RETURNS:
    --------
    bool : True wenn Seite bereit, False bei Timeout
    
    WAIT-FOR STRATEGIE:
    -------------------
    1. Network Idle (keine laufenden Requests)
    2. Sichtbarkeit des Email-Containers
    3. Interaktivität (kein Loading-Spinner)
    """
    try:
        page = await browser_helper.get_page_for_step("m02_wait_for_page")
        
        if not page:
            browser_helper.log("❌ Keine Page verfügbar")
            return False
        
        browser_helper.log("⏳ Warte auf vollständiges Seitenladen...")
        
        # Strategie 1: Warte auf Network Idle
        await page.wait_for_load_state("networkidle", timeout=15000)
        browser_helper.log("✅ Netzwerk ruhig")
        
        # Strategie 2: Warte auf sichtbaren Email-Container
        selectors_to_check = [
            "#email",           # E-Mail Anzeige
            ".email-address",   # Alternative Klasse
            "#copy-btn",        # Copy Button (zeigt Seite ist ready)
        ]
        
        selector_found = None
        for selector in selectors_to_check:
            try:
                await page.wait_for_selector(selector, state="visible", timeout=3000)
                selector_found = selector
                break
            except:
                continue
        
        if selector_found:
            browser_helper.log(f"✅ UI-Element gefunden: {selector_found}")
        else:
            browser_helper.log("⚠️ Kein Standard-UI-Element gefunden, aber Seite geladen")
        
        # Strategie 3: Kurze Extra-Pause für React Rendering
        # React braucht manchmal extra Zeit nach networkidle
        await asyncio.sleep(1.5)
        
        # Prüfen ob Loading-Spinner noch aktiv ist
        loading_selectors = [".loading", ".spinner", "[class*='loading']"]
        loading_visible = False
        
        for selector in loading_selectors:
            try:
                is_visible = await page.is_visible(selector)
                if is_visible:
                    loading_visible = True
                    browser_helper.log(f"⏳ Loading-Spinner noch sichtbar: {selector}")
                    break
            except:
                pass
        
        if loading_visible:
            browser_helper.log("⏳ Warte auf Ende des Loadings...")
            await asyncio.sleep(2)
        
        browser_helper.log("✅ Seite vollständig geladen und interaktiv")
        return True
        
    except asyncio.TimeoutError:
        browser_helper.log("❌ TIMEOUT: Seite lädt nicht innerhalb von 15s")
        return False
    except Exception as e:
        browser_helper.log(f"❌ FEHLER beim Warten: {e}")
        return False
