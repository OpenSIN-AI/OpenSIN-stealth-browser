import asyncio, os, subprocess, time, urllib.request

PORT = 9334
# Chrome 136+ weigert sich, das Root-Profil für Remote Debugging freizugeben.
# Lösung: user-data-dir auf Chrome/Default setzen (nested Default/Default).
# Funktioniert nachweislich seit Commit 6a20b7e.
CHROME_PROFILE = "/Users/jeremy/Library/Application Support/Google/Chrome/Default"


def _debug_ready(port) -> bool:
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json/version", timeout=0.5
        ):
            return True
    except Exception:
        return False


async def launch():
    if _debug_ready(PORT):
        print("Chrome laeuft bereits auf 9334!")
        return True

    print(
        "Starte Chrome ueber Binary, weil macOS open -a den Port nicht weiterreicht..."
    )
    CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    subprocess.Popen(
        [
            CHROME_BIN,
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={CHROME_PROFILE}",
            "--profile-directory=Default",
            "--no-first-run",
            "--no-default-browser-check",
            "--new-window",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(40):
        if _debug_ready(PORT):
            return True
        time.sleep(0.5)
    return False


if __name__ == "__main__":
    if asyncio.run(launch()):
        print("CHROME READY")
    else:
        print("CHROME FAILED")
