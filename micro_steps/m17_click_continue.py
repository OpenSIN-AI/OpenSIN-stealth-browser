import asyncio, nodriver as uc, sys
import nodriver.cdp.input_ as input_cdp

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None
    
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "openai.com" in url or "chatgpt.com" in url:
            t = tab
            break
    if not t:
        return False

    print("M17: Kurze Gedenksekunde...")
    await asyncio.sleep(1.5)  # Give React time to process password input
    
    # First try: click the submit button
    clicked = await t.evaluate("""(function(){
        var btn = document.querySelector('button[type="submit"]');
        if(btn && !btn.disabled) { btn.click(); return "submit_click"; }
        return null;
    })()""")
    
    if not clicked:
        # Fallback: press Enter in the password field
        await t.evaluate("document.querySelector('input[type=\"password\"]')?.focus()")
        await asyncio.sleep(0.2)
        await t.send(input_cdp.dispatch_key_event(type_="keyDown", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
        await t.send(input_cdp.dispatch_key_event(type_="keyUp", key="Enter", windows_virtual_key_code=13, native_virtual_key_code=13))
        clicked = "enter_key"
    
    print(f"M17 OK: Weiter geklickt ({clicked}).")
    return True

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
