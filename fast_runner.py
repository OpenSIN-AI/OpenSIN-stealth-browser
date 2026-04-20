#!/usr/bin/env python3
"""
OPEN SIN STEALTH BROWSER - Fast Runner v0.5.0 (Geheimprojekt: openai-temp-rotator)

WAS: Vollautomatischer Account-Rotator für OpenAI Tokens.
WARUM: Umgeht Rate-Limits durch automatische Neuerstellung von Accounts.
WIE: Temp-Mail.org → OpenAI Signup → OAuth → Token Pool Push.

ACHTUNG FÜR ENTWICKLER:
- Dies ist ein GEHEIMPROJEKT! Keine Erwähnung in anderen Repos!
- 0% User Interaction! Alles läuft vollautomatisch.
- Dual-Browser: Port 9334 (Temp-Mail Default), Port 9335 (OpenAI Incognito).
- Singleton-Patch verhindert Browser-Zombies nach WebSocket-Crash.

VERWENDUNG:
    export STEALTH_RUNS=30      # Anzahl Runs
    export STEALTH_COOLDOWN=120 # Sekunden zwischen Runs
    python3 fast_runner.py
"""

import asyncio
import functools
import importlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

import nodriver as uc

# ── SINGLETON PATCH ──────────────────────────────────────────────────────────
# WARUM: Verhindert dass jeder Micro-Step einen neuen Browser startet.
# Ohne Patch: 50 Steps = 50 Browser = Chaos + Port-Blockaden.
# Mit Patch: Alle Steps nutzen denselben Browser auf Port 9334.
_orig_start = uc.start
_browser_singleton = None


@functools.wraps(_orig_start)
async def _patched_start(*args, **kwargs):
    """
    Singleton-Wrapper für uc.start().
    
    WARUM: Nach WebSocket-Crash bleibt Chrome am Leben (macOS Hintergrundprozess).
    Dieser Patch stellt sicher dass alle Steps denselben Browser nutzen.
    """
    global _browser_singleton
    
    if _browser_singleton is not None:
        # Browser existiert bereits, wiederverwenden
        return _browser_singleton

    # Default-Parameter für CDP-Verbindung
    kwargs["host"] = "127.0.0.1"
    kwargs["port"] = 9334  # Temp-Mail Browser (Default Profile)

    # Starte neuen Browser (oder verbinde mit existierendem)
    _browser_singleton = await _orig_start(*args, **kwargs)
    
    # WICHTIG: Verhindert dass nodriver den Browser killt beim Schließen
    # WARUM: macOS hält Chrome im Hintergrund, würde Port blockieren
    _browser_singleton._browser_process = None
    _browser_singleton._process_pid = None
    
    return _browser_singleton


# Patch anwenden - ALLE zukünftigen uc.start() Aufrufe nutzen Singleton
uc.start = _patched_start


def _reset_browser_singleton():
    """Setzt Singleton zurück für nächsten Run."""
    global _browser_singleton
    _browser_singleton = None


def _chrome_alive(port=9334):
    """Prüft ob Chrome auf gegebenem Port erreichbar ist."""
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return True
    except Exception:
        return False


def _ensure_chrome():
    """
    Startet Chrome falls nicht bereits laufend.
    
    WARUM: Pipeline benötigt laufenden Browser auf Port 9334.
    Nutzt connect_micro.py für korrekte CDP-Initialisierung.
    """
    if _chrome_alive():
        print("Chrome already alive on port 9334, reusing...")
        return
    
    print("Starte Chrome via connect_micro.py...")
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "connect_micro.py")],
        capture_output=True,
        text=True,
    )
    
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    
    if result.returncode != 0 or not _chrome_alive():
        raise RuntimeError("Chrome did not come up on port 9334")


# ── PIPELINE PHASEN ──────────────────────────────────────────────────────────
# WARUM: Aufteilung in logische Phasen für bessere Fehlerbehandlung.
# Jede Phase kann separat getestet werden.

PHASE1_TEMPMAIL = [
    # Phase 1: Temp-Mail vorbereiten (alte E-Mails löschen, neue generieren)
    "m05_goto_tempmail",           # Navigiere zu temp-mail.org
    "m07_click_tempmail_delete",   # Lösche alte E-Mail
    "m08_check_delete_confirm",    # Prüfe Bestätigung
    "m09_click_delete_yes",        # Bestätige Löschen
    "m10_click_generate_new",      # Generiere neue E-Mail
    "m11_wait_and_get_email",      # Warte + extrahiere E-Mail
]

PHASE2_STEALTH_REG = [
    # Phase 2: OpenAI Registrierung (Stealth Mode)
    "s5_stealth_navigation",       # Google → OpenAI (stealth)
    "s11_enter_email",             # E-Mail eingeben (stealth type)
    "s12_enter_password",          # Passwort eingeben (stealth)
    "s13_get_and_type_otp",        # OTP holen + eingeben
    "s13b_onboarding",             # Onboarding starten
    "s13c_skip_onboarding",        # Onboarding überspringen
]

PHASE2B_ONBOARDING = [
    # Phase 2b: Optionales Onboarding (falls nötig)
    # Leer = wird automatisch übersprungen
]

PHASE3_OAUTH = [
    # Phase 3: OAuth Login (Incognito Browser auf Port 9335)
    "s14_start_auth_login",        # Starte Auth-Flow
    "s15_open_oauth_in_incognito", # Öffne OAuth in Incognito
    "s16_enter_email_relogin",     # E-Mail erneut eingeben
    "s17_click_einmalcode",        # Einmal-Code anfordern
    "s18_get_2nd_otp",             # Zweites OTP holen
    "s19_type_2nd_otp",            # Zweites OTP eingeben
    "s20_click_authorize",         # Autorisieren
    "s21_wait_callback",           # Warte Callback URL
]

# Pfade für Micro-Steps hinzufügen
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "micro_steps"))


async def take_error_screenshots(step_name):
    """
    Macht Screenshots bei Fehlern für Debugging.
    
    WARUM: Bei OpenAI-Detection müssen wir UI-Zustand analysieren.
    Speichert unter /tmp/fail_{step}_tab_{n}.png
    """
    try:
        b = await uc.start()
        for i, t in enumerate(b.tabs):
            path = f"/tmp/fail_{step_name}_tab_{i}.png"
            try:
                await t.bring_to_front()
                await asyncio.sleep(0.5)
                await t.save_screenshot(path)
                url = getattr(t, "url", getattr(t.target, "url", ""))
                print(f"screenshot {path} {url}")
            except Exception:
                pass
    except Exception as e:
        print(f"screenshot-error {e}")


def _cleanup_state_files():
    """
    Bereinigt temporäre State-Files vor jedem Run.
    
    WARUM: Alte OTPs/Passwörter würden nächste Runs korrumpieren.
    Jeder Run muss frischen State haben.
    """
    state_files = [
        "/tmp/current_password.txt",
        "/tmp/current_otp.txt",
        "/tmp/current_otp2.txt",
        "/tmp/opencode_auth.log",
        "/tmp/oauth_url.txt",
        "/tmp/s_skip_login.txt",
        "/tmp/s_otp_needed.txt",
        "/tmp/m30_skip_login.txt",
        "/tmp/m30_otp_needed.txt",
        "/tmp/m30_login_mode.txt",
        "/tmp/incognito_ctx_id.txt",
        "/tmp/incognito_tab_id.txt",
    ]
    
    for path in state_files:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass  # File existiert nicht = ok


def _run_log_dir():
    """Return the canonical directory used for per-run JSON summaries."""
    return os.path.join(os.path.dirname(__file__), "logs", "runs")


def _write_run_summary(summary):
    """
    Persist one JSON artifact per pipeline run so operators can inspect the full
    step timeline after the fact without scraping console output.
    """
    os.makedirs(_run_log_dir(), exist_ok=True)
    summary_path = os.path.join(
        _run_log_dir(), f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    )
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    print(f"run-summary-written {summary_path}")
    return summary_path


async def _ensure_browser_target_exists():
    """Stellt sicher dass mindestens ein Tab existiert."""
    b = await uc.start()
    if getattr(b, "tabs", None):
        return
    await b.connection.send(uc.cdp.target.create_target("about:blank"))
    await asyncio.sleep(1)


async def _run_steps(steps, optional=False):
    """
    Execute the configured step modules sequentially while emitting a structured
    JSON log line for every step and collecting those records for the per-run
    summary written by run_all().
    
    WARUM: Sequenzielle Ausführung mit Timing für Performance-Analyse.
    """
    step_results = []
    
    for module_name in steps:
        print(f"-> EXECUTING: {module_name}")

        # Start timing immediately before importing/executing the step
        t0 = time.time()
        try:
            mod = importlib.import_module(module_name)
            mod = importlib.reload(mod)
            success = await mod.run()
        except Exception as e:
            success = False
            print(f"exception in {module_name}: {e}")

        elapsed = time.time() - t0
        step_result = {
            "step": module_name,
            "status": "OK" if success else "FAIL",
            "elapsed_s": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
        }
        print(json.dumps(step_result))
        step_results.append(step_result)

        if success:
            await asyncio.sleep(0.05)  # Kurze Pause zwischen Steps
            continue
        
        if optional:
            print(f"optional-step-failed {module_name}")
            continue
        
        print(f"hard-step-failed {module_name}")
        await take_error_screenshots(module_name)
        return False, step_results
    
    return True, step_results


async def run_single():
    """
    Run one full stealth rotation and return a structured result object.
    
    RÜCKGABE: {"success": bool, "steps": [...]}
    """
    run_result = {"success": False, "steps": []}

    await _ensure_browser_target_exists()

    # Phase 1: Temp-Mail vorbereiten
    phase_success, phase_steps = await _run_steps(PHASE1_TEMPMAIL)
    run_result["steps"].extend(phase_steps)
    if not phase_success:
        return run_result

    # Phase 2: OpenAI Stealth Registration
    phase_success, phase_steps = await _run_steps(PHASE2_STEALTH_REG)
    run_result["steps"].extend(phase_steps)
    if not phase_success:
        return run_result

    # Phase 2b: Optional Onboarding
    phase_success, phase_steps = await _run_steps(PHASE2B_ONBOARDING, optional=True)
    run_result["steps"].extend(phase_steps)
    if not phase_success:
        return run_result

    # Phase 3: OAuth Login
    phase_success, phase_steps = await _run_steps(PHASE3_OAUTH)
    run_result["steps"].extend(phase_steps)
    if not phase_success:
        return run_result

    run_result["success"] = True
    return run_result


async def run_all():
    """
    Hauptfunktion: Führt mehrere Runs mit Cooldown durch.
    
    ENV: STEALTH_RUNS (default: 1), STEALTH_COOLDOWN (default: 120s)
    """
    max_runs = int(os.environ.get("STEALTH_RUNS", "1"))
    cooldown = int(os.environ.get("STEALTH_COOLDOWN", "120"))
    
    print(f"=== OPENAI STEALTH ROTATOR ({max_runs} RUNS) ===")
    print(f"Cooldown zwischen Runs: {cooldown}s")
    
    os.system("rm -f /tmp/fail_*.png")
    _ensure_chrome()
    
    for run_idx in range(1, max_runs + 1):
        print(f"\n{'='*50}")
        print(f"RUN {run_idx}/{max_runs}")
        print(f"{'='*50}")
        
        _reset_browser_singleton()
        _cleanup_state_files()

        run_started_at = datetime.now().isoformat()
        run_result = await run_single()
        
        run_summary = {
            "run_index": run_idx,
            "max_runs": max_runs,
            "started_at": run_started_at,
            "finished_at": datetime.now().isoformat(),
            "success": run_result["success"],
            "steps": run_result["steps"],
        }

        if run_result["success"]:
            print("\n✅ RUN SUCCESSFUL")
            
            # Token in Pool pushen
            try:
                from push_to_pool import run_push
                run_push()
                run_summary["push_to_pool"] = {"status": "OK"}
                print("✅ Token pushed to pool")
            except Exception as e:
                print(f"⚠️ push-warning {e}")
                run_summary["push_to_pool"] = {"status": "WARN", "message": str(e)}
        else:
            print("\n❌ RUN FAILED")
            run_summary["push_to_pool"] = {"status": "SKIPPED"}
            _write_run_summary(run_summary)
            return False

        _write_run_summary(run_summary)
        
        if run_idx < max_runs:
            print(f"\n⏳ Cooldown: {cooldown}s bis nächster Run...")
            await asyncio.sleep(cooldown)
    
    return True


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(run_all()) else 1)
