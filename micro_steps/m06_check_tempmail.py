import asyncio, nodriver as uc, sys

_CHECK = """(function(){
    var btns = Array.from(document.querySelectorAll("button, a, [class*='delete'], [id*='delete']"));
    var hasDelete = btns.some(b => {
        var t = (b.innerText || b.textContent || "").toLowerCase();
        return (t.includes("delete") || t.includes("l\u00f6schen") || t.includes("change") || t.includes("generate")) && b.offsetParent !== null;
    });
    // Also accept if email address is already visible
    var hasEmail = (document.getElementById("mail") && document.getElementById("mail").value) ||
                   Array.from(document.querySelectorAll("span, p, div")).some(el => {
                       var t = (el.innerText || "").trim();
                       return t.includes("@") && t.length < 80 && !t.includes(" ");
                   });
    return hasDelete || hasEmail;
})()"""

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    # Find temp-mail tab
    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "temp-mail" in url:
            t = tab
            break

    if not t:
        print("M06 FAIL: Kein Temp-Mail Tab!")
        return False

    for i in range(20):
        try:
            ok = await t.evaluate(_CHECK)
            if ok:
                print(f"M06 OK: Delete sichtbar nach {i * 0.5:.1f}s.")
                return True
        except Exception:
            pass
        await asyncio.sleep(0.5)

    print("M06 FAIL: Temp-Mail nicht geladen!")
    return False

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
