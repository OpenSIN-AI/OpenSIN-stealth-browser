#!/usr/bin/env python3
"""
s17_click_einmalcode.py — "Mit Einmalcode anmelden" auf der Passwort-Seite klicken.

Nach s16 (Email eingegeben + Continue) kann OpenAI verschiedene Seiten zeigen:
1. Passwort-Seite → Hier klicken wir "Mit Einmalcode anmelden" (OTP statt Passwort)
2. OTP-Seite direkt → Kein Klick nötig, OpenAI hat direkt OTP gewählt
3. Authorize-Seite → Kein Login nötig, direkt autorisieren (skip)
4. Callback (localhost:1455) → Bereits fertig (skip)

WARUM OTP statt Passwort?
- Das Passwort wurde in s12 zufällig generiert und ist in /tmp/current_password.txt
- Trotzdem nutzen wir OTP, weil OpenAI manchmal zusätzliche Verifizierung
  bei Passwort-Logins verlangt (z.B. CAPTCHA oder erneutes Email-Verify)
- OTP ist der zuverlässigere Pfad für frisch registrierte Accounts
"""

import asyncio
import nodriver as uc
import sys
import os


async def run():
    # ── Skip-Check ──────────────────────────────────────────────────────────
    if os.path.exists("/tmp/s_skip_login.txt"):
        print("S17 SKIP: Kein Re-Login noetig.")
        return True

    # ── Mit Chrome verbinden ────────────────────────────────────────────────
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    # ── Auth-Tab finden ─────────────────────────────────────────────────────
    t = None
    for tab in b.tabs:
        tab_url = getattr(tab, "url", getattr(tab.target, "url", "")) or ""
        if "auth.openai" in tab_url:
            t = tab
            break

    if not t:
        print("S17 FAIL: Kein auth.openai Tab gefunden.")
        return False

    await t.bring_to_front()

    # ── Warten auf Seitenzustand (max 15s) ──────────────────────────────────
    # Wir warten bis die Seite einen der bekannten Zustände erreicht:
    # - Passwort-Input → klicke "Einmalcode"
    # - OTP-Input → schon auf OTP-Seite, nichts zu tun
    # - Authorize-Buttons → kein Login nötig
    # - Callback → bereits fertig
    for attempt in range(30):
        curr = getattr(t, "url", getattr(t.target, "url", "")) or ""

        # ── Fall 4: Callback bereits erreicht ───────────────────────────────
        if "localhost:1455" in curr or "127.0.0.1:1455" in curr:
            print("S17 OK: Direkt Callback! Kein Login noetig.")
            with open("/tmp/s_skip_login.txt", "w") as f:
                f.write("1")
            return True

        # ── Seite analysieren ───────────────────────────────────────────────
        state = await t.evaluate("""(function(){
            // Passwort-Input vorhanden?
            var pw = document.querySelector('input[type="password"]');
            if(pw) return 'password';

            // OTP-Input vorhanden? (numerisch, 6-stellig)
            var otp = document.querySelector('input[inputmode="numeric"], input[name="code"]');
            if(otp) return 'otp';

            // Authorize-Button vorhanden?
            var btns = Array.from(document.querySelectorAll('button'));
            var auth = btns.some(x => /authorize|erlauben|allow|zulassen/i.test(x.textContent));
            if(auth) return 'authorize';

            // Email-Verification Seite?
            if(window.location.href.includes('email-verification')) return 'otp';

            return '';
        })()""")

        # ── Fall 3: Authorize-Seite → Skip Login ───────────────────────────
        if state == "authorize":
            print("S17 OK: Authorize-Seite erkannt. Kein Login noetig.")
            with open("/tmp/s_skip_login.txt", "w") as f:
                f.write("1")
            return True

        # ── Fall 2: OTP-Seite → Bereits im OTP-Modus ───────────────────────
        if state == "otp":
            print("S17 OK: Bereits auf OTP-Seite. 2. OTP wird benoetigt.")
            with open("/tmp/s_otp_needed.txt", "w") as f:
                f.write("1")
            return True

        # ── Fall 1: Passwort-Seite → "Mit Einmalcode anmelden" klicken ─────
        if state == "password":
            print("S17: Passwort-Seite erkannt. Suche 'Mit Einmalcode anmelden'...")

            # Suche den Link "Mit Einmalcode anmelden" / "Log in with a one-time code"
            # OpenAI zeigt diesen Link unter dem Passwort-Feld.
            clicked = await t.evaluate("""(function(){
                // Alle Links und Buttons auf der Seite durchsuchen
                var elements = Array.from(document.querySelectorAll('a, button, span[role="button"]'));
                var einmalcode = elements.find(function(el){
                    var txt = (el.innerText || el.textContent || '').toLowerCase();
                    // Deutsche und englische Varianten
                    return txt.includes('einmalcode') ||
                           txt.includes('one-time code') ||
                           txt.includes('login code') ||
                           txt.includes('code senden') ||
                           txt.includes('email a login code') ||
                           txt.includes('email me a login code') ||
                           txt.includes('send code');
                });
                if(einmalcode) {
                    // React-kompatible Klick-Kette
                    einmalcode.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
                    einmalcode.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
                    einmalcode.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
                    return true;
                }
                return false;
            })()""")

            if clicked:
                print("S17 OK: 'Mit Einmalcode anmelden' geklickt!")
                await asyncio.sleep(2)

                # Warte auf OTP-Input (max 10s)
                for _ in range(20):
                    has_otp = await t.evaluate("""(function(){
                        var otp = document.querySelector('input[inputmode="numeric"], input[name="code"]');
                        return !!otp;
                    })()""")
                    if has_otp:
                        print(
                            "S17 OK: OTP-Eingabefeld erschienen. 2. OTP wird benoetigt."
                        )
                        with open("/tmp/s_otp_needed.txt", "w") as f:
                            f.write("1")
                        return True
                    # Prüfe auch auf email-verification URL
                    curr2 = getattr(t, "url", getattr(t.target, "url", "")) or ""
                    if "email-verification" in curr2:
                        print(
                            "S17 OK: Email-Verification Seite erkannt. 2. OTP wird benoetigt."
                        )
                        with open("/tmp/s_otp_needed.txt", "w") as f:
                            f.write("1")
                        return True
                    await asyncio.sleep(0.5)

                print("S17 WARN: OTP-Input nach Einmalcode-Klick nicht erschienen.")
                # Trotzdem weitermachen — vielleicht kommt es noch
                with open("/tmp/s_otp_needed.txt", "w") as f:
                    f.write("1")
                return True
            else:
                # Kein "Einmalcode" Link gefunden — Fallback: Passwort tippen
                # Das sollte eigentlich nicht passieren, aber als Fallback
                # nutzen wir das gespeicherte Passwort
                print(
                    "S17 WARN: Kein 'Einmalcode' Link gefunden! Fallback: Passwort nutzen."
                )
                if os.path.exists("/tmp/current_password.txt"):
                    import nodriver.cdp.input_ as input_cdp

                    pwd = open("/tmp/current_password.txt").read().strip()
                    # Passwort-Feld fokussieren und tippen
                    await t.evaluate("""(function(){
                        var inp = document.querySelector('input[type="password"]');
                        if(inp) inp.focus();
                    })()""")
                    await asyncio.sleep(0.3)
                    for char in pwd:
                        await t.send(
                            input_cdp.dispatch_key_event(type_="char", text=char)
                        )
                        await asyncio.sleep(0.04)
                    await asyncio.sleep(1.0)
                    # Submit klicken
                    await t.evaluate("""(function(){
                        var btn = document.querySelector('button[type="submit"]');
                        if(btn) btn.click();
                    })()""")
                    print("S17 OK: Passwort getippt und submitted (Fallback).")
                    await asyncio.sleep(2)

                    # Prüfe ob OTP danach nötig ist (OpenAI verlangt manchmal
                    # trotzdem OTP nach Passwort bei frischen Accounts)
                    for _ in range(10):
                        curr3 = getattr(t, "url", getattr(t.target, "url", "")) or ""
                        if "localhost:1455" in curr3:
                            print("S17 OK: Direkt Callback nach Passwort!")
                            with open("/tmp/s_skip_login.txt", "w") as f:
                                f.write("1")
                            return True
                        has_otp = await t.evaluate(
                            "!!document.querySelector('input[inputmode=\"numeric\"]')"
                        )
                        if has_otp or "email-verification" in curr3:
                            print("S17 OK: OTP nach Passwort noetig.")
                            with open("/tmp/s_otp_needed.txt", "w") as f:
                                f.write("1")
                            return True
                        has_auth = await t.evaluate("""(function(){
                            var b = document.querySelectorAll('button');
                            return Array.from(b).some(x =>
                                /authorize|erlauben|allow/i.test(x.textContent)
                            );
                        })()""")
                        if has_auth:
                            print("S17 OK: Authorize nach Passwort. Kein OTP noetig.")
                            with open("/tmp/s_skip_login.txt", "w") as f:
                                f.write("1")
                            return True
                        await asyncio.sleep(0.5)

                    # Unbekannter Zustand nach Passwort
                    print("S17 WARN: Unbekannter Zustand nach Passwort-Login.")
                    return True
                else:
                    print("S17 FAIL: Kein Einmalcode-Link UND kein Passwort verfügbar!")
                    return False

        # Noch kein Zustand erkannt → weiter warten
        await asyncio.sleep(0.5)

    print("S17 FAIL: Timeout — weder Passwort noch OTP noch Authorize Seite nach 15s.")
    return False


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
