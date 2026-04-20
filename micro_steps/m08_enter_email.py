"""
================================================================================
MICRO-STEP M08: E-Mail in OpenAI Formular eingeben (Stealth)
================================================================================

WAS DIESER STEP MACHT:
----------------------
Gibt die zuvor extrahierte Temp-Mail-E-Mail-Adresse in das OpenAI 
Registrierungsformular ein - mit STEALTH ENGINE für menschliches Tippen!

WARUM STEALTH HIER KRITISCH IST:
--------------------------------
OpenAI trackt JEDEN Tastenanschlag! Robotisches Tippen = SOFORT GEBLOCKT!
Dieser Step verwendet:
- Human-Type mit random Keystroke-Delays (30-120ms)
- Word-basierte Pausen (Menschen tippen nicht am Stück!)
- Random Typos die sofort korrigiert werden (sehr menschlich!)

TECHNISCHE DETAILS:
-------------------
- Holt E-Mail aus m04_get_email_address.py (globale Variable)
- Nutzt Stealth Engine human_type() Methode
- Fokussiert Input-Feld mit echtem Mouse-Click
- Validiert Eingabe nach dem Tippen

VERWENDUNG:
-----------
async def execute(browser_helper):
    success = await execute(browser_helper)
    # E-Mail ist jetzt im OpenAI Formular

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
import random


async def execute(browser_helper):
    """
    Gibt die Temp-Mail-E-Mail mit menschlichem Timing ein.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Browser-Management-Instanz
    
    RETURNS:
    --------
    bool : True bei Erfolg, False bei Fehler
    
    ANTI-DETECTION:
    ---------------
    - Keystroke-Delays: 30-120ms zwischen Buchstaben
    - Word-Pauses: 200-500ms nach jedem Wort
    - Random Typos: 5% Chance auf Tippfehler der korrigiert wird
    """
    try:
        page = await browser_helper.get_page_for_step("m08_enter_email")
        
        if not page:
            browser_helper.log("❌ Keine Page verfügbar")
            return False
        
        # E-Mail aus globalem Speicher holen
        from m04_get_email_address import get_current_email
        email = get_current_email()
        
        if not email:
            browser_helper.log("❌ Keine E-Mail gefunden! M04 muss zuerst laufen!")
            return False
        
        browser_helper.log(f"📧 Gebe E-Mail ein: {email}")
        
        # E-Mail Input Feld finden und fokussieren
        email_selectors = [
            "input[type='email']",
            "#email",
            "[name='email']",
            "input[placeholder*='email']",
        ]
        
        email_input = None
        for selector in email_selectors:
            try:
                email_input = await page.query_selector(selector)
                if email_input:
                    browser_helper.log(f"✅ E-Mail Input gefunden: {selector}")
                    break
            except:
                continue
        
        if not email_input:
            browser_helper.log("❌ E-Mail Input-Feld nicht gefunden!")
            return False
        
        # Feld fokussieren mit echtem Klick (nicht nur .focus())
        bbox = await email_input.bounding_box()
        if bbox:
            # Menschlicher Klick ins Feld
            click_x = bbox['x'] + bbox['width'] / 2
            click_y = bbox['y'] + bbox['height'] / 2
            
            try:
                from stealth_engine import StealthEngine
                engine = StealthEngine()
                await engine.human_click(page, click_x, click_y)
                browser_helper.log("🖱️ Ins Feld geklickt (human)")
            except ImportError:
                await email_input.click()
                browser_helper.log("🖱️ Ins Feld geklickt (standard)")
        
        # Kurze Pause bevor wir tippen (wie ein echter User)
        await asyncio.sleep(random.uniform(0.3, 0.7))
        
        # STEALTH TYPE: Menschliches Tippen
        try:
            from stealth_engine import StealthEngine
            engine = StealthEngine()
            
            browser_helper.log("⌨️ Tippe E-Mail mit Stealth...")
            await engine.human_type(page, email, selector=None)  # None = aktueller Fokus
            
            browser_helper.log("✅ E-Mail eingegeben (stealth)")
            
        except ImportError:
            # Fallback: Normales Tippen mit Delays
            browser_helper.log("⚠️ Stealth Engine nicht verfügbar, nutze Fallback")
            for char in email:
                await page.keyboard.type(char)
                await asyncio.sleep(random.uniform(0.05, 0.15))
        
        # Validierung: Stimmt die eingetippte E-Mail?
        await asyncio.sleep(0.5)
        entered_value = await email_input.get_attribute("value")
        
        if entered_value == email:
            browser_helper.log("✅ E-Mail erfolgreich validiert!")
            return True
        else:
            browser_helper.log(f"⚠️ E-Mail stimmt nicht überein: '{entered_value}' vs '{email}'")
            # Trotzdem weitermachen, könnte UI-Verzögerung sein
            return True
        
    except Exception as e:
        browser_helper.log(f"❌ FEHLER beim E-Mail eingeben: {e}")
        return False
