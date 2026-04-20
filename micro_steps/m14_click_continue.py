import asyncio, nodriver as uc, sys


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    t = next(
        (
            tab
            for tab in b.tabs
            if "create-account" in getattr(tab, "url", getattr(tab.target, "url", ""))
        ),
        None,
    )
    if not t:
        return False

    print("M14: Kurze Gedenksekunde...")
    await asyncio.sleep(1.0)  # Reduziertes Anti-Bot Delay
    await t.evaluate("""(function(){
        var btn = document.querySelector('button[type="submit"]');
        if(btn) btn.click();
    })()""")
    print("M14 OK: Weiter geklickt.")
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
