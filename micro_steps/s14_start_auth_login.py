#!/usr/bin/env python3
"""
s14_start_auth_login.py — Fire-and-forget: opencode auth login im Hintergrund.

Basiert auf dem bewährten m27-Pattern:
1. Port 1455 freiräumen (falls alter Listener noch läuft)
2. Alte Auth-Logs & State-Files löschen
3. opencode auth login als Hintergrundprozess starten
4. OAuth URL erscheint in /tmp/opencode_auth.log (für s15)

WICHTIG: Dieser Schritt blockiert NICHT. Die Pipeline geht sofort weiter.
Der opencode auth login Prozess wartet im Hintergrund auf den Callback
auf localhost:1455, der erst in s21 ausgelöst wird.
"""

import asyncio
import sys
import subprocess
import os


def run_sync():
    """Synchrone Version: Startet opencode auth login fire-and-forget."""

    # ── Schritt 1: Port 1455 freiräumen ──────────────────────────────────────
    # Falls ein alter opencode auth login Prozess noch auf Port 1455 lauscht,
    # muss er zuerst gekillt werden. Sonst bekommt der neue Prozess einen
    # "address already in use" Fehler.
    print("S14: Raeume Port 1455 leer...")
    os.system("lsof -ti tcp:1455|xargs kill -9 2>/dev/null")

    # ── Schritt 2: Alte State-Files aufräumen ────────────────────────────────
    # Alle temporären Files aus dem vorherigen Run löschen, damit keine
    # stale States in die neue Pipeline leaken. Besonders wichtig:
    # - opencode_auth.log: Enthält die OAuth URL für s15
    # - oauth_url.txt: Alternative URL-Quelle
    # - s_skip_login.txt: Skip-Flag für s16-s19 (falls Direktlogin klappt)
    # - s_otp_needed.txt: Flag ob 2. OTP nötig ist
    # - current_otp2.txt: Der 2. OTP Code
    print("S14: Cleaning up old auth artifacts...")
    cleanup_files = [
        "/tmp/opencode_auth.log",
        "/tmp/oauth_url.txt",
        "/tmp/s_skip_login.txt",
        "/tmp/s_otp_needed.txt",
        "/tmp/current_otp2.txt",
    ]
    for f in cleanup_files:
        try:
            os.remove(f)
        except FileNotFoundError:
            pass

    # ── Schritt 3: opencode auth login im Hintergrund starten ────────────────
    # --provider openai: Wir wollen einen OpenAI Token
    # --method "ChatGPT Pro/Plus (browser)": Browser-basierter OAuth Flow
    # > /tmp/opencode_auth.log 2>&1: Gesamte Ausgabe ins Log (für URL-Extraktion)
    # start_new_session=True: Prozess überlebt auch wenn Python beendet wird
    subprocess.Popen(
        'opencode auth login --provider openai --method "ChatGPT Pro/Plus (browser)" > /tmp/opencode_auth.log 2>&1',
        shell=True,
        start_new_session=True,
    )
    print(
        "S14 OK: opencode auth login laeuft im Hintergrund. Pipeline geht sofort weiter!"
    )
    return True


async def run():
    """Async Wrapper für den Runner."""
    return run_sync()


if __name__ == "__main__":
    sys.exit(0 if run_sync() else 1)
