import asyncio, nodriver as uc, sys, os, re

F = "https://auth.openai.com/authorize?response_type=code&client_id=app_EMoamEEZ73f0CkXaXp7hrann&redirect_uri=http%3A%2F%2Flocalhost%3A1455%2Fauth%2Fcallback&scope=openid+profile+email+offline_access&codex_cli_simplified_flow=true"

async def extract_url_from_log():
    for _ in range(30):
        if os.path.exists("/tmp/opencode_auth.log"):
            with open("/tmp/opencode_auth.log", "r", errors="ignore") as f:
                content = f.read()
                m = re.search(r"(https://auth\.openai\.com[^\s\x1b]+)", content)
                if m:
                    return m.group(1)
        await asyncio.sleep(0.5)
    return F

async def run():
    print("M30a: Warte auf OAuth URL aus Hintergrund-Prozess...")
    url = await extract_url_from_log()
    print(f"M30a OK: URL gefunden: {url[:60]}...")

    b = await uc.start(host="127.0.0.1", port=9334)

    # KRITISCHER FIX (Issue #55 / WebSocket 404): 
    # Wir öffnen ZUERST den neuen Tab! 
    # Wenn wir vorher alle anderen Tabs schließen, schließt sich das Chrome-Fenster
    # komplett und die WebSocket-Verbindung stirbt (Error 404).
    print("M30a: Oeffne OAuth URL in neuem Tab...")
    new_t = await b.get(url, new_tab=True)
    await asyncio.sleep(2)

    # Jetzt können wir gefahrlos alte OpenAI Tabs schließen
    for t in b.tabs:
        # Den gerade neu erstellten Tab nicht schließen!
        t_id = getattr(t.target, 'targetId', getattr(t.target, 'target_id', str(t.target)))
        nt_id = getattr(new_t.target, 'targetId', getattr(new_t.target, 'target_id', str(new_t.target)))
        if t_id == nt_id:
            continue
            
        curr = getattr(t, "url", getattr(t.target, "url", "")) or ""
        if "openai.com" in curr or "chatgpt.com" in curr:
            try:
                await t.close()
            except Exception as e:
                print(f"M30a WARN: Fehler beim Schließen von altem Tab: {e}")

    await asyncio.sleep(2)

    # URL check needs to wait for redirects to settle
    for _ in range(15):
        await asyncio.sleep(1)
        curr = getattr(new_t.target, "url", "") or getattr(new_t, "url", "") or ""
        # The initial URL contains /authorize? but the actual authorize page has a different path or we wait to see if it redirects
        if "log-in" in curr or "login" in curr:
            print("M30a OK: /log-in Seite erkannt. Re-Login noetig.")
            return True
            
        html = await new_t.get_content()
        html = html.lower()
        if "localhost:1455" in curr:
            print("M30a OK: Direkt Callback! Token gespeichert.")
            with open("/tmp/m30_skip_login.txt", "w") as f: f.write("1")
            return True
            
        if "authorize" in html or "zulassen" in html or "allow" in html or "continue" in html or "weiter" in html:
            # Only if the page actually rendered the authorize buttons
            print("M30a OK: Direkt auf Authorize Seite (kein Re-Login).")
            with open("/tmp/m30_skip_login.txt", "w") as f: f.write("1")
            return True

    print("M30a WARN: Unbekannter Zustand, versuche trotzdem Re-Login.")
    return True

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
