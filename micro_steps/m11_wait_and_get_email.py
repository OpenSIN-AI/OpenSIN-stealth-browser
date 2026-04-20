import asyncio, nodriver as uc, sys

_GET_EMAIL = """(function(){
    // Priority 1: The actual input field value (most reliable)
    var input = document.getElementById('mail') || 
                document.querySelector('input[name="email"]') ||
                document.querySelector('input[type="email"]');
    if(input && input.value && input.value.includes('@') && !input.value.includes('*')) {
        return input.value.trim();
    }
    
    // Priority 2: A copy-able element with the full email (not masked)
    var candidates = document.querySelectorAll('[data-clipboard-text], [data-copy], [class*="copy-text"]');
    for(var el of candidates) {
        var txt = el.getAttribute('data-clipboard-text') || el.getAttribute('data-copy') || (el.innerText || '').trim();
        if(txt && txt.includes('@') && !txt.includes('*')) return txt;
    }
    
    // Priority 3: Any element showing a real (non-masked) email
    var allEls = Array.from(document.querySelectorAll('span, p, div, td, li'));
    for(var el of allEls) {
        var txt = (el.innerText || el.textContent || '').trim();
        if(txt.includes('@') && txt.includes('.') && txt.length < 80 && !txt.includes(' ') && !txt.includes('*')) {
            return txt;
        }
    }
    return null;
})()"""

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "temp-mail" in url:
            t = tab
            break

    if not t:
        print("M11 FAIL: Kein Temp-Mail Tab!")
        return False

    try:
        await t.reload()
        await asyncio.sleep(3)
    except Exception:
        await asyncio.sleep(3)

    for attempt in range(15):
        val = await t.evaluate(_GET_EMAIL)
        if val and "@" in val and "*" not in val:
            val = val.strip()
            with open("/tmp/current_email.txt", "w") as f:
                f.write(val)
            print(f"M11 OK: Email erhalten: {val}")
            return True
        if attempt == 5:
            # Try to force-show the email by clicking the address area
            await t.evaluate("""
                var btn = document.querySelector('[class*="address"], [id*="address"]');
                if(btn) btn.click();
            """)
        await asyncio.sleep(1.5)

    print("M11 FAIL: Email nicht geladen (oder maskiert).")
    return False

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
