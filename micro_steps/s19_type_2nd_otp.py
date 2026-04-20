#!/usr/bin/env python3
"""
s19_type_2nd_otp.py — 2. OTP in den Auth-Tab tippen und absenden.

Basiert auf dem bewährten m30k + m30l Pattern:
1. Prüfe ob OTP überhaupt nötig ist
2. Wechsle zurück zum auth.openai.com Tab (Inkognito!)
3. Lösche vorhandenen Inhalt im OTP-Feld (KRITISCH — stale Codes!)
4. Tippe den 2. OTP Code Zeichen für Zeichen
5. Klicke "Weiter" / "Continue"

KRITISCH: Das OTP-Feld MUSS vor dem Tippen geleert werden!
Manchmal enthält es bereits einen alten/falschen Code.
Wir nutzen Cmd+A + Backspace (bewährtes Pattern aus s13).
"""

import asyncio
import nodriver as uc
import nodriver.cdp.input_ as input_cdp
import sys
import os


async def run():
    # ── Skip-Checks ─────────────────────────────────────────────────────────
    if os.path.exists("/tmp/s_skip_login.txt"):
        print("S19 SKIP: Kein Re-Login noetig.")
        return True

    otp_needed = "0"
    if os.path.exists("/tmp/s_otp_needed.txt"):
        otp_needed = open("/tmp/s_otp_needed.txt").read().strip()
    if otp_needed != "1":
        print("S19 SKIP: Kein 2. OTP noetig.")
        return True

    # ── 2. OTP aus Datei lesen ──────────────────────────────────────────────
    if not os.path.exists("/tmp/current_otp2.txt"):
        print("S19 FAIL: /tmp/current_otp2.txt existiert nicht!")
        return False

    otp = open("/tmp/current_otp2.txt").read().strip()

    # ── Validierung: 2. OTP muss gültig und verschieden vom 1. sein ────────
    old_otp = ""
    if os.path.exists("/tmp/current_otp.txt"):
        old_otp = open("/tmp/current_otp.txt").read().strip()

    if otp == old_otp:
        print(f"S19 FAIL: 2. OTP ({otp}) == 1. OTP! Stale Code.")
        return False
    if len(otp) != 6 or not otp.isdigit():
        print(f"S19 FAIL: Ungueltiger 2. OTP Code: '{otp}'")
        return False

    print(f"S19: 2. OTP = {otp} (1. war {old_otp})")

    # ── Mit Chrome verbinden ────────────────────────────────────────────────
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    # ── Auth-Tab finden (Inkognito) ─────────────────────────────────────────
    # Bevorzuge email-verification URL, dann auth.openai.com allgemein
    t = None
    for tab in b.tabs:
        tab_url = getattr(tab, "url", getattr(tab.target, "url", "")) or ""
        if "email-verification" in tab_url:
            t = tab
            break
    if not t:
        for tab in b.tabs:
            tab_url = getattr(tab, "url", getattr(tab.target, "url", "")) or ""
            if "auth.openai" in tab_url:
                t = tab
                break

    if not t:
        print("S19 FAIL: Kein auth.openai Tab gefunden.")
        return False

    await t.bring_to_front()
    await asyncio.sleep(1)

    # ── OTP-Feld finden, leeren und fokussieren ─────────────────────────────
    # KRITISCH: Zuerst alles im Feld löschen! Kann stale Code enthalten.
    # Wir nutzen JavaScript um das Feld zu leeren UND zu fokussieren.
    await t.evaluate("""(function(){
        var inp = document.querySelector('input[inputmode="numeric"], input[name="code"], input[type="text"]');
        if(inp) {
            inp.value = '';
            inp.focus();
            // React-Event triggern damit der interne State auch geleert wird
            inp.dispatchEvent(new Event('input', {bubbles: true}));
            inp.dispatchEvent(new Event('change', {bubbles: true}));
        }
    })()""")
    await asyncio.sleep(0.3)

    # ── Zusätzlich Cmd+A + Backspace (Sicherheitsnetz) ──────────────────────
    # Falls das JavaScript value='' nicht greift (React controlled component),
    # machen wir noch Cmd+A + Backspace wie in s13.
    await t.send(
        input_cdp.dispatch_key_event(
            type_="keyDown", key="a", windows_virtual_key_code=65, modifiers=8
        )
    )
    await t.send(
        input_cdp.dispatch_key_event(
            type_="keyUp", key="a", windows_virtual_key_code=65, modifiers=8
        )
    )
    await asyncio.sleep(0.1)
    await t.send(
        input_cdp.dispatch_key_event(
            type_="keyDown", key="Backspace", windows_virtual_key_code=8
        )
    )
    await t.send(
        input_cdp.dispatch_key_event(
            type_="keyUp", key="Backspace", windows_virtual_key_code=8
        )
    )
    await asyncio.sleep(0.3)

    # ── OTP Zeichen für Zeichen tippen ──────────────────────────────────────
    for char in otp:
        await t.send(input_cdp.dispatch_key_event(type_="char", text=char))
        await asyncio.sleep(0.1)  # 100ms zwischen Zeichen — etwas langsamer für OTP
    print(f"S19 OK: 2. OTP '{otp}' getippt.")

    # ── Anti-Bot Pause ──────────────────────────────────────────────────────
    await asyncio.sleep(1.0)

    # ── Submit klicken ──────────────────────────────────────────────────────
    # Versuche Submit-Button, dann Fallback mit Enter
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
        print("S19: Kein Submit-Button, sende Enter...")
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

    print("S19 OK: 2. OTP submitted.")
    await asyncio.sleep(3)
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
