#!/usr/bin/env python3
"""
OPEN SIN STEALTH BROWSER - Micro-Step: Registrieren klicken (v0.5.0)

WAS: Sucht den 'Registrieren' oder 'Sign Up' Button auf OpenAI/chatgpt.com und klickt ihn.
WARUM: Startet den Account-Erstellungsflow. Nutzt ID-basierten Klick für Zuverlässigkeit.

ACHTUNG FÜR ENTWICKLER:
- Nicht ändern ohne Testing! JS-Selector sind empfindlich.
- Port 9334 = Temp-Mail Browser (Default Profile mit Login).
- Kein Passwort nötig, Pipeline erstellt NEUE Accounts automatisch.
- 0% User Interaction erforderlich!
"""

import asyncio
import nodriver as uc
import sys

# JavaScript zum Finden des Registrieren-Buttons
# WARUM: OpenAI verwendet React, normale Clicks funktionieren nicht immer.
# Dieser Script sucht nach Text-Mustern in allen Links/Buttons.
_FIND_REG = """(function(){
    var links = Array.from(document.querySelectorAll("a, button"));
    var reg = links.find(l => {
        var t = (l.innerText||l.textContent||"").toLowerCase().trim();
        return t.includes("registrieren") || t.includes("sign up") || t.includes("get started") || t.includes("create account");
    });
    if(reg) {
        reg.setAttribute("id", "mcp_reg_btn");
        return true;
    }
    return false;
})()"""

async def run():
    """
    Hauptfunktion: Verbindet mit Browser (Port 9334), findet Tab, klickt Button.
    
    Rückgabe: True bei Erfolg, False bei Fehler.
    """
    # Verbinde mit existierendem Browser (Singleton Patch in fast_runner.py)
    # WARUM: Port 9334 ist der Temp-Mail Browser mit Default-Profil (Login bleibt!)
    b = await uc.start(host="127.0.0.1", port=9334)
    
    # WICHTIG: Verhindert dass nodriver den Browser beim Schließen killt
    b._browser_process = None
    b._process_pid = None

    # Suche echten Tab (nicht chrome:// oder about:blank)
    # WARUM: Browser hat oft leere Tabs, wir brauchen den mit OpenAI-Seite.
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if not url.startswith("chrome://"):
            t = tab
            break
    
    if not t:
        print("M03 FAIL: Kein echter Tab gefunden!")
        return False

    # Warte bis Seite wirklich geladen ist (URL muss chatgpt.com oder openai.com sein)
    # WARUM: Seite lädt eventuell noch, JS würde sonst fehlschlagen.
    for i in range(20):  # Max 10 Sekunden warten
        url = getattr(t.target, "url", "") or ""
        if "chatgpt.com" in url or "openai.com" in url:
            break
        await asyncio.sleep(0.5)

    # Führe JS aus um Button zu finden und ID zu setzen
    found = await t.evaluate(_FIND_REG)
    
    if found:
        print("M03 OK: 'Registrieren' Button gefunden, klicke...")
        # Klicke via ID (zuverlässiger als QuerySelector)
        await t.evaluate("document.getElementById('mcp_reg_btn').click();")
        return True

    # Fallback: Vielleicht sind wir schon direkt auf der Create-Account Seite
    # WARUM: Manchmal leitet OpenAI direkt weiter, kein Button nötig.
    url = getattr(t.target, "url", "") or ""
    if "create-account" in url or "signup" in url:
        print("M03 OK: Direkt auf Create-Account Seite, kein Klick nötig.")
        return True

    # Fehlerfall: Button nicht gefunden
    print("M03 FAIL: 'Registrieren' Button nicht gefunden!")
    print(f"  Aktuelle URL: {getattr(t.target, 'url', 'unbekannt')}")
    return False

if __name__ == "__main__":
    # Exit-Code: 0 = Erfolg, 1 = Fehler (für Pipeline-Executor wichtig!)
    sys.exit(0 if asyncio.run(run()) else 1)
