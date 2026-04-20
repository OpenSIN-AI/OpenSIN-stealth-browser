import asyncio, nodriver as uc, sys

_CLICK = """(function(){
    var btn = document.querySelector('button[type="submit"]');
    if(btn && !btn.disabled) { btn.click(); return true; }
    return false;
})()"""


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    t = next(
        (
            tab
            for tab in b.tabs
            if "about-you" in getattr(tab.target, "url", "")
            or "openai.com" in getattr(tab.target, "url", "")
            or "chatgpt.com" in getattr(tab.target, "url", "")
        ),
        None,
    )
    if not t:
        return False

    if await t.evaluate(_CLICK):
        print("M28 OK: Submit 'Kontoerstellung abschliessen'.")
        await t.save_screenshot("/tmp/m28_submitted.png")
        return True

    print("M28 FAIL: Button nicht klickbar!")
    return False


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
