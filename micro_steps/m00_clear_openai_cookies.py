import asyncio, nodriver as uc, sys, os

_FLAGS = [
    "/tmp/m30_skip_login.txt",
    "/tmp/m30_login_mode.txt",
    "/tmp/m30_otp_needed.txt",
    "/tmp/current_otp2.txt",
    "/tmp/current_email.txt",
    "/tmp/current_otp.txt",
    "/tmp/current_password.txt",
    "/tmp/oauth_url.txt",
    "/tmp/m08_popup_seen.txt",
]


async def run():
    for f in _FLAGS:
        if os.path.exists(f):
            os.remove(f)
    b = await uc.start(host="127.0.0.1", port=9334)
    # Hole Cookies ueber die Browser-Connection direkt, kein Tab noetig.
    try:
        cookies = await b.connection.send(uc.cdp.network.get_cookies())
        for c in cookies:
            if "openai.com" in c.domain or "chatgpt.com" in c.domain:
                await b.connection.send(
                    uc.cdp.network.delete_cookies(
                        name=c.name, domain=c.domain, path=c.path
                    )
                )
    except Exception as e:
        print(f"M00 WARN: Konnte Cookies nicht loeschen: {e}")
    print("M00 OK: OpenAI Cookies + Flags geloescht (Temp-Mail intakt!).")
    return True


if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
