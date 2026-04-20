import asyncio, nodriver as uc, sys

# Klickt alle bekannten Onboarding-Buttons weg inkl. "Überspringen", "Ok, los geht's" etc.
_CLICK_POPUP = """(function(){
    var btns = Array.from(document.querySelectorAll('button, a'));
    
    // PRIORITAET 1: "Tour überspringen" oder "Skip tour" zuerst!
    var skipBtn = btns.find(b => {
        var t = (b.innerText || '').trim().toLowerCase();
        return t.includes('überspringen') || t.includes('tour') || t.includes('skip');
    });
    if(skipBtn && skipBtn.offsetParent !== null) {
        skipBtn.click();
        return 'skip';
    }
    
    // PRIORITAET 2: Abschluss-Buttons ("Du bist jetzt startklar" -> "Weiter", "Ok, los geht's" etc.)
    var doneBtn = btns.find(b => {
        var t = (b.innerText || '').trim().toLowerCase();
        return t === 'ok' || t === 'fertig' || t === 'done' || t === 'got it'
            || t === 'weiter' || t === 'next'
            || t.includes('los geht') || t.includes('get started') || t.includes('startklar');
    });
    if(doneBtn && doneBtn.offsetParent !== null) {
        doneBtn.click();
        return 'done';
    }
    return false;
})()"""


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Nimm den LETZTEN chatgpt.com Tab (der von m28a neu geoeffnete)
    chatgpt_tabs = [
        tab for tab in b.tabs if "chatgpt.com" in getattr(tab.target, "url", "")
    ]
    t = chatgpt_tabs[-1] if chatgpt_tabs else None
    if not t:
        print("M28b WARN: Kein chatgpt.com Tab gefunden!")
        return True

    await t.bring_to_front()

    # Zuerst Chrome "Seiten wiederherstellen?" Popup per ESC wegschicken
    import nodriver.cdp.input_ as input_cdp

    await t.send(
        input_cdp.dispatch_key_event(
            type_="keyDown", key="Escape", code="Escape", windows_virtual_key_code=27
        )
    )
    await t.send(
        input_cdp.dispatch_key_event(
            type_="keyUp", key="Escape", code="Escape", windows_virtual_key_code=27
        )
    )
    await asyncio.sleep(1)

    print("M28b: Warte auf Onboarding-Popups...")
    for i in range(20):  # bis zu 10 Sekunden
        if await t.evaluate(_CLICK_POPUP):
            print("M28b OK: Onboarding Popup weggeklickt.")
            await asyncio.sleep(0.7)
        else:
            await asyncio.sleep(0.5)

    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
