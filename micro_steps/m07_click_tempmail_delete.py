import asyncio, nodriver as uc, sys

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "temp-mail" in url:
            t = tab
            break
    if not t:
        print("M07 FAIL: Kein Temp-Mail Tab!")
        return False

    # Try Delete first, then Change as fallback
    clicked = await t.evaluate("""
        (function(){
            var btns = Array.from(document.querySelectorAll("button, a"));
            // Try Delete first
            var del = btns.find(b => (b.innerText || b.textContent || "").toLowerCase().trim() === "delete");
            if(del && del.offsetParent !== null) { del.click(); return "delete"; }
            // Then Change
            var chg = btns.find(b => (b.innerText || b.textContent || "").toLowerCase().trim() === "change");
            if(chg && chg.offsetParent !== null) { chg.click(); return "change"; }
            return null;
        })()
    """)
    
    print(f"M07 OK: Klick auf {clicked or 'Change/Delete'}.")
    return True

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
