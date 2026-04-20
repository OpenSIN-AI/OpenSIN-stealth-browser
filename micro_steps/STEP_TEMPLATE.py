#!/usr/bin/env python3
"""
MICRO-STEP TEMPLATE - Vorlage für neue Steps

WARUM DIESE DATEI?
- Einheitliche Struktur für alle Micro-Steps
- Entwickler können diese Datei kopieren und anpassen
- Verhindert Fehler durch inkonsistente Implementierung

ANLEITUNG FÜR NEUE STEPS:
1. Diese Datei kopieren als mXX_beschreibung.py
2. execute()-Funktion implementieren
3. Browser-Auswahl anpassen (temp_mail oder openai)
4. Stealth-Funktionen nutzen (click_stealth, type_stealth)
5. Ausgiebig testen!

WICHTIG: Jeder Step muss atomar sein!
- Ein Step = Eine klare Aufgabe
- Bei Fehler: Exception werfen, nicht schlucken
- Browser immer am Ende schließen (außer bei Tabs)
"""

import sys
import os
from typing import Optional, Dict, Any

# Parent-Verzeichnis zum Importieren von Helpers
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports von globalen Modulen
from stealth_engine import StealthEngine
from micro_steps.browser_helper import get_browser_for_step, log

# ============================================================================
# STEP-KONFIGURATION
# ============================================================================

# Welcher Browser wird für diesen Step benötigt?
# Optionen: "temp_mail" (9334) oder "openai" (9335)
TARGET_BROWSER = "temp_mail"  # ODER: "openai"

# Timeout in Sekunden - wie lange darf dieser Step maximal dauern?
STEP_TIMEOUT = 10

# Retry-Einstellungen - wie oft bei Fehler wiederholen?
MAX_RETRIES = 3
RETRY_DELAY = 2  # Sekunden zwischen Retries

# ============================================================================
# STEP-LOGIK
# ============================================================================

def execute(browser=None, **kwargs) -> bool:
    """
    Hauptfunktion dieses Micro-Steps.
    
    ARGUMENTE:
    - browser: Browser-Instanz (wird automatisch von Pipeline übergeben)
    - kwargs: Zusätzliche Parameter (z.B. email_address, password, etc.)
    
    RÜCKGABE:
    - True bei Erfolg
    - False bei Fehler (oder Exception werfen)
    
    BEISPIEL:
    ```python
    def execute(browser, email="test@example.com"):
        # 1. Navigation
        browser.get("https://temp-mail.org")
        
        # 2. Element finden
        register_button = browser.find_element(By.ID, "register-btn")
        
        # 3. Stealth Click ausführen
        from stealth_engine import click_stealth
        click_stealth(browser, register_button)
        
        # 4. Erfolg prüfen
        if "dashboard" in browser.current_url:
            return True
        return False
    ```
    """
    
    log(f"🔧 START: {os.path.basename(__file__)}")
    
    # Wenn kein Browser übergeben wurde, selbst holen
    if browser is None:
        browser = get_browser_for_step(
            os.path.basename(__file__),
            temp_port=9334,
            openai_port=9335
        )
    
    if not browser:
        log("❌ FEHLER: Kein Browser verfügbar!")
        return False
    
    try:
        # ================================================================
        # HIER DEINE STEP-LOGIK IMPLEMENTIEREN
        # ================================================================
        
        # Beispiel-Code (durch echten Code ersetzen):
        
        # 1. Navigation zur Zielseite
        # target_url = "https://temp-mail.org"
        # browser.get(target_url)
        
        # 2. Warten bis Seite geladen ist
        # WebDriverWait(browser, 10).until(
        #     EC.presence_of_element_located((By.ID, "some-element"))
        # )
        
        # 3. Element finden und interagieren
        # element = browser.find_element(By.CSS_SELECTOR, ".button")
        # click_stealth(browser, element)
        
        # 4. Ergebnis prüfen
        # success = "success" in browser.page_source
        
        log("⚠️  TODO: Implementiere deine Step-Logik hier!")
        success = True  # Placeholder
        
        # ================================================================
        # ENDE DEINER STEP-LOGIK
        # ================================================================
        
        if success:
            log(f"✅ SUCCESS: {os.path.basename(__file__)}")
            return True
        else:
            log(f"❌ FAILED: {os.path.basename(__file__)}")
            return False
            
    except Exception as e:
        log(f"❌ EXCEPTION: {e}")
        # Optional: Screenshot bei Fehler
        # take_screenshot(os.path.basename(__file__))
        raise  # Exception weiterwerfen für Pipeline-Handling

def validate_prerequisites(browser) -> bool:
    """
    Prüft ob alle Voraussetzungen für diesen Step erfüllt sind.
    
    WARUM? Manche Steps können nur ausgeführt werden wenn:
    - Bestimmte Seite geladen ist
    - Element sichtbar ist
    - Vorheriger Step erfolgreich war
    
    RÜCKGABE: True wenn bereit, False wenn nicht
    """
    # Beispiel-Implementierung:
    # return "temp-mail.org" in browser.current_url
    return True

def cleanup(browser):
    """
    Aufräumarbeiten nach dem Step.
    
    WARUM? Browser-Tabs schließen, Speicher freigeben, etc.
    Wird auch bei Fehlern aufgerufen (finally-Block).
    """
    # Beispiel: Tab schließen aber Browser offen lassen
    # if len(browser.tabs) > 1:
    #     browser.close()
    pass

# ============================================================================
# MAIN (für direktes Testen des Steps)
# ============================================================================

if __name__ == "__main__":
    # Direkter Test-Aufruf dieses Steps (ohne Pipeline)
    log("🧪 TEST MODE: Führe Step isoliert aus...")
    
    # Mock-Browser erstellen (oder echten Browser starten)
    # from selenium import webdriver
    # browser = webdriver.Chrome()
    
    try:
        result = execute()
        log(f"TEST ERGEBNIS: {'✅ SUCCESS' if result else '❌ FAILED'}")
    except Exception as e:
        log(f"TEST FEHLER: {e}")
    finally:
        # Browser schließen falls geöffnet
        # browser.quit()
        pass
