import nodriver as uc
import asyncio
import sys


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    t = None
    for tab in b.tabs:
        if "openai.com" in tab.url:
            t = tab
            break
    if not t:
        print("S5 FAIL: No OpenAI tab found")
        return False

    await t.bring_to_front()

    # Handle OpenAI Cookie Consent
    try:
        await t.evaluate("""(function(){
            var btns = Array.from(document.querySelectorAll("button"));
            var accept = btns.find(b => {
                var txt = (b.innerText || b.textContent || "").toLowerCase();
                return txt.includes("alle akzeptieren") || txt.includes("accept all") || txt.includes("allow all");
            });
            if(accept) accept.click();
        })()""")
        await asyncio.sleep(2)
    except:
        pass

    # Reload with Cmd+R (dispatch_key_event)
    # Cmd is modifier 8 (Command/Meta)
    await t.send(
        uc.cdp.input_.dispatch_key_event(
            type_="keyDown",
            key="r",
            code="KeyR",
            windows_virtual_key_code=82,
            modifiers=8,
        )
    )
    await t.send(
        uc.cdp.input_.dispatch_key_event(
            type_="keyUp",
            key="r",
            code="KeyR",
            windows_virtual_key_code=82,
            modifiers=8,
        )
    )

    print("S5 OK: Reloaded")
    await asyncio.sleep(5)

    # 15 times Tab
    for i in range(15):
        await t.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyDown", key="Tab", windows_virtual_key_code=9
            )
        )
        await t.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyUp", key="Tab", windows_virtual_key_code=9
            )
        )
        await asyncio.sleep(0.1)

    # 1 time Enter
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

    print("S7 OK: 15x Tab + Enter")
    await asyncio.sleep(3)

    # Click on "ChatGPT"
    # User said mouse click. We can try evaluate click first as it is more reliable for specific text.
    clicked = await t.evaluate("""(function(){
        var links = Array.from(document.querySelectorAll("a, button, [role='button']"));
        var target = links.find(l => (l.innerText || l.textContent || "").toLowerCase().includes("chatgpt"));
        if(target) { target.click(); return true; }
        return false;
    })()""")

    if not clicked:
        print("S8 FAIL: ChatGPT button not clicked via DOM")
        # Fallback to mouse click via search
        try:
            target = await t.select('a:contains("ChatGPT"), button:contains("ChatGPT")')
            if target:
                await target.click()
                clicked = True
        except:
            pass

    if clicked:
        print("S8 OK: Clicked ChatGPT")
    else:
        print("S8 WARN: ChatGPT click might have failed, proceeding with tabs anyway")

    await asyncio.sleep(5)

    # 19 times Tab
    for i in range(19):
        await t.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyDown", key="Tab", windows_virtual_key_code=9
            )
        )
        await t.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyUp", key="Tab", windows_virtual_key_code=9
            )
        )
        await asyncio.sleep(0.1)

    # 1 time Enter
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

    print("S10 OK: 19x Tab + Enter (Signup target)")
    await asyncio.sleep(5)
    return True


if __name__ == "__main__":
    asyncio.run(run())
