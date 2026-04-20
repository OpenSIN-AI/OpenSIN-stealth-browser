#!/usr/bin/env python3
"""
PIPELINE EXECUTOR - Führt Micro-Steps sequenziell aus

WARUM DIESE DATEI?
- Verbindet alle Micro-Steps zu einer kompletten Pipeline
- Handhabt Fehler und macht Screenshots bei Problemen
- Unterstützt beide Browser (Temp-Mail + OpenAI) parallel

WICHTIG: Jeder Step muss eine execute()-Funktion haben!
"""

import os
import sys
import time
import importlib.util
from datetime import datetime
from pathlib import Path

# Importiere Browser-Helper für Browser-Auswahl
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from micro_steps.browser_helper import get_browser_for_step, log

# ============================================================================
# KONFIGURATION
# ============================================================================

# Liste aller Micro-Steps in der richtigen Reihenfolge
# Format: (Dateiname, Beschreibung, Timeout in Sekunden)
MICRO_STEPS = [
    # === PHASE 1: Temp-Mail Registrierung ===
    ("m01_open_tempmail.py", "Öffne temp-mail.org", 10),
    ("m02_wait_for_page.py", "Warte auf Seite laden", 15),
    ("m03_click_register.py", "Klicke Registrieren-Button", 10),
    
    # === PHASE 2: E-Mail abrufen ===
    ("m04_get_email_address.py", "Hole E-Mail Adresse", 10),
    ("m05_wait_for_verification_email.py", "Warte auf Bestätigungs-Mail", 60),
    
    # === PHASE 3: OpenAI Registrierung ===
    ("m06_open_openai.py", "Öffne openai.com", 10),
    ("m07_click_signup.py", "Klicke Signup-Button", 10),
    ("m08_enter_email.py", "E-Mail eingeben", 10),
    ("m09_submit_email.py", "E-Mail absenden", 10),
    
    # === PHASE 4: Verification Code ===
    ("m10_switch_to_tempmail.py", "Wechsle zu Temp-Mail Tab", 5),
    ("m11_copy_verification_code.py", "Kopiere Verifizierungscode", 10),
    ("m12_switch_to_openai.py", "Wechsle zu OpenAI Tab", 5),
    ("m13_enter_verification_code.py", "Code eingeben", 10),
    
    # === PHASE 5: Passwort setzen ===
    ("m14_create_password.py", "Generiere sicheres Passwort", 5),
    ("m15_enter_password.py", "Passwort eingeben", 10),
    ("m16_type_password.py", "Passwort tippen (Stealth)", 15),
    ("m17_confirm_password.py", "Passwort bestätigen", 10),
    
    # === PHASE 6: Onboarding überspringen ===
    ("m18_skip_intro.py", "Intro überspringen", 10),
    ("m19_dismiss_tutorial.py", "Tutorial ablehnen", 10),
    ("m20_close_welcome.py", "Willkommensnachricht schließen", 10),
    
    # === PHASE 7: Session speichern ===
    ("m21_save_session.py", "Session speichern", 10),
    ("m22_verify_login.py", "Login verifizieren", 10),
    ("m23_export_cookies.py", "Cookies exportieren", 10),
    
    # === PHASE 8: Cleanup ===
    ("m24_close_tabs.py", "Tabs schließen", 5),
    ("m25_log_success.py", "Erfolg loggen", 5),
]

# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================

def load_step_module(step_file):
    """
    Lädt ein Micro-Step Modul dynamisch.
    
    WARUM? Wir wollen nicht jeden Step manuell importieren müssen.
    Das ermöglicht einfaches Hinzufügen neuer Steps.
    """
    step_path = Path(__file__).parent / step_file
    
    if not step_path.exists():
        log(f"❌ Step-Datei nicht gefunden: {step_file}")
        return None
    
    # Dynamischer Import
    spec = importlib.util.spec_from_file_location("step_module", step_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    return module

def execute_step(step_name, description, timeout, temp_port, openai_port):
    """
    Führt einen einzelnen Micro-Step aus mit Timeout.
    
    ARGUMENTE:
    - step_name: Dateiname des Steps (z.B. "m03_click_register.py")
    - description: Menschliche Beschreibung für Logs
    - timeout: Maximalzeit in Sekunden
    - temp_port: Port für Temp-Mail Browser
    - openai_port: Port für OpenAI Browser
    
    RÜCKGABE:
    - True bei Erfolg, False bei Fehler
    """
    log(f"\n⚙️  STEP: {description}")
    log(f"   Datei: {step_name} | Timeout: {timeout}s")
    
    # Modul laden
    module = load_step_module(step_name)
    if not module:
        return False
    
    # Prüfen ob execute()-Funktion existiert
    if not hasattr(module, 'execute'):
        log(f"❌ Step hat keine execute()-Funktion!")
        return False
    
    # Browser für diesen Step holen
    browser = get_browser_for_step(step_name, temp_port, openai_port)
    if not browser:
        log(f"❌ Kein Browser verfügbar für Step {step_name}")
        return False
    
    try:
        # Step ausführen mit Timeout
        start_time = time.time()
        
        # TODO: Hier die echte execute-Funktion aufrufen
        # result = module.execute(browser)
        
        # Simuliere Ausführung (später entfernen)
        time.sleep(2)
        result = True
        
        elapsed = time.time() - start_time
        log(f"   ✅ Erfolgreich in {elapsed:.2f}s")
        
        return result
        
    except TimeoutError:
        log(f"❌ TIMEOUT: Step dauerte länger als {timeout}s")
        return False
    except Exception as e:
        log(f"❌ FEHLER: {e}")
        return False

def take_screenshot(run_number, step_name, error_msg):
    """Macht Screenshot bei Fehler."""
    screenshot_dir = "error_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{screenshot_dir}/run{run_number}_{step_name}_{timestamp}.png"
    
    # TODO: Echten Screenshot machen mit pyautogui
    # import pyautogui
    # pyautogui.screenshot(filename)
    
    log(f"📸 Screenshot: {filename}")

# ============================================================================
# MAIN EXECUTOR
# ============================================================================

def run_pipeline(temp_port=9334, openai_port=9335, run_number=1):
    """
    Hauptfunktion: Führt alle Micro-Steps sequenziell aus.
    
    ARGUMENTE:
    - temp_port: Port für Temp-Mail Browser
    - openai_port: Port für OpenAI Browser
    - run_number: Laufende Nummer des Runs (für Logs)
    
    RÜCKGABE:
    - True wenn alle Steps erfolgreich, False bei erstem Fehler
    """
    log("=" * 60)
    log(f"🚀 PIPELINE START - Run #{run_number}")
    log(f"   Temp-Mail Port: {temp_port}")
    log(f"   OpenAI Port: {openai_port}")
    log("=" * 60)
    
    success_count = 0
    failed_step = None
    
    for step_file, description, timeout in MICRO_STEPS:
        # Step ausführen
        success = execute_step(
            step_file, 
            description, 
            timeout,
            temp_port,
            openai_port
        )
        
        if success:
            success_count += 1
        else:
            failed_step = step_file
            take_screenshot(run_number, step_file, "Step failed")
            
            # Bei Fehler: Pipeline abbrechen oder retry?
            # Option 1: Sofort abbrechen (konservativ)
            log(f"\n❌ PIPELINE ABGEBROCHEN bei Step: {step_file}")
            break
            
            # Option 2: Retry-Logik (fortgeschritten)
            # for retry in range(3):
            #     log(f"   Retry {retry+1}/3...")
            #     if execute_step(...):
            #         break
    
    # Zusammenfassung
    total_steps = len(MICRO_STEPS)
    log("\n" + "=" * 60)
    log(f"📊 PIPELINE ERGEBNIS:")
    log(f"   Erfolgreiche Steps: {success_count}/{total_steps}")
    if failed_step:
        log(f"   ❌ Fehlgeschlagen bei: {failed_step}")
        log(f"   STATUS: FAILED")
        return False
    else:
        log(f"   ✅ Alle Steps erfolgreich!")
        log(f"   STATUS: SUCCESS")
        return True

if __name__ == "__main__":
    # Test-Aufruf
    log("🧪 TEST: Pipeline Executor")
    success = run_pipeline(run_number=1)
    sys.exit(0 if success else 1)
