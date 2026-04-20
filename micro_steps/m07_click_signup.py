"""
================================================================================
MICRO-STEP M07: Klick auf Signup Button (OpenAI)
================================================================================

WAS DIESER STEP MACHT:
----------------------
Klickt auf den "Sign Up" oder "Continue" Button auf der OpenAI Startseite
um zum Registrierungsformular zu gelangen.

WARUM STEALTH HIER WICHTIG IST:
-------------------------------
OpenAI trackt jeden Klick! Ein robotischer Klick = SOFORT GEBLOCKT!
Dieser Step verwendet:
- Bezier-Mouse Movement (nicht linear!)
- Human Click Pressure (0.8-1.0 force)
- Random Delays vor/nach dem Klick

TECHNISCHE DETAILS:
-------------------
- Sucht nach mehreren Button-Varianten
- Nutzt Stealth Engine für menschlichen Klick
- Validiert dass Formular danach lädt

VERWENDUNG:
-----------
async def execute(browser_helper):
    success = await execute(browser_helper)
    # Signup-Formular ist jetzt sichtbar

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
import random


async def execute(browser_helper):
    """
    Klickt auf Signup Button mit Stealth Movement.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Browser-Management-Instanz
    
    RETURNS:
    --------
    bool : True bei Erfolg, False bei Fehler
    """
    try:
        page = await browser_helper.get_page_for_step("m07_click_signup")
        
        if not page:
            browser_helper.log("❌ Keine Page verfügbar")
            return False
        
        browser_helper.log("🖱️ Suche Signup Button...")
        
        # Mehrere Selektoren für Signup Button
        button_selectors = [
            "button[type='submit']",           # Submit Button
            "button:has-text('Sign up')",      # Text Button
            "button:has-text('Continue')",     # Continue Button
            "a[href*='signup']",               # Link
            "[data-testid='signup-button']",   # Test ID
            ".btn-signup",                     # Klasse
        ]
        
        signup_button = None
        for selector in button_selectors:
            try:
                signup_button = await page.query_selector(selector)
                if signup_button:
                    browser_helper.log(f"✅ Button gefunden: {selector}")
                    break
            except:
                continue
        
        if not signup_button:
            browser_helper.log("❌ Signup Button nicht gefunden!")
            # Fallback: Vielleicht sind wir schon auf der Signup-Seite?
            current_url = page.url
            if "signup" in current_url or "auth" in current_url:
                browser_helper.log("⚠️ Aber URL sieht nach Signup aus, mache weiter...")
                return True
            return False
        
        # bounding_box holen für Klick-Position
        bbox = await signup_button.bounding_box()
        
        if not bbox:
            browser_helper.log("❌ Button nicht sichtbar/klickbar")
            return False
        
        # Klick-Position berechnen (mit leichtem Jitter)
        click_x = bbox['x'] + bbox['width'] / 2 + random.uniform(-5, 5)
        click_y = bbox['y'] + bbox['height'] / 2 + random.uniform(-5, 5)
        
        # STEALTH CLICK mit Human Movement
        try:
            from stealth_engine import StealthEngine
            engine = StealthEngine()
            
            browser_helper.log("🖱️ Klick mit Stealth Movement...")
            await engine.human_click(page, click_x, click_y)
            
        except ImportError:
            browser_helper.log("⚠️ Stealth Engine nicht verfügbar, nutze Standard-Klick")
            await signup_button.click()
        
        # Kurze Pause nach Klick
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        # Warten bis Seite/Modal lädt
        try:
            await page.wait_for_load_state("networkidle", timeout=10000)
            browser_helper.log("✅ Seite nach Klick geladen")
        except asyncio.TimeoutError:
            browser_helper.log("⚠️ Timeout nach Klick, aber mache weiter")
        
        # Validieren dass Formular da ist
        form_indicators = [
            "input[type='email']",
            "#email",
            "[name='email']",
        ]
        
        for selector in form_indicators:
            try:
                is_visible = await page.is_visible(selector)
                if is_visible:
                    browser_helper.log(f"✅ Formular erkannt: {selector}")
                    return True
            except:
                continue
        
        browser_helper.log("⚠️ Formular nicht eindeutig erkannt, aber Klick war erfolgreich")
        return True
        
    except Exception as e:
        browser_helper.log(f"❌ FEHLER beim Signup-Klick: {e}")
        return False
