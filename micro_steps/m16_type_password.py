"""
================================================================================
MICRO-STEP M16: Password eingeben mit STEALTH TYPE ENGINE
================================================================================

WAS DIESER STEP MACHT:
----------------------
Gibt das Passwort im OpenAI Registrierungsformular ein.

WARUM STEALTH HIER WICHTIG IST:
-------------------------------
OpenAI analysiert TIPPGESCHWINDIGKEIT und TIMING!
- Roboter tippen immer gleich schnell (50ms pro Key)
- Echte Typisten haben VARIIERENDES Timing (30-120ms)
- Pausen zwischen Wörtern (> 150ms)
- Gelegentliche Tippfehler mit Korrektur

DIESER STEP VERWENDET:
----------------------
- Human Type Engine mit random Keystroke-Delays
- Word-basierte Pausen (nach Leerzeichen)
- Stealth Focus Click vor dem Tippen

VERWENDUNG:
-----------
from browser_helper import BrowserHelper

async def execute(browser_helper: BrowserHelper):
    success = await execute(browser_helper)
    return success

AUTHOR: OpenSIN AI Team
VERSION: 0.4.0
================================================================================
"""

import asyncio
import random
import os
from stealth_engine import stealth


async def execute(browser_helper, password: str = None):
    """
    Hauptfunktion des Micro-Steps.
    
    PARAMS:
    -------
    browser_helper : BrowserHelper
        Instanz des BrowserHelpers für Dual-Browser Management
    password : str, optional
        Das Passwort das eingegeben werden soll.
        Wenn None, wird aus Umgebungsvariable gelesen.
        
    RETURNS:
    --------
    bool: True wenn erfolgreich, False sonst
    
    RAISES:
    -------
    Exception: Wenn kritischer Fehler auftritt
    """
    print("\n[M16] Entering password...")
    
    try:
        # Passwort holen (aus Parameter oder Env-Variable)
        if not password:
            password = os.getenv('OPENAI_PASSWORD', 'TempPass123!')
            print(f"[M16] ⚠️  Verwende Default-Passwort (Env-Variable nicht gesetzt)")
        else:
            print(f"[M16] 🔐 Passwort übergeben ({len(password)} Zeichen)")
        
        # RICHTIGEN Browser holen (OpenAI Incognito)
        browser = browser_helper.get_browser_for_step("m16_type_password")
        
        # Aktuelle Page holen
        pages = await browser.pages
        if not pages:
            print("[M16] ❌ Keine Page verfügbar!")
            return False
        
        page = pages[0]
        
        # Stealth Engine anwenden (MUSS nach jedem Page-Load!)
        await stealth.apply_stealth(page)
        
        # Nach Passwort-Feld suchen (verschiedene Selector)
        selectors = [
            'input[type="password"]',
            'input[name="password"]',
            '#password',
            '[data-testid="password-input"]',
        ]
        
        element = None
        for selector in selectors:
            try:
                element = await page.select(selector)
                if element:
                    print(f"[M16] 🎯 Passwort-Feld gefunden: {selector}")
                    break
            except:
                continue
        
        if not element:
            print("[M16] ❌ Passwort-Feld nicht gefunden!")
            await page.screenshot("m16_no_password_field.png")
            return False
        
        # Element ins Viewport scrollen
        await element.scroll_into_view()
        await asyncio.sleep(random.uniform(0.3, 0.6))
        
        # STEALTH TYPE ausführen (menschliches Timing!)
        print(f"[M16] ⌨️  Typing password with human timing...")
        
        # Zuerst menschlicher Klick aufs Feld (Focus)
        box = await element.get_position()
        if box:
            x = int(box[0] + 20)
            y = int(box[1] + 10)
            await stealth.human_click(page, x, y)
            await asyncio.sleep(random.uniform(0.2, 0.4))
        
        # Passwort zeichenweise tippen mit menschlichem Timing
        # ACHTUNG: Nicht das ganze Passwort auf einmal!
        words = password.split(' ') if ' ' in password else [password]
        
        for word_idx, word in enumerate(words):
            for char in word:
                # Haupt-Tipp-Delay (30-120ms wie echte Typisten)
                delay = random.uniform(0.04, 0.15)
                await asyncio.sleep(delay)
                
                # Zeichen senden
                await page.send_keys(char)
            
            # Pause nach "Wörtern" (länger als zwischen Buchstaben)
            if word_idx < len(words) - 1:
                pause = random.uniform(0.2, 0.5)
                await asyncio.sleep(pause)
                await page.send_keys(' ')
        
        print("[M16] ✅ Passwort eingegeben!")
        
        # Kurze Pause nach der Eingabe (menschliches Verhalten)
        await asyncio.sleep(random.uniform(0.5, 1.0))
        
        # Screenshot zum Debuggen (optional, nur bei Fehlern)
        # await page.screenshot("m16_password_entered.png")
        
        return True
        
    except Exception as e:
        print(f"[M16] 💥 KRITISCHER FEHLER: {e}")
        raise

