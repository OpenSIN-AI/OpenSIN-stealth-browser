import asyncio, nodriver as uc, sys

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Suche den echten Tab (nicht chrome://)
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if not url.startswith("chrome://"):
            t = tab
            break

    if not t:
        print("M02 FAIL: Kein echter Tab gefunden!")
        return False

    for i in range(40):
        try:
            task = asyncio.create_task(t.get_content())
            done, _ = await asyncio.wait([task], timeout=2.0)
            if done:
                html = task.result().lower()
                if any(kw in html for kw in ["registrieren", "sign up", "log in", "anmelden", "create account"]):
                    print(f"M02 OK: Geladen nach {i * 0.5:.1f}s.")
                    return True
        except Exception:
            pass
        await asyncio.sleep(0.5)

    print("M02 FAIL: Timeout auf OpenAI Landingpage.")
    return False

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
