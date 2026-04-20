#!/usr/bin/env python3
"""
s20_click_authorize.py — Authorize/Allow Button klicken.

Basiert auf dem bewährten m30m Pattern:
1. Finde den aktiven OpenAI/Auth Tab (Inkognito)
2. Warte auf Authorize-Button ("Authorize", "Allow", "Erlauben", "Zulassen")
3. Klicke mit React-kompatibler mousedown→mouseup→click Kette
4. Warte auf localhost:1455 Redirect (Callback)
5. Handle Sonderfälle: add-phone Wall, Consent-Seite

SONDERFALL: add-phone Wall
OpenAI verlangt manchmal eine Telefonnummer (add-phone Seite).
In diesem Fall versuchen wir:
1. "Not now" / "Jetzt nicht" / "Skip" Button klicken
2. Falls kein Skip möglich: Frischen opencode auth login starten
3. Falls beides fehlschlägt: FAIL (Phone Wall nicht überwindbar)
"""

import asyncio
import nodriver as uc
import sys
import os
import re
import subprocess

# ── JavaScript: Authorize Button klicken (React-kompatibel) ─────────────────
# Sucht nach dem Button mit passendem Text und feuert die volle
# mousedown→mouseup→click Event-Kette (gegen React Event Swallowing).
_AUTH_JS = """(function(){
    var btns = Array.from(document.querySelectorAll('button, [role="button"], input[type="submit"]'));
    var b = btns.find(x => {
        var txt = (x.innerText || x.textContent || x.value || '').trim().toLowerCase();
        return /authorize|erlauben|allow|zulassen|fortfahren|accept|akzeptieren|continue|weiter/i.test(txt);
    });
    if(!b) {
        // Fallback: Generischer Submit-Button
        b = document.querySelector('button[type="submit"]:not([name="cancel"]), .btn-primary');
    }
    if(b && !b.disabled) {
        b.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
        b.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
        b.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
        return true;
    }
    return false;
})()"""

# ── JavaScript: Skip Phone Page ─────────────────────────────────────────────
_SKIP_PHONE_JS = """(function(){
    var links = Array.from(document.querySelectorAll('a, button'));
    var skip = links.find(l => {
        var t = (l.innerText||'').toLowerCase();
        return t.includes('not now') || t.includes('jetzt nicht') ||
               t.includes('skip') || t.includes('später') ||
               t.includes('überspringen') || t.includes('maybe later') ||
               t.includes('remind me later');
    });
    if(skip) { skip.click(); return true; }
    return false;
})()"""


def _restart_opencode_auth():
    """Startet einen frischen opencode auth login Prozess.

    Wird verwendet wenn die add-phone Wall den aktuellen OAuth-Flow blockiert.
    Ein frischer OAuth-Flow startet eine neue Auth-Session, die möglicherweise
    die Phone Wall umgeht.

    Returns: Die neue OAuth URL oder None bei Timeout.
    """
    import time

    print("S20: add-phone Wall erkannt — restarting opencode auth login...")

    # Alte Prozesse killen
    os.system("lsof -ti tcp:1455 | xargs kill -9 2>/dev/null")
    os.system("pkill -f 'opencode auth login' 2>/dev/null")
    time.sleep(1)

    # Altes Log löschen und neu starten
    os.system("rm -f /tmp/opencode_auth.log /tmp/oauth_url.txt")
    subprocess.Popen(
        'opencode auth login --provider openai --method "ChatGPT Pro/Plus (browser)" > /tmp/opencode_auth.log 2>&1',
        shell=True,
        start_new_session=True,
    )
    print("S20: Fresh opencode auth login started. Warte auf neue OAuth URL...")

    # Bis zu 20s auf neue URL warten
    for _ in range(40):
        time.sleep(0.5)
        if os.path.exists("/tmp/opencode_auth.log"):
            content = open("/tmp/opencode_auth.log", errors="ignore").read()
            m = re.search(r"(https://auth\.openai\.com[^\s\x1b]+)", content)
            if m:
                url = m.group(1)
                print(f"S20: Neue OAuth URL: {url[:70]}...")
                return url

    print("S20 WARN: Keine neue OAuth URL nach 20s erhalten.")
    return None


async def run():
    # ── Mit Chrome verbinden ────────────────────────────────────────────────
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    # ── Finde den aktiven OpenAI/Auth Tab ───────────────────────────────────
    t = None
    for tab in b.tabs:
        tab_url = getattr(tab.target, "url", "") or ""
        if (
            "auth.openai.com" in tab_url
            or "openai.com" in tab_url
            or "chatgpt.com" in tab_url
        ):
            t = tab
            break

    if not t:
        print("S20 FAIL: Kein OpenAI Tab gefunden.")
        return False

    await t.bring_to_front()

    # ── Flag: Verhindert endlose Retry-Schleife bei Phone Wall ──────────────
    phone_bypass_attempted = False

    # ── Haupt-Loop: Warte auf Authorize oder Callback (max 40s) ─────────────
    for i in range(80):  # 80 × 0.5s = 40s
        curr = getattr(t.target, "url", "") or ""

        # ── ERFOLG: Callback erreicht ───────────────────────────────────────
        if "localhost:1455" in curr or "127.0.0.1:1455" in curr:
            print("S20 OK: Callback erfolgreich erreicht!")
            return True

        # ── add-phone Wall: OpenAI verlangt Telefonnummer ───────────────────
        if "add-phone" in curr or ("verify" in curr and "phone" in curr):
            # Versuche Skip-Button
            if await t.evaluate(_SKIP_PHONE_JS):
                print(f"S20 INFO: Phone skip geklickt (Iteration {i})")
                await asyncio.sleep(2)
                continue

            # Kein Skip → frischen OAuth Flow starten (einmalig)
            if not phone_bypass_attempted:
                phone_bypass_attempted = True
                new_url = _restart_opencode_auth()
                if new_url:
                    print("S20: Navigiere zu frischer OAuth URL...")
                    await t.get(new_url)
                    await asyncio.sleep(3)
                    continue
                else:
                    print("S20 FAIL: Phone Wall nicht überwindbar.")
                    return False
            else:
                print("S20 FAIL: add-phone Wall nach Neustart immer noch aktiv.")
                return False

        # ── Authorize Button klicken ────────────────────────────────────────
        if await t.evaluate(_AUTH_JS):
            print(f"S20 OK: Authorize geklickt (Iteration {i})!")

            # Warte gezielt auf localhost Redirect nach Klick (max 10s)
            for j in range(20):
                curr2 = getattr(t.target, "url", "") or ""
                if "localhost:1455" in curr2 or "127.0.0.1:1455" in curr2:
                    print("S20 OK: Callback nach Authorize-Klick erfolgreich!")
                    return True
                await asyncio.sleep(0.5)

            # Authorize geklickt aber kein sofortiger Redirect
            print(
                "S20 INFO: Authorize geklickt aber kein Redirect nach 10s. Weiter warten..."
            )
        else:
            # Kein Authorize-Button → Seite lädt noch oder anderer Zustand
            await asyncio.sleep(0.5)

    # ── Timeout: 40s ohne Callback ──────────────────────────────────────────
    # Nicht als FAIL markieren — s21 prüft nochmal auf den Callback
    print("S20 WARN: Authorize-Schleife nach 40s beendet ohne Callback.")
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
