#!/usr/bin/env python3
"""
s21_wait_callback.py — Warte auf den OAuth Callback (localhost:1455).

Basiert auf dem bewährten m30n Pattern:
1. Prüfe alle Browser-Tabs auf localhost:1455 URL (Callback)
2. Alternativ: Prüfe ob auth.json kürzlich aktualisiert wurde
   (falls der Tab-Redirect verpasst wurde)
3. Timeout nach 60s

Der opencode auth login Prozess (gestartet in s14) lauscht auf Port 1455.
Wenn der Callback kommt, speichert er den Token automatisch in auth.json.

ERFOLG = Token wurde erfolgreich gespeichert. Bereit für push_to_pool.py.
"""

import asyncio
import nodriver as uc
import sys
import os
import time as time_module


async def run():
    # ── Mit Chrome verbinden ────────────────────────────────────────────────
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    print("S21: Warte auf localhost:1455 Callback (max 60s)...")

    # ── Callback-Loop: Prüfe Tabs und auth.json (max 60s) ───────────────────
    for i in range(120):  # 120 × 0.5s = 60s
        # ── Methode 1: Tab-URL prüfen ───────────────────────────────────────
        # Der OAuth-Flow redirected den Browser zu localhost:1455/auth/callback
        # wenn der Token erfolgreich ausgetauscht wurde.
        for tab in b.tabs:
            curr = getattr(tab.target, "url", "") or ""
            if "localhost:1455" in curr or "127.0.0.1:1455" in curr:
                print(f"S21 OK: Callback erreicht nach {i * 0.5}s!")
                # Kurz warten damit opencode auth login den Token speichern kann
                await asyncio.sleep(5)
                return True

        # ── Methode 2: auth.json Timestamp prüfen ──────────────────────────
        # Falls wir den Tab-Redirect verpasst haben (z.B. Tab wurde geschlossen
        # oder Redirect war zu schnell), prüfen wir ob auth.json kürzlich
        # aktualisiert wurde. opencode auth login speichert den Token dort.
        auth_paths = [
            os.path.expanduser("~/.local/share/opencode/auth.json"),
            os.path.expanduser("~/.config/opencode/auth.json"),
        ]
        for auth_path in auth_paths:
            if os.path.exists(auth_path):
                try:
                    mtime = os.path.getmtime(auth_path)
                    # Wurde in den letzten 30s aktualisiert?
                    if (time_module.time() - mtime) < 30:
                        print(f"S21 OK: auth.json Update erkannt ({auth_path})!")
                        return True
                except Exception:
                    pass

        # ── Methode 3: opencode_auth.log auf Erfolg prüfen ─────────────────
        # opencode auth login schreibt "success" oder "saved" ins Log
        if os.path.exists("/tmp/opencode_auth.log"):
            try:
                content = open("/tmp/opencode_auth.log", errors="ignore").read().lower()
                if (
                    "success" in content
                    or "saved" in content
                    or "authenticated" in content
                ):
                    print("S21 OK: Erfolg im opencode auth login Log erkannt!")
                    return True
            except Exception:
                pass

        await asyncio.sleep(0.5)

    # ── Timeout ─────────────────────────────────────────────────────────────
    print("S21 FAIL: Callback nicht innerhalb von 60s erreicht.")

    # Debug-Info ausgeben
    print("S21 DEBUG: Verfügbare Tabs:")
    for tab in b.tabs:
        tab_url = getattr(tab.target, "url", "") or ""
        print(f"  - {tab_url[:100]}")

    if os.path.exists("/tmp/opencode_auth.log"):
        print("S21 DEBUG: Letztes Log:")
        content = open("/tmp/opencode_auth.log", errors="ignore").read()
        # Nur die letzten 500 Zeichen ausgeben
        print(f"  {content[-500:]}")

    return False


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
