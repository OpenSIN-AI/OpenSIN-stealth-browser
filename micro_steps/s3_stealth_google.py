import nodriver as uc
import asyncio
import os


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    ctx_id = None
    if os.path.exists("/tmp/incognito_ctx_id.txt"):
        with open("/tmp/incognito_ctx_id.txt") as f:
            ctx_id = f.read().strip() or None

    t = None
    if ctx_id:
        all_targets = await b.connection.send(uc.cdp.target.get_targets())
        for tgt in all_targets:
            tgt_ctx = getattr(tgt, "browser_context_id", None)
            tgt_url = getattr(tgt, "url", "") or ""
            if str(tgt_ctx) == str(ctx_id) and "google.com" in tgt_url:
                for tab in b.tabs:
                    if getattr(tab.target, "target_id", None) == tgt.target_id:
                        t = tab
                        break
                if t:
                    break

    if not t:
        print("S3 FAIL: Kein Inkognito Google-Tab gefunden")
        print(f"  ctx_id={ctx_id}")
        for tab in b.tabs:
            print(f"  Tab: {getattr(tab.target, 'url', '?')[:80]}")
        return False

    await t.bring_to_front()
    print(f"S3: Inkognito Google-Tab gefunden: {getattr(t.target, 'url', '')[:60]}")

    try:
        await t.evaluate("""(function(){
            var btns = Array.from(document.querySelectorAll("button"));
            var accept = btns.find(b => {
                var txt = (b.innerText || b.textContent || "").toLowerCase();
                return txt.includes("alle akzeptieren") || txt.includes("accept all") || txt.includes("zustimmen");
            });
            if(accept) accept.click();
        })()""")
        await asyncio.sleep(2)
    except Exception:
        pass

    search_input = await t.select('textarea[name="q"], input[name="q"]')
    await search_input.send_keys("openai")
    await asyncio.sleep(0.5)

    await t.send(
        uc.cdp.input_.dispatch_key_event(
            type_="keyDown", key="Enter", windows_virtual_key_code=13
        )
    )
    await t.send(
        uc.cdp.input_.dispatch_key_event(
            type_="keyUp", key="Enter", windows_virtual_key_code=13
        )
    )
    await asyncio.sleep(4)

    clicked = await t.evaluate("""(function(){
        var links = Array.from(document.querySelectorAll("a"));
        var target = links.find(l => {
            var href = l.href || "";
            return href === "https://openai.com/" || href === "https://openai.com/de-DE" || href === "https://openai.com/de-DE/";
        });
        if(target) {
            target.removeAttribute("target");
            target.click();
            return true;
        }
        return false;
    })()""")

    await asyncio.sleep(5)
    return clicked


if __name__ == "__main__":
    asyncio.run(run())
