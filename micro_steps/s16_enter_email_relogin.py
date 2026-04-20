#!/usr/bin/env python3
"""
s16_enter_email_relogin.py — Email auf der OAuth Login-Seite eingeben.

Basiert auf dem bewährten m30b-Pattern:
1. Skip-Check: Wenn s_skip_login.txt existiert, brauchen wir kein Re-Login
2. Finde den auth.openai.com Tab (Inkognito)
3. Finde das Email-Eingabefeld
4. Lösche vorhandenen Inhalt (falls vorhanden)
5. Tippe die Temp-Mail Adresse Zeichen für Zeichen (Anti-Bot)
6. Klicke "Weiter" / "Continue" Button

WICHTIG: Die Email wird aus /tmp/current_email.txt gelesen.
Das ist dieselbe Email, mit der wir uns in s11 registriert haben.
"""

import asyncio
import nodriver as uc
import nodriver.cdp.input_ as input_cdp
import sys
import os


async def run():
    # ── Skip-Check: Kein Re-Login nötig wenn Flag gesetzt ───────────────────
    if os.path.exists("/tmp/s_skip_login.txt"):
        print("S16 SKIP: Kein Re-Login noetig (direkt Callback oder Authorize).")
        return True

    # ── Mit Chrome verbinden ────────────────────────────────────────────────
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    # ── Auth-Tab finden (Inkognito) ─────────────────────────────────────────
    # Der Tab wurde in s15 via window.open() im Inkognito-Fenster geöffnet.
    # Er sollte auf auth.openai.com sein (Login-Seite).
    t = None
    for tab in b.tabs:
        tab_url = getattr(tab, "url", getattr(tab.target, "url", "")) or ""
        if "auth.openai" in tab_url:
            t = tab
            break

    if not t:
        print("S16 FAIL: Kein auth.openai Tab gefunden.")
        print("S16 DEBUG: Verfügbare Tabs:")
        for tab in b.tabs:
            tab_url = getattr(tab, "url", getattr(tab.target, "url", "")) or ""
            print(f"  - {tab_url[:100]}")
        return False

    await t.bring_to_front()
    await asyncio.sleep(1)

    # ── Warten auf Email-Input (max 10s) ────────────────────────────────────
    # Die Login-Seite braucht manchmal etwas zum Laden.
    email_ready = False
    for _ in range(20):
        has_input = await t.evaluate("""(function(){
            var inp = document.querySelector('input[type="email"], input[name="email"], input[name="username"]');
            return !!inp;
        })()""")
        if has_input:
            email_ready = True
            break
        await asyncio.sleep(0.5)

    if not email_ready:
        print("S16 FAIL: Kein Email-Eingabefeld nach 10s gefunden.")
        return False

    # ── Email aus /tmp/current_email.txt lesen ──────────────────────────────
    if not os.path.exists("/tmp/current_email.txt"):
        print("S16 FAIL: /tmp/current_email.txt existiert nicht!")
        return False

    with open("/tmp/current_email.txt", "r") as f:
        email = f.read().strip()

    if not email:
        print("S16 FAIL: Email in /tmp/current_email.txt ist leer!")
        return False

    # ── Email-Feld leeren und Focus setzen ──────────────────────────────────
    # Sicherheitshalber vorhandenen Inhalt löschen (könnte vom Browser
    # auto-ausgefüllt worden sein, auch in Inkognito).
    await t.evaluate("""(function(){
        var inp = document.querySelector('input[type="email"], input[name="email"], input[name="username"]');
        if(inp) {
            inp.value = '';
            inp.focus();
            inp.dispatchEvent(new Event('input', {bubbles: true}));
        }
    })()""")
    await asyncio.sleep(0.3)

    # ── Email Zeichen für Zeichen tippen (Anti-Bot) ─────────────────────────
    # Direktes value-Setzen wird von React-Apps oft ignoriert.
    # Zeichen-für-Zeichen Tippen mit kleinen Delays simuliert echtes Tippen.
    for char in email:
        await t.send(input_cdp.dispatch_key_event(type_="char", text=char))
        await asyncio.sleep(0.04)  # 40ms zwischen Zeichen = menschlich
    print(f"S16 OK: Email '{email}' getippt.")

    # ── Anti-Bot Pause vor dem Submit ───────────────────────────────────────
    # Echte Menschen warten kurz nachdem sie ihre Email getippt haben.
    await asyncio.sleep(1.0)

    # ── "Weiter" / "Continue" Button klicken ────────────────────────────────
    # Versuche zuerst den submit-Button, dann Fallback mit Enter.
    clicked = await t.evaluate("""(function(){
        var btn = document.querySelector('button[type="submit"]');
        if(btn && !btn.disabled) {
            btn.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
            btn.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
            btn.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
            return true;
        }
        return false;
    })()""")

    if not clicked:
        # Fallback: Enter-Taste drücken
        print("S16: Kein Submit-Button gefunden, sende Enter...")
        await t.send(
            input_cdp.dispatch_key_event(
                type_="keyDown", key="Enter", windows_virtual_key_code=13
            )
        )
        await t.send(
            input_cdp.dispatch_key_event(
                type_="keyUp", key="Enter", windows_virtual_key_code=13
            )
        )

    print("S16 OK: Email eingegeben und Weiter geklickt.")
    await asyncio.sleep(2)
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
