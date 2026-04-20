import asyncio, nodriver as uc, sys

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Find real tab
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if not url.startswith("chrome://"):
            t = tab
            break
    if not t and b.tabs:
        t = b.tabs[-1]  # take last tab as fallback
    if not t:
        print("M04 FAIL: Kein Tab!")
        return False

    for i in range(20):
        try:
            url = getattr(t.target, "url", "") or ""
            task = asyncio.create_task(t.get_content())
            done, _ = await asyncio.wait([task], timeout=2.0)
            page_text = ""
            if done:
                page_text = task.result().lower()

            # Accept any OpenAI registration-like page
            if any(kw in url for kw in ["create-account", "signup", "register", "email"]):
                print(f"M04 OK: Create Account geladen nach {i * 0.5:.1f}s (URL match).")
                return True
            if any(kw in page_text for kw in ["e-mail-adresse", "email address", "create account",
                                               "konto erstellen", "your email", "deine e-mail"]):
                print(f"M04 OK: Create Account geladen nach {i * 0.5:.1f}s.")
                return True
        except Exception:
            pass
        await asyncio.sleep(0.5)

    print("M04 FAIL: Registrierungsseite nicht geladen!")
    return False

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
