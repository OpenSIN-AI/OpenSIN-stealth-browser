import asyncio, nodriver as uc, sys

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Find OpenAI tab (create-account or auth.openai.com)
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "openai.com" in url or "chatgpt.com" in url:
            t = tab
            break
    if not t:
        print("M15 FAIL: Kein OpenAI Tab gefunden!")
        return False

    for i in range(30):
        try:
            task = asyncio.create_task(t.get_content())
            done, _ = await asyncio.wait([task], timeout=2.0)
            if done:
                html = task.result()
                html_l = html.lower()
                url = getattr(t.target, "url", "") or ""

                if any(kw in html_l for kw in ["passwort", "password", "wähle ein", "choose a"]):
                    print(f"M15 OK: Password Seite sichtbar nach {i * 0.5:.1f}s.")
                    return True

                # OpenAI might show email verification inline — that's also OK (go on)
                if "verification" in url or "verify" in url:
                    print(f"M15 OK: Verification Seite (skip password step) nach {i * 0.5:.1f}s.")
                    return True

                # Could be that already on password page but waiting for input
                if "input" in html_l and "type" in html_l:
                    inputs = await t.evaluate("Array.from(document.querySelectorAll('input')).map(i=>i.type+':'+i.name)")
                    print(f"M15 INFO: Inputs on page: {inputs}")
                    if "password" in str(inputs).lower():
                        print(f"M15 OK: Password Input nach {i * 0.5:.1f}s.")
                        return True
        except Exception:
            pass

        if i % 4 == 0:
            print(f"M15 WARN: Warte auf Password Seite... ({i * 0.5:.1f}s)")
        await asyncio.sleep(0.5)

    print("M15 FAIL: Timeout.")
    return False

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
