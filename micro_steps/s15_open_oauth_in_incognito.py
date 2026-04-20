import asyncio
import nodriver as uc
import sys
import os
import re

FALLBACK_URL = (
    "https://auth.openai.com/authorize?"
    "response_type=code&"
    "client_id=app_EMoamEEZ73f0CkXaXp7hrann&"
    "redirect_uri=http%3A%2F%2Flocalhost%3A1455%2Fauth%2Fcallback&"
    "scope=openid+profile+email+offline_access&"
    "codex_cli_simplified_flow=true"
)


async def extract_url_from_log():
    for _ in range(30):
        if os.path.exists("/tmp/opencode_auth.log"):
            with open("/tmp/opencode_auth.log", "r", errors="ignore") as f:
                content = f.read()
                m = re.search(r"(https://auth\.openai\.com[^\s\x1b]+)", content)
                if m:
                    return m.group(1)
        await asyncio.sleep(0.5)
    print("S15 WARN: Keine OAuth URL im Log gefunden, nutze Fallback URL")
    return FALLBACK_URL


async def run():
    print("S15: Warte auf OAuth URL aus opencode auth login...")
    url = await extract_url_from_log()
    print(f"S15: OAuth URL: {url[:80]}...")

    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    ctx_id = None
    if os.path.exists("/tmp/incognito_ctx_id.txt"):
        with open("/tmp/incognito_ctx_id.txt") as f:
            ctx_id = f.read().strip() or None

    if ctx_id:
        print(f"S15: Oeffne OAuth via CDP create_target in ctx {ctx_id[:16]}...")
        await b.connection.send(
            uc.cdp.target.create_target(url, browser_context_id=ctx_id)
        )
        print("S15: OAuth Tab via CDP geoeffnet")
        await asyncio.sleep(3)
    else:
        incognito_tab = None
        for tab in b.tabs:
            tab_url = getattr(tab.target, "url", "") or ""
            if "chatgpt.com" in tab_url or "openai.com" in tab_url:
                incognito_tab = tab
                break

        if not incognito_tab:
            print("S15 FAIL: Kein Inkognito-Tab und keine ctx_id gefunden!")
            for tab in b.tabs:
                tab_url = getattr(tab.target, "url", "") or ""
                print(f"  - {tab_url[:100]}")
            return False

        await incognito_tab.bring_to_front()
        await asyncio.sleep(0.5)
        escaped_url = url.replace("\\", "\\\\").replace("'", "\\'")
        await incognito_tab.evaluate(f"window.open('{escaped_url}', '_blank')")
        print("S15: OAuth URL via window.open() geoeffnet")
        await asyncio.sleep(3)

    for attempt in range(15):
        for tab in b.tabs:
            curr = getattr(tab.target, "url", "") or ""

            if "localhost:1455" in curr or "127.0.0.1:1455" in curr:
                print("S15 OK: Direkt Callback! Token bereits gespeichert.")
                with open("/tmp/s_skip_login.txt", "w") as f:
                    f.write("1")
                return True

            if "auth.openai.com" in curr:
                await tab.bring_to_front()
                await asyncio.sleep(1)

                has_auth = await tab.evaluate("""(function(){
                    var btns = document.querySelectorAll('button');
                    return Array.from(btns).some(x =>
                        /authorize|erlauben|allow|zulassen/i.test(x.textContent)
                    );
                })()""")

                if has_auth:
                    print("S15 OK: Direkt auf Authorize-Seite (kein Re-Login noetig).")
                    with open("/tmp/s_skip_login.txt", "w") as f:
                        f.write("1")
                    return True

                if "log-in" in curr or "login" in curr:
                    print(f"S15 OK: Login-Seite erkannt: {curr[:80]}")
                    return True

                print(f"S15: Auth-Seite laedt... (Versuch {attempt + 1}/15)")

        await asyncio.sleep(1)

    print("S15 WARN: Timeout beim Zustandscheck. Versuche trotzdem Re-Login.")
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
