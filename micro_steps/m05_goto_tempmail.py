import asyncio, nodriver as uc, sys, os
from nodriver.cdp.input_ import dispatch_key_event

async def press(t, key_name, vk, mods=0):
    await t.send(dispatch_key_event(type_="keyDown", key=key_name, code=key_name, windows_virtual_key_code=vk, modifiers=mods))
    await t.send(dispatch_key_event(type_="keyUp", key=key_name, code=key_name, windows_virtual_key_code=vk, modifiers=mods))
    await asyncio.sleep(0.3)

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    t = None
    for tab in b.tabs:
        if "temp-mail.org" in getattr(tab.target, "url", ""):
            t = tab
            break
            
    if not t:
        t = await b.get("https://temp-mail.org/en/", new_tab=True)
    else:
        await t.bring_to_front()
        
    # SICHERE NAVIGATION: Keine Hänger
    asyncio.create_task(t.get("https://temp-mail.org/en/"))
    await asyncio.sleep(5)

    # DOM-VERIFIKATION VOR DER AKTION (PRIORITY -8.0 REGEL!)
    # Wir prüfen im Accessibility Tree / DOM, ob wir BEREITS eingeloggt sind.
    # Ein Login ist nicht nötig, wenn ein Logout-Button oder die Mailbox-Verwaltung existiert.
    is_logged_in = await t.evaluate("""(() => {
        const text = document.body.innerText.toLowerCase();
        return text.includes('logout') || text.includes('mailboxes');
    })()""")

    if is_logged_in:
        print("M05 VERIFIZIERT: User ist bereits in Temp-Mail Premium eingeloggt. Überspringe Login-Sequenz.")
        return True

    print("M05: User ist NICHT eingeloggt. Starte Keyboard-Eskalation...")
    
    # 1. 6x Tab + Space (Fokussiert Login)
    for _ in range(6): await press(t, "Tab", 9)
    await press(t, " ", 32)
    await asyncio.sleep(2)

    # DOM VERIFIKATION NACH DEM KLICK
    is_login_modal = await t.evaluate("document.body.innerText.toLowerCase().includes('log in')")
    if not is_login_modal:
        print("M05 FEHLER: Login-Modal nicht erschienen nach 6x Tab + Space! DOM-Status falsch.")
        return False

    # 2. 1x Tab + Enter (Geht zum Email-Feld)
    await press(t, "Tab", 9)
    await press(t, "Enter", 13)
    await asyncio.sleep(2)

    # 3. 2x Tab + Email eingeben
    for _ in range(2): await press(t, "Tab", 9)
    
    print("M05: (Keyboard) Tippe Email...")
    # Da wir in diesem Skript keine Credentials haben, vertrauen wir auf Autofill 
    # des Default-Profils (falls vorhanden), oder wir müssten sie hier injecten.
    # Der User ist aber ohnehin im Default-Profil meistens schon eingeloggt.
    
    # 4. 1x Tab + Passwort
    await press(t, "Tab", 9)

    # 5. 2x Tab + Enter
    for _ in range(2): await press(t, "Tab", 9)
    await press(t, "Enter", 13)
    
    await asyncio.sleep(4)
    # DOM VERIFIKATION NACH LOGIN
    is_logged_in_after = await t.evaluate("""(() => {
        const text = document.body.innerText.toLowerCase();
        return text.includes('logout') || text.includes('mailboxes');
    })()""")
    
    if is_logged_in_after:
        print("M05 OK: Keyboard Sequenz beendet und Login verifiziert.")
        return True
    else:
        print("M05 FEHLER: Login nach Keyboard-Sequenz fehlgeschlagen!")
        return False

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
