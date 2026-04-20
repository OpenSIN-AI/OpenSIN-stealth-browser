import asyncio, nodriver as uc, sys, random, string
import nodriver.cdp.input_ as input_cdp

def _pwd():
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=12)) + "!2aA"

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Find OpenAI tab - URL could be /create-account or /create-account/password
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "openai.com" in url or "chatgpt.com" in url:
            t = tab
            break
    if not t:
        print("M16 FAIL: Kein OpenAI Tab!")
        return False

    # WAIT up to 10s for the password field to appear (React SPA)
    password_found = False
    for i in range(20):
        found = await t.evaluate("""
            (function(){
                var inp = document.querySelector('input[type="password"]');
                if(inp && inp.offsetParent !== null) {
                    inp.focus();
                    inp.click();
                    return true;
                }
                return false;
            })()
        """)
        if found:
            password_found = True
            print(f"M16 INFO: Password-Feld gefunden nach {i * 0.5:.1f}s")
            break
        await asyncio.sleep(0.5)

    if not password_found:
        print("M16 FAIL: Password-Feld nicht gefunden nach 10s!")
        return False

    await asyncio.sleep(0.3)

    pwd = _pwd()
    with open("/tmp/current_password.txt", "w") as f:
        f.write(pwd)

    # Clear and type
    await t.evaluate("""
        (function(){
            var inp = document.querySelector('input[type="password"]');
            if(inp) {
                var setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
                setter.call(inp, "");
                inp.dispatchEvent(new Event("input", {bubbles:true}));
            }
        })()
    """)
    await asyncio.sleep(0.1)

    for char in pwd:
        await t.send(input_cdp.dispatch_key_event(type_="char", text=char))
        await asyncio.sleep(0.04)

    print("M16 OK: Password getippt + gespeichert.")
    return True

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
