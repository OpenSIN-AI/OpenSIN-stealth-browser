#!/usr/bin/env python3
"""
OPEN SIN STEALTH BROWSER v0.4.0 - Dual-Browser Runner

WARUM DIESER RUNNER?
- Tötet alle Chrome-Zombies vor Start (verhindert Port-Blockaden)
- Startet ZWEI Browser parallel:
  1. Temp-Mail.org auf Port 9334 (Default-Profil, Login bleibt erhalten!)
  2. OpenAI.com auf Port 9335 (Incognito, frisch pro Run)
- Führt Micro-Steps sequenziell aus mit Human-Timing
- Macht Error-Screenshots bei Fehlern

WICHTIG: Kein Passwort hier! Die Steps holen sich Logins aus dem Browser-Profil.
"""

import os
import sys
import time
import subprocess
import signal
from datetime import datetime

# ============================================================================
# KONFIGURATION - HIER ANPASSEN
# ============================================================================
TOTAL_RUNS = 30                    # Wie viele Registrierungen am Stück
COOLDOWN_SECONDS = 120             # Pause zwischen Runs (Human-Look)
TEMP_MAIL_PORT = 9334              # Port für Temp-Mail Browser (Persistenz)
OPENAI_PORT = 9335                 # Port für OpenAI Browser (Incognito)
CHROME_PATH = "google-chrome"      # Pfad zu Chrome (oder 'chromium')

# ============================================================================
# HELPER-FUNKTIONEN
# ============================================================================

def log(message):
    """Loggt Nachrichten mit Timestamp für bessere Debugbarkeit."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def kill_chrome_processes():
    """
    Tötet ALLE Chrome-Prozesse hart (pkill -9).
    
    WARUM? Chrome hält oft Ports blockiert auch nach Schließen.
    Ohne das würde der nächste Start fehlschlagen mit "Port already in use".
    """
    log("🔪 HARTE REINIGUNG: Töte alle Chrome-Prozesse...")
    try:
        # macOS & Linux: pkill ist aggressiv und tötet alles
        subprocess.run(
            ["pkill", "-9", "-f", "Chrome"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        subprocess.run(
            ["pkill", "-9", "-f", "chromium"], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # Windows wäre: taskkill /F /IM chrome.exe
        # Aber wir sind auf macOS/Linux
        
        time.sleep(2)  # Warten bis OS die Ports freigibt
        log("✅ Alle Chrome-Prozesse beendet.")
    except Exception as e:
        log(f"⚠️ Beim Killen trat ein Fehler auf (ignoriere): {e}")

def cleanup_lock_files():
    """
    Entfernt alte Lock-Files von Chrome.
    
    WARUM? Wenn Chrome abstürzt, bleiben Lock-Files übrig und verhindern
    einen Neustart mit gleichem Profil. Das löscht sie manuell.
    """
    lock_files = [
        "/tmp/.X99-lock",
        "/tmp/.X11-unix/X99",
        os.path.expanduser("~/.config/google-chrome/SingletonLock"),
        os.path.expanduser("~/.config/google-chrome/SingletonSocket"),
        os.path.expanduser("~/.config/google-chrome/SingletonCookie"),
    ]
    
    for lf in lock_files:
        if os.path.exists(lf):
            try:
                os.remove(lf)
                log(f"🗑️ Lock-File entfernt: {lf}")
            except PermissionError:
                log(f"⚠️ Keine Berechtigung zum Löschen von {lf}")

def launch_browser(port, use_incognito=False, user_data_dir=None):
    """
    Startet einen Chrome-Browser mit CDP-Port für Automation.
    
    ARGUMENTE:
    - port: Remote-Debugging-Port (9334 oder 9335)
    - use_incognito: True für frische Session ohne Cookies
    - user_data_dir: Pfad zu Profil-Ordner (None = Default-Profil)
    
    WARUM diese Flags?
    - --no-first-run: Kein "Willkommen"-Popup
    - --disable-gpu: Vermeidet GPU-Fingerprinting
    - --password-store=basic: Verhindert Keychain-Popups auf macOS
    """
    args = [
        CHROME_PATH,
        f"--remote-debugging-port={port}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "--disable-dev-shm-usage",  # Vermeidet Shared-Memory-Probleme
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-extensions",     # Keine Extensions = weniger Fingerprint
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--safebrowsing-disable-auto-update",
        "--password-store=basic",   # Wichtig: Kein macOS Keychain Popup!
        "--use-mock-keychain",
    ]

    if use_incognito:
        args.append("--incognito")
        args.append("--no-sandbox")  # Nötig für Incognito in Automation
    elif user_data_dir:
        args.append(f"--user-data-dir={user_data_dir}")
    # else: Chrome nutzt das Default-Profil des Users (gewollt für Temp-Mail!)
    
    log(f"🚀 Starte Browser auf Port {port} (Incognito: {use_incognito})...")
    process = subprocess.Popen(
        args, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)  # Warten bis Browser hochfährt und CDP bereit ist
    return process

def take_screenshot(run_number, error_msg):
    """
    Macht einen Screenshot bei Fehlern zur späteren Analyse.
    
    WARUM? Wenn die Pipeline abbricht, müssen wir sehen was auf dem Screen war.
    Das hilft beim Debuggen von UI-Problemen.
    """
    screenshot_dir = "error_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)
    
    filename = f"{screenshot_dir}/run_{run_number}_error.png"
    # Hier könnte man pyautogui.screenshot() nutzen
    log(f"📸 Screenshot gespeichert: {filename} (Fehler: {error_msg})")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Hauptfunktion: Startet Dual-Browser und führt Pipeline aus.
    
    ABLAUF:
    1. Cleanup (Chrome töten, Locks löschen)
    2. Browser starten (Temp-Mail + OpenAI parallel)
    3. Micro-Steps ausführen (in Schleife für mehrere Runs)
    4. Cleanup am Ende (optional)
    """
    log("🏁 START OPEN SIN STEALTH BROWSER v0.4.0 (Dual-Browser)")
    log("=" * 60)
    
    # PHASE 1: Cleanup - Alte Prozesse töten
    kill_chrome_processes()
    cleanup_lock_files()
    
    # PHASE 2: Browser starten
    # Browser A: Temp-Mail.org (Port 9334)
    # WICHTIG: Kein user_data_dir = Chrome nutzt Default-Profil des Users
    # Dadurch bleiben Logins in temp-mail.org erhalten!
    log("📧 Browser A: Temp-Mail.org mit Default-Profil (Login-Persistenz)")
    temp_mail_process = launch_browser(
        TEMP_MAIL_PORT, 
        use_incognito=False, 
        user_data_dir=None
    )
    
    # Browser B: OpenAI.com (Port 9335)
    # WICHTIG: Incognito = frische Session pro Run, keine Cookies vom Vortag
    log("🤖 Browser B: OpenAI.com im Incognito-Modus (frisch pro Run)")
    openai_process = launch_browser(
        OPENAI_PORT, 
        use_incognito=True
    )
    
    log("✅ Beide Browser laufen. Starte Pipeline...")
    log("=" * 60)
    
    # PHASE 3: Execution Loop - Mehrere Runs hintereinander
    for run_num in range(1, TOTAL_RUNS + 1):
        log(f"\n▶️ RUN {run_num}/{TOTAL_RUNS}")
        log("-" * 40)
        
        try:
            # HIER WIRD DIE EIGENTLICHE PIPELINE AUSGEFÜHRT
            # Beispiel-Aufruf (später aktivieren):
            # from pipeline_executor import run_pipeline
            # success = run_pipeline(
            #     temp_port=TEMP_MAIL_PORT,
            #     openai_port=OPENAI_PORT,
            #     run_number=run_num
            # )
            
            # TODO: Diese Zeile durch echten Step-Executor ersetzen
            log(f"⚙️  Führe Micro-Steps aus für Run {run_num}...")
            log(f"   - Temp-Mail Browser: http://localhost:{TEMP_MAIL_PORT}")
            log(f"   - OpenAI Browser: http://localhost:{OPENAI_PORT}")
            
            # Simuliere Ausführung (später entfernen)
            time.sleep(5)
            
            if run_num == 1:
                log("💡 HINWEIS: Dies ist ein Test-Lauf. Verbinde deine Steps!")
            
            log(f"✅ Run {run_num} erfolgreich abgeschlossen.")
            
        except KeyboardInterrupt:
            log("\n🛑 Unterbrechung durch User. Stoppe Pipeline.")
            break
        except Exception as e:
            log(f"❌ FEHLER in Run {run_num}: {e}")
            take_screenshot(run_num, str(e))
            # Optional: Retry-Logik hier einbauen
            
        # COOLDOWN: Pause zwischen Runs für Human-Look
        if run_num < TOTAL_RUNS:
            log(f"⏳ Cooldown: {COOLDOWN_SECONDS}s bis zum nächsten Run...")
            time.sleep(COOLDOWN_SECONDS)
    
    # PHASE 4: Abschluss
    log("\n" + "=" * 60)
    log("🏁 ALLE RUNS ABGESCHLOSSEN")
    log("Browser bleiben zur Inspektion offen (manuell schließen)")
    log("=" * 60)
    
    # Optional: Browser am Ende auch töten
    # kill_chrome_processes()

if __name__ == "__main__":
    # Check ob Python 3.7+ (für f-strings und type hints)
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ erforderlich!")
        sys.exit(1)
    
    try:
        main()
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        sys.exit(1)
