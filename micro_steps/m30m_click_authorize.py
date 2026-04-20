import asyncio, nodriver as uc, sys, os, re, subprocess

# ────────────────────────────────────────────────────────────────
# JS: Click the Authorize / Allow / Zulassen / Erlauben button
# Fires a full mousedown→mouseup→click chain (React-compatible)
# ────────────────────────────────────────────────────────────────
_AUTH = """(function(){
    var btns = Array.from(document.querySelectorAll('button, [role="button"], input[type="submit"]'));
    var b = btns.find(x => {
        var txt = (x.innerText || x.textContent || x.value || '').trim().toLowerCase();
        return /authorize|erlauben|allow|zulassen|fortfahren|accept|akzeptieren/i.test(txt);
    });
    if(!b) {
        b = document.querySelector('button[type="submit"]:not([name="cancel"]), .btn-primary, button[data-action="authorize"]');
    }
    if(b && !b.disabled) { 
        b.dispatchEvent(new MouseEvent('mousedown', {bubbles:true}));
        b.dispatchEvent(new MouseEvent('mouseup', {bubbles:true}));
        b.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
        return true; 
    }
    return false;
})()"""

# ────────────────────────────────────────────────────────────────
# JS: Try to skip/dismiss the add-phone page.
# OpenAI removed the "Not now" button in late 2025, so this now
# looks for any dismissal option. If none found → returns false.
# ────────────────────────────────────────────────────────────────
_SKIP_PHONE = """(function(){
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
    """Kill old opencode auth login processes and start a fresh one.

    Returns the new OAuth URL once it appears in /tmp/opencode_auth.log.
    This is needed when OpenAI's add-phone wall blocks the current OAuth session —
    a fresh OAuth URL bypasses the phone wall because it starts a clean auth flow.
    """
    print("M30m: add-phone wall erkannt — restarting opencode auth login ...")

    # Kill any existing opencode auth login processes on port 1455
    os.system("lsof -ti tcp:1455 | xargs kill -9 2>/dev/null")
    os.system("pkill -f 'opencode auth login' 2>/dev/null")
    import time

    time.sleep(1)

    # Clear old log and restart
    os.system("rm -f /tmp/opencode_auth.log /tmp/oauth_url.txt /tmp/m30_skip_login.txt")
    subprocess.Popen(
        'opencode auth login --provider openai --method "ChatGPT Pro/Plus (browser)" > /tmp/opencode_auth.log 2>&1',
        shell=True,
        start_new_session=True,
    )
    print("M30m: Fresh opencode auth login started. Warte auf neue OAuth URL ...")

    # Wait up to 20s for the new URL to appear in the log
    for _ in range(40):
        time.sleep(0.5)
        if os.path.exists("/tmp/opencode_auth.log"):
            content = open("/tmp/opencode_auth.log", errors="ignore").read()
            m = re.search(r"(https://auth\.openai\.com[^\s\x1b]+)", content)
            if m:
                url = m.group(1)
                print(f"M30m: Neue OAuth URL: {url[:70]}...")
                return url
    print("M30m WARN: Keine neue OAuth URL nach 20s erhalten.")
    return None


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    # KRITISCH: Singleton-Patch — verhindert dass nodriver Chrome killt beim Beenden
    b._browser_process = None
    b._process_pid = None

    # ── Finde den aktiven OpenAI/Auth Tab ──────────────────────
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "openai.com" in url or "chatgpt.com" in url:
            t = tab
            break
    if not t:
        print("M30m FAIL: Kein OpenAI Tab gefunden.")
        return False

    await t.bring_to_front()

    phone_bypass_attempted = False  # Verhindert endlose Retry-Schleife

    for i in range(80):  # Max 40 Sekunden (80 × 0.5s)
        curr = getattr(t.target, "url", "") or ""

        # ── ERFOLG: Callback erreicht ───────────────────────────
        if "localhost:1455" in curr:
            print("M30m OK: Callback erfolgreich erreicht!")
            return True

        # ── add-phone Wall: OpenAI verlangt Telefonnummer ───────
        if "add-phone" in curr or ("verify" in curr and "phone" in curr):
            # Erst versuchen ob es einen Skip-Button gibt (ältere OpenAI-Versionen)
            if await t.evaluate(_SKIP_PHONE):
                print(f"M30m INFO: Phone skip geklickt (Iteration {i})")
                await asyncio.sleep(2)
                continue

            # Kein Skip-Button — phone wall ist mandatory.
            # Strategie: frischen opencode auth login starten und OAuth URL neu öffnen.
            if not phone_bypass_attempted:
                phone_bypass_attempted = True
                new_url = _restart_opencode_auth()
                if new_url:
                    print(f"M30m: Navigiere zu frischer OAuth URL ...")
                    await t.get(new_url)
                    await asyncio.sleep(3)
                    # Schauen ob wir jetzt auf der Login- oder Authorize-Seite sind
                    curr2 = getattr(t.target, "url", "") or ""
                    print(f"M30m: Nach frischer URL: {curr2[:80]}")
                    continue
                else:
                    print(
                        "M30m FAIL: Kein frisches OAuth URL erhalten — Phone Wall nicht überwindbar."
                    )
                    return False
            else:
                # Zweiter Versuch gescheitert — phone wall hält an
                print(
                    "M30m FAIL: add-phone Wall nach Neustart immer noch aktiv. Abbruch."
                )
                return False

        # ── Authorize Button klicken ────────────────────────────
        if await t.evaluate(_AUTH):
            print(f"M30m OK: Authorize geklickt (Iteration {i})!")

            # Warte gezielt auf localhost Redirect nach dem Klick
            for j in range(20):
                curr2 = getattr(t.target, "url", "") or ""
                if "localhost:1455" in curr2:
                    print("M30m OK: Callback nach Authorize-Klick erfolgreich!")
                    return True
                await asyncio.sleep(0.5)
            # Authorize hat nicht sofort geredirectet — äußere Schleife weiter
            print(
                f"M30m INFO: Authorize geklickt aber kein Redirect nach 10s. Weiter warten ..."
            )
        else:
            # Kein Authorize-Button gefunden — Seite lädt noch oder anderer Zustand
            await asyncio.sleep(0.5)

    print("M30m WARN: Authorize-Schleife nach 40s beendet ohne Callback.")
    return True  # Nicht False — m30n soll noch auf den Callback prüfen


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
