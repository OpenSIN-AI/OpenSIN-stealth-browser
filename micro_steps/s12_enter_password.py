import nodriver as uc
import asyncio
import os
import random
import string
import nodriver.cdp.input_ as inp


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

    t = next(
        (
            tab
            for tab in b.tabs
            if "auth.openai.com" in (getattr(tab.target, "url", "") or "")
            or "chatgpt.com" in (getattr(tab.target, "url", "") or "")
        ),
        None,
    )

    if not t:
        if os.path.exists("/tmp/incognito_tab_id.txt"):
            with open("/tmp/incognito_tab_id.txt") as f:
                saved_id = f.read().strip()
            for tab in b.tabs:
                if str(getattr(tab.target, "target_id", "")) == saved_id:
                    t = tab
                    break

    if not t:
        print("S12 FAIL: No auth.openai.com or chatgpt.com tab found")
        return False

    await t.bring_to_front()
    await asyncio.sleep(5)

    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = "".join(random.choice(chars) for _ in range(16)) + "A1!"
    with open("/tmp/current_password.txt", "w") as f:
        f.write(password)

    print("S12: Waiting for password input to appear...")
    focused = False
    for _ in range(15):
        focused = await t.evaluate("""(function(){
            var pwd = document.querySelector('input[type="password"]');
            if(pwd) { pwd.focus(); return true; }
            return false;
        })()""")
        if focused:
            break
        await asyncio.sleep(1)

    if not focused:
        print("S12 FAIL: 'input[type=\"password\"]' not found! Page did not advance.")
        await t.save_screenshot("/tmp/fail_s12_no_password_field.png")
        os.system("open /tmp/fail_s12_no_password_field.png")
        return False

    print("S12: Entering password via CDP...")
    for ch in password:
        kc = ord(ch) if ord(ch) < 128 else 0
        if ch == ".":
            kc = 190
        elif ch == "@":
            kc = 50
        elif ch == "!":
            kc = 49
        elif ch == "#":
            kc = 51
        elif ch == "$":
            kc = 52
        elif ch == "%":
            kc = 53
        elif ch == "^":
            kc = 54
        elif ch == "&":
            kc = 55
        elif ch == "*":
            kc = 56

        await t.send(
            inp.dispatch_key_event(
                type_="keyDown", key=ch, text=ch, windows_virtual_key_code=kc
            )
        )
        await asyncio.sleep(0.04)
        await t.send(
            inp.dispatch_key_event(
                type_="keyUp", key=ch, text=ch, windows_virtual_key_code=kc
            )
        )
        await asyncio.sleep(0.04)

    await asyncio.sleep(1)

    print("S12: Pressing Enter...")
    await _key(t, "Enter", "Enter", 13)
    await asyncio.sleep(6)

    print("S12 OK: Password submitted")
    return True


if __name__ == "__main__":
    asyncio.run(run())
