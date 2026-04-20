#!/usr/bin/env python3
"""
s18_get_2nd_otp.py — 2. OTP von Temp-Mail holen.

Basiert auf dem bewährten m30h + m30i Pattern:
1. Prüfe ob OTP überhaupt nötig ist (s_otp_needed.txt)
2. Wechsle zum Temp-Mail Tab (NORMALES Chrome-Fenster, nicht Inkognito!)
3. Lade die Inbox neu (KRITISCH: verhindert stale Email-Cache)
4. Warte auf NEUE OpenAI Email (muss sich vom 1. OTP unterscheiden!)
5. Extrahiere den 6-stelligen Code
6. Speichere in /tmp/current_otp2.txt

WICHTIG: Der Temp-Mail Tab läuft im Default-Profil (normales Fenster),
nicht im Inkognito-Fenster. CDP auf Port 9334 sieht BEIDE Fenster.
"""

import asyncio
import nodriver as uc
import sys
import os

# Reuse the shared helper so both OTP steps benefit from the same hardened email
# discovery and parsing logic instead of drifting into separate implementations.
from _otp_helper import extract_otp_from_tempmail


async def run():
    # ── Skip-Check: OTP nötig? ──────────────────────────────────────────────
    otp_needed = "0"
    if os.path.exists("/tmp/s_otp_needed.txt"):
        otp_needed = open("/tmp/s_otp_needed.txt").read().strip()
    if os.path.exists("/tmp/s_skip_login.txt"):
        print("S18 SKIP: Kein Re-Login noetig.")
        return True
    if otp_needed != "1":
        print("S18 SKIP: Kein 2. OTP noetig.")
        return True

    # ── 1. OTP laden (zum Vergleich, damit wir nicht den alten Code nehmen) ─
    old_otp = ""
    if os.path.exists("/tmp/current_otp.txt"):
        old_otp = open("/tmp/current_otp.txt").read().strip()
    print(f"S18: 1. OTP war '{old_otp}'. Suche NEUEN Code...")

    # ── Mit Chrome verbinden ────────────────────────────────────────────────
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    # ── Temp-Mail Tab finden (normales Fenster, NICHT Inkognito) ─────────────
    temp_tab = None
    for tab in b.tabs:
        tab_url = getattr(tab, "url", getattr(tab.target, "url", "")) or ""
        if "temp-mail" in tab_url:
            temp_tab = tab
            break

    if not temp_tab:
        # Fallback: Temp-Mail Inbox in neuem Tab öffnen
        # ACHTUNG: Dieser Tab öffnet sich im Default-Profil (nicht Inkognito),
        # was korrekt ist — die Premium-Session Cookies sind dort gespeichert.
        print("S18 WARN: Kein Temp-Mail Tab gefunden. Oeffne neuen...")
        temp_tab = await b.get("https://temp-mail.org/en/", new_tab=True)
        await asyncio.sleep(3)
    else:
        await temp_tab.bring_to_front()
        await asyncio.sleep(0.5)

    # ── KRITISCH: Inbox neu laden ───────────────────────────────────────────
    # Ohne Reload zeigt Temp-Mail möglicherweise die alte Email an (Cache!).
    # Durch Navigation zur Startseite wird die Inbox komplett neu geladen.
    print("S18: Lade Temp-Mail Inbox neu (Cache-Bust)...")
    await temp_tab.get("https://temp-mail.org/en/")
    await asyncio.sleep(3)

    # ── Warte auf neue OpenAI Email (max 60s) ───────────────────────────────
    # Der 2. OTP wird von OpenAI gesendet nachdem wir in s17
    # "Mit Einmalcode anmelden" geklickt haben. Kann 5-30s dauern.
    for i in range(60):
        # Use the shared fallback helper in short polling windows so we still keep
        # the existing stale-code check and inbox reset behavior around the 2nd OTP.
        code = await extract_otp_from_tempmail(temp_tab, timeout=2)

        if code and code != old_otp:
            # NEUER Code gefunden! Verschieden vom 1. OTP.
            with open("/tmp/current_otp2.txt", "w") as f:
                f.write(code)
            print(f"S18 OK: 2. OTP = {code} (nach {i}s, 1. OTP war {old_otp})")
            return True

        if code == old_otp and code:
            # Gleicher Code wie beim 1. OTP — alte Email gecacht. Wir gehen
            # bewusst zurück in die Inbox und warten weiter auf die neue Mail.
            print(f"S18: Code {code} == 1. OTP (stale). Zurueck zur Inbox...")
            await temp_tab.get("https://temp-mail.org/en/")
            await asyncio.sleep(3)
        elif code is None:
            # Kein verwertbarer Code gefunden. Wir lassen die regelmäßigen Reloads
            # weiterlaufen, damit Temp-Mail frische Inbox-Daten liefert.
            if i % 10 == 0 and i > 0:
                print(f"S18: Warte auf 2. OTP Email... ({i}s)")
                await temp_tab.get("https://temp-mail.org/en/")
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(1)

    print("S18 FAIL: Timeout — 2. OTP Email nicht innerhalb von 60s erhalten.")
    return False


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
