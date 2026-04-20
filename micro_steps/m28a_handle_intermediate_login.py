import asyncio, nodriver as uc, sys
import nodriver.cdp.input_ as input_cdp

_CLICK_CONTINUE = """(function(){
    var btn = document.querySelector('button[type="submit"], button[name="action"][value="default"]');
    if(btn && btn.offsetParent !== null) { btn.click(); return true; }
    return false;
})()"""


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    print("M28a: Warte 4s damit OpenAI seinen Redirect abschliesst...")
    await asyncio.sleep(4)

    # SCHLIESSE alle alten kaputten auth.openai.com/log-in Tabs — die sind wertloser Muell!
    for tab in list(b.tabs):
        tab_url = getattr(tab.target, "url", "") or ""
        if "auth.openai.com" in tab_url or "/log-in" in tab_url:
            print(f"M28a: Schliesse kaputten Tab: {tab_url[:60]}")
            try:
                await tab.close()
            except:
                pass
    await asyncio.sleep(1)

    # Oeffne NEUEN Tab mit chatgpt.com
    print("M28a: Oeffne NEUEN Tab mit https://chatgpt.com ...")
    new_tab = await b.get("https://chatgpt.com", new_tab=True)
    await asyncio.sleep(5)

    url = getattr(new_tab.target, "url", "") or ""
    print(f"M28a: Neuer Tab URL: {url}")

    # Sind wir direkt eingeloggt? Dann fertig!
    if "chatgpt.com" in url and "/auth" not in url and "/log-in" not in url:
        print("M28a OK: Bereits eingeloggt auf chatgpt.com!")
        return True

    # Sonst: Login-Formular ausfuellen
    print("M28a: Login Formular erkannt. Lade credentials...")
    try:
        with open("/tmp/current_email.txt", "r") as f:
            email = f.read().strip()
        with open("/tmp/current_password.txt", "r") as f:
            pwd = f.read().strip()
    except:
        print("M28a FAIL: Konnte email/password nicht lesen.")
        return False

    print(f"M28a: Logge ein mit {email}")

    # 1. E-Mail eintippen
    await new_tab.evaluate("""(function(){
        var inp = document.querySelector('input[type="email"], input[name="username"]');
        if(inp) { inp.focus(); inp.click(); }
    })()""")
    await asyncio.sleep(0.5)
    for char in email:
        await new_tab.send(input_cdp.dispatch_key_event(type_="char", text=char))
        await asyncio.sleep(0.02)

    # 2. Weiter klicken
    await new_tab.evaluate(_CLICK_CONTINUE)
    await asyncio.sleep(3)

    # 3. Passwort eintippen
    print("M28a: Tippe Passwort...")
    await new_tab.evaluate("""(function(){
        var inp = document.querySelector('input[type="password"]');
        if(inp) { inp.focus(); inp.click(); }
    })()""")
    await asyncio.sleep(0.5)
    for char in pwd:
        await new_tab.send(input_cdp.dispatch_key_event(type_="char", text=char))
        await asyncio.sleep(0.02)

    # 4. Submit
    await new_tab.evaluate(_CLICK_CONTINUE)
    print("M28a OK: Login abgeschickt. Warte auf ChatGPT Ladevorgang...")
    await asyncio.sleep(6)
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
