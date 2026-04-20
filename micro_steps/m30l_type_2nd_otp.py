import asyncio, nodriver as uc, sys, os
import nodriver.cdp.input_ as input_cdp


async def run():
    otp_needed = (
        open("/tmp/m30_otp_needed.txt").read().strip()
        if os.path.exists("/tmp/m30_otp_needed.txt")
        else "0"
    )
    if otp_needed != "1":
        print("M30l SKIP: Kein 2. OTP noetig.")
        return True
    b = await uc.start(host="127.0.0.1", port=9334)
    # Bevorzuge den Verification-Tab statt des alten Login-Tabs
    t = next(
        (
            tab
            for tab in b.tabs
            if "email-verification"
            in getattr(tab, "url", getattr(tab.target, "url", ""))
        ),
        None,
    )
    if not t:
        t = next(
            (
                tab
                for tab in b.tabs
                if "auth.openai" in getattr(tab, "url", getattr(tab.target, "url", ""))
            ),
            None,
        )
    if not t:
        print("M30l FAIL: Kein passender OpenAI Tab.")
        return False

    await t.bring_to_front()
    with open("/tmp/current_otp2.txt", "r") as f:
        otp = f.read().strip()
    await t.evaluate(
        "var inp = document.querySelector('input'); if(inp) { inp.value=''; inp.focus(); }"
    )
    await asyncio.sleep(0.5)
    for char in otp:
        await t.send(input_cdp.dispatch_key_event(type_="char", text=char))
        await asyncio.sleep(0.1)
    print(f"M30l OK: 2. OTP {otp} getippt.")
    await asyncio.sleep(1)
    await t.evaluate("""(function(){
        var btn = document.querySelector('button[type="submit"]');
        if(btn && !btn.disabled) btn.click();
    })()""")
    print("M30l OK: Weiter geklickt.")
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
