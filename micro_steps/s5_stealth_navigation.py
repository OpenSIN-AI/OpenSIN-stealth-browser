import nodriver as uc
import asyncio
import nodriver.cdp.input_ as inp
import os
import json
import urllib.request

# Reuse the shared polling helper so this step stops waiting as soon as the
# email field is actually rendered instead of burning a fixed 6-second delay.
from micro_steps._wait import wait_for_selector


LOGIN_URL = "https://chatgpt.com/auth/login?openaicom_referred=true"


async def _key(t, key, code, keycode):
    await t.send(
        inp.dispatch_key_event(
            type_="keyDown", key=key, code=code, windows_virtual_key_code=keycode
        )
    )
    await asyncio.sleep(0.05)
    await t.send(
        inp.dispatch_key_event(
            type_="keyUp", key=key, code=code, windows_virtual_key_code=keycode
        )
    )
    await asyncio.sleep(0.08)


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    print(f"S5: Opening incognito window with {LOGIN_URL} via AppleScript...")
    script = (
        "osascript -e 'tell application \"Google Chrome\"\n"
        "set newWin to make new window with properties {mode:\"incognito\"}\n"
        f"set URL of active tab of newWin to \"{LOGIN_URL}\"\n"
        "end tell'"
    )
    os.system(script)

    # The old hard sleep always waited the full duration even when the page was
    # ready much sooner. We now wait for the actual email field that the next
    # step depends on, then keep only a tiny anti-bot pause before interacting.
    print("S5: Polling for email input instead of sleeping for a fixed 6 seconds...")

    tab_id = None
    ws_url = None
    tab_url = ""
    tab_type = ""
    tab_title = ""
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:9334/json/list", timeout=2)
        tabs = json.loads(resp.read())
        for tab in tabs:
            if "chatgpt.com" in tab.get("url", "") and tab.get("type") == "page":
                tab_id = tab.get("id")
                ws_url = tab.get("webSocketDebuggerUrl")
                tab_url = tab.get("url", "")
                tab_type = tab.get("type", "")
                tab_title = tab.get("title", "")
                break
    except Exception as e:
        print(f"S5 HTTP error: {e}")

    if not ws_url:
        print("S5 FAIL: Could not find chatgpt.com tab via HTTP list")
        return False

    import websockets

    try:
        ws = await websockets.connect(ws_url, max_size=2**24)
        t = uc.Tab(
            websocket_url=ws_url,
            target=uc.cdp.target.TargetInfo(
                target_id=uc.cdp.target.TargetID(tab_id),
                type_=tab_type,
                title=tab_title,
                url=tab_url,
                attached=True,
                can_access_opener=False,
            ),
            browser=b,
        )
        b.tabs.append(t)
    except Exception as e:
        print(f"S5 FAIL: WebSocket connect failed: {e}")
        return False

    await t.bring_to_front()
    await asyncio.sleep(2)
    print(f"S5: Tab found and connected: {LOGIN_URL[:70]}")

    # Wait for the real DOM dependency instead of a blind page-load guess. If
    # the selector never appears we still continue, but the log now explains
    # that the timeout came from missing UI state rather than an arbitrary sleep.
    email_ready = await wait_for_selector(t, 'input[type="email"]', timeout=15)
    if email_ready:
        print("S5 OK: Email input detected via DOM polling")
    else:
        print("S5 WARN: Email input not detected within timeout; continuing cautiously")

    # Keep a small human-like pause so timing still looks natural after the DOM
    # condition flips to ready. This preserves the existing anti-bot cadence.
    await asyncio.sleep(0.5)

    await t.evaluate("document.body.focus();")
    await asyncio.sleep(0.5)

    await t.evaluate("""(function(){
        var inp = document.querySelector('input[type="email"], input[name="email"]');
        if(inp) inp.dispatchEvent(new Event('input', { bubbles: true }));
    })()""")
    await asyncio.sleep(0.5)

    print("S5: Suchen und Klicken auf 'Weiter' Button...")
    clicked = await t.evaluate("""(function(){
        var btns = Array.from(document.querySelectorAll("button"));
        var submit = btns.find(b => {
            var txt = (b.innerText || b.textContent || "").toLowerCase().trim();
            return txt === "weiter" || txt === "continue" || txt === "fortsetzen";
        });
        if(submit) {
            submit.removeAttribute("disabled");
            submit.click();
            return true;
        }
        return false;
    })()""")

    if not clicked:
        print("S5: 'Weiter' Button nicht gefunden. Fallback zu Enter-Taste...")
        await _key(t, "Enter", "Enter", 13)

    await asyncio.sleep(6)

    await t.save_screenshot("/tmp/s5_after_email.png")
    print("S5 OK: screenshot -> /tmp/s5_after_email.png")
    return True


if __name__ == "__main__":
    asyncio.run(run())
