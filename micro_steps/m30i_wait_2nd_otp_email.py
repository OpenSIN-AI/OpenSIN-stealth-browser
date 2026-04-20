import asyncio, nodriver as uc, sys, os

_CLICK_TOP = """(function(){
    var items = Array.from(document.querySelectorAll('a.title-subject, div.subject, td > a, a.viewLink'));
    var otp = items.find(function(el){
        var t = (el.innerText || '').toLowerCase();
        return (t.includes('code') || t.includes('verify') || t.includes('chatgpt')) && el.offsetParent !== null;
    });
    if(otp){ (otp.closest('a') || otp).click(); return true; }
    return false;
})()"""

_GET_CODE = """(function(){
    var v = document.querySelector('.inbox-data-content') || document.body;
    var m = v.innerText.match(/([0-9]{6})/);
    return m ? m[1] : null;
})()"""


async def run():
    if (
        not os.path.exists("/tmp/m30_otp_needed.txt")
        or open("/tmp/m30_otp_needed.txt").read().strip() != "1"
    ):
        print("M30i SKIP")
        return True
    old = (
        open("/tmp/current_otp.txt").read().strip()
        if os.path.exists("/tmp/current_otp.txt")
        else ""
    )
    print(f"M30i: 1. OTP={old}. Suche NEUEN Code...")
    b = await uc.start(host="127.0.0.1", port=9334)
    t = next(
        (
            tab
            for tab in b.tabs
            if "temp-mail" in getattr(tab, "url", getattr(tab.target, "url", ""))
        ),
        None,
    )
    if not t:
        print("M30i FAIL: Kein Temp-Mail Tab.")
        return False
    # CRITICAL FIX: Reload inbox to force fresh email list (kills cached old email view)
    await t.get("https://temp-mail.org/en/")
    await asyncio.sleep(3)
    for i in range(60):
        if await t.evaluate(_CLICK_TOP):
            await asyncio.sleep(1.5)
            code = await t.evaluate(_GET_CODE)
            if code and code != old:
                open("/tmp/current_otp2.txt", "w").write(code)
                print(f"M30i OK: 2. OTP={code} nach {i}s")
                return True
            # Same old code or no code found — back to inbox, wait for new email
            print(f"M30i: Code={code} ist alt/leer, zurueck zur Inbox...")
            await t.get("https://temp-mail.org/en/")
            await asyncio.sleep(3)
        else:
            await asyncio.sleep(1)
    print("M30i FAIL: Timeout auf 2. OTP Email.")
    return False


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
