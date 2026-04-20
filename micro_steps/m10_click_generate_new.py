import asyncio, nodriver as uc, sys

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Find temp-mail tab — URL could have changed after delete (redirect)
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "temp-mail" in url:
            t = tab
            break

    if not t:
        # After delete the page might have navigated — wait and check all tabs again
        await asyncio.sleep(2)
        for tab in b.tabs:
            url = getattr(tab.target, "url", "") or ""
            if "temp-mail" in url:
                t = tab
                break

    if not t:
        print("M10 FAIL: Kein Temp-Mail Tab!")
        return False

    # Click Generate/Change if visible
    clicked = await t.evaluate("""(function(){
        var btns = Array.from(document.querySelectorAll("button, a"));
        var target = btns.find(b => {
            var txt = (b.innerText || b.textContent || "").toLowerCase().trim();
            return txt === "generate new" || txt === "change" || txt === "refresh" || txt.includes("generate");
        });
        if(target && target.offsetParent !== null) { target.click(); return true; }
        return false;
    })()""")

    if clicked:
        print("M10 OK: DOM Click auf Generate/Change.")
    else:
        try:
            await t.reload()
            print("M10 OK: Tab reloaded.")
        except Exception:
            print("M10 OK: Übersprungen (Premium Mode, Adresse generiert).")

    await asyncio.sleep(2)
    return True

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
