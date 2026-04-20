import asyncio, nodriver as uc, sys

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Tab 0 kann chrome://profile-picker oder chrome://omnibox-popup sein —
    # immer einen sauberen neuen Tab öffnen damit wir einen echten Browser-Kontext haben.
    real_tab = None
    for t in b.tabs:
        url = getattr(t.target, "url", "") or ""
        if not url.startswith("chrome://"):
            real_tab = t
            break

    if real_tab is None:
        # Alle Tabs sind interne Chrome-Seiten → neuen echten Tab öffnen
        real_tab = await b.get("about:blank", new_tab=True)
        await asyncio.sleep(1)

    # Echten Tab navigieren (create_task damit Cloudflare das Load-Event nicht blockiert)
    asyncio.create_task(real_tab.get("https://chatgpt.com/auth/login_with"))
    print("M01: Seite https://chatgpt.com/auth/login_with im Haupt-Tab aufgerufen.")
    return True

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
