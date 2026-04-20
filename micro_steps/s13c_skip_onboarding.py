import nodriver as uc
import asyncio


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    t = None
    for tab in b.tabs:
        tab_url = getattr(tab.target, "url", "") or ""
        if "chatgpt.com" in tab_url:
            t = tab
            break

    if not t:
        print(
            "S13c SKIP: Kein chatgpt.com Tab gefunden (Onboarding evtl. nicht angezeigt)"
        )
        return True

    await t.bring_to_front()
    print("S13c: Handling post-login onboarding popups...")

    for i in range(4):
        clicked_text = await t.evaluate("""
            (function(){
                var btns = Array.from(document.querySelectorAll('button, a, [role="button"]'));
                
                var skip = btns.find(b => {
                    var txt = (b.innerText || b.textContent || "").toLowerCase().trim();
                    return txt.includes("überspringen") || txt.includes("skip");
                });
                if (skip) { skip.click(); return skip.innerText.trim(); }
                
                var done = btns.find(b => {
                    var txt = (b.innerText || b.textContent || "").toLowerCase().trim();
                    return txt.includes("fertig") || txt.includes("done") || 
                           txt.includes("ok") || txt.includes("los geht");
                });
                if (done) { done.click(); return done.innerText.trim(); }
                
                var cont = btns.find(b => {
                    var txt = (b.innerText || b.textContent || "").toLowerCase().trim();
                    return txt === "weiter" || txt === "continue";
                });
                if (cont) { cont.click(); return cont.innerText.trim(); }
                
                return null;
            })()
        """)

        if clicked_text:
            print(f"S13c OK: Clicked '{clicked_text}'")
            await asyncio.sleep(2)
        else:
            await asyncio.sleep(1)

    print("S13c OK: Onboarding modals cleared")
    return True


if __name__ == "__main__":
    asyncio.run(run())
