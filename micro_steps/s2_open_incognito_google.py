import nodriver as uc
import asyncio
import os
import json
import urllib.request


LOGIN_URL = "https://chatgpt.com/auth/login?openaicom_referred=true"


def _find_chatgpt_tab_http():
    try:
        resp = urllib.request.urlopen("http://127.0.0.1:9334/json/list", timeout=2)
        tabs = json.loads(resp.read())
        for tab in tabs:
            url = tab.get("url", "")
            typ = tab.get("type", "")
            if "chatgpt.com" in url and typ == "page":
                return tab.get("id"), url
    except Exception:
        pass
    return None, None


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    tab_id, tab_url = _find_chatgpt_tab_http()
    if tab_id and LOGIN_URL in tab_url:
        print(f"S2: ChatGPT login tab already open: {tab_url[:60]}")
        with open("/tmp/incognito_tab_id.txt", "w") as f:
            f.write(tab_id)
        return True

    print(f"S2: Opening incognito window with {LOGIN_URL} via AppleScript...")
    script = (
        'osascript -e \'tell application "Google Chrome"\n'
        'set newWin to make new window with properties {mode:"incognito"}\n'
        f'set URL of active tab of newWin to "{LOGIN_URL}"\n'
        "end tell'"
    )
    ret = os.system(script)
    print(f"S2: AppleScript returned {ret}")

    for i in range(15):
        await asyncio.sleep(2)
        tab_id, tab_url = _find_chatgpt_tab_http()
        if tab_id and "chatgpt.com" in (tab_url or ""):
            print(f"S2 OK: Incognito tab found after {(i + 1) * 2}s: {tab_url[:60]}")
            with open("/tmp/incognito_tab_id.txt", "w") as f:
                f.write(tab_id)
            return True

    print("S2 FAIL: Incognito chatgpt.com tab not found after 30s")
    return False


if __name__ == "__main__":
    asyncio.run(run())
