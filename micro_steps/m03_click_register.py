"""
================================================================================
MICRO-STEP M03: Click Register Button mit STEALTH ENGINE
================================================================================

WAS DIESER STEP MACHT:
----------------------
Klickt auf den "Register" oder "Sign Up" Button auf der OpenAI Login-Seite.

WARUM STEALTH HIER WICHTIG IST:
-------------------------------
OpenAI trackt JEDEN Klick! Ein robotischer Klick = SOFORT GEBLOCKT!
Dieser Step verwendet:
- Bezier-Mouse Movement (nicht linear!)
- Human Click Pressure (0.8-1.0 force)
- Random Delays vor/nach dem Klick

VERWENDUNG:
-----------
from browser_helper import BrowserHelper

async def execute(browser_helper: BrowserHelper):
    browser = browser_helper.get_browser_for_step("m03_click_register")
    page = await browser_helper.get_page_for_step("m03_click_register")
    
    # Stealth Click ausführen
    success = await human_stealth_click(page, "Register")
    
    return success

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
import random
from stealth_engine import stealth


async def execute(browser_helper):
    """
    Hauptfunktion des Micro-Steps.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Instanz des BrowserHelpers für Dual-Browser Management
        
    RETURNS:
    --------
    bool: True wenn erfolgreich, False sonst
    
    RAISES:
    -------
    Exception: Wenn kritischer Fehler auftritt
    """
    print("\n[M03] Clicking Register Button...")
    
    try:
        # RICHTIGEN Browser holen (OpenAI Incognito)
        browser = browser_helper.get_browser_for_step("m03_click_register")
        
        # Aktuelle Page holen
        pages = await browser.pages
        if not pages:
            page = await browser.get('https://auth.openai.com')
        else:
            page = pages[0]
        
        # Stealth Engine anwenden (MUSS nach jedem Page-Load!)
        await stealth.apply_stealth(page)
        
        # Nach Register-Button suchen (verschiedene Selector probieren)
        selectors = [
            'a[href*="signup"]',
            'a[href*="register"]',
            'button:contains("Sign up")',
            'button:contains("Register")',
            '[data-testid="signup-button"]',
        ]
        
        element = None
        for selector in selectors:
            try:
                element = await page.select(selector)
                if element:
                    break
            except:
                continue
        
        if not element:
            # Fallback: Text-Suche
            element = await page.find("Sign up", best_match=True)
        
        if not element:
            element = await page.find("Register", best_match=True)
        
        if not element:
            print("[M03] ❌ Register Button nicht gefunden!")
            await page.screenshot("m03_no_button.png")
            return False
        
        # Element ins Viewport scrollen
        await element.scroll_into_view()
        await asyncio.sleep(random.uniform(0.3, 0.6))
        
        # Position berechnen mit Random-Offset (nicht immer gleiche Stelle!)
        box = await element.get_position()
        if not box:
            print("[M03] ❌ Konnte Button-Position nicht bestimmen!")
            return False
        
        # Zufällige Position innerhalb des Elements (wie echte User!)
        x = int(box[0] + random.randint(20, box[3] - 20))
        y = int(box[1] + random.randint(10, box[4] - 10))
        
        # STEALTH CLICK ausführen (Bezier-Kurve + Pressure!)
        print(f"[M03] 🖱️  Performing stealth click at ({x}, {y})...")
        success = await stealth.human_click(page, x, y, clicks=1)
        
        if success:
            print("[M03] ✅ Register Button geklickt!")
            
            # Warten bis Seite lädt (random für menschliches Timing)
            await asyncio.sleep(random.uniform(2.0, 4.0))
            
            # Erneut Stealth anwenden nach Navigation
            await stealth.apply_stealth(page)
            
            return True
        else:
            print("[M03] ❌ Stealth Click fehlgeschlagen!")
            await page.screenshot("m03_click_failed.png")
            return False
            
    except Exception as e:
        print(f"[M03] 💥 KRITISCHER FEHLER: {e}")
        raise

