import asyncio, nodriver as uc, sys

async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = None
    b._process_pid = None

    t = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "openai.com" in url or "chatgpt.com" in url:
            t = tab
            break
    if not t:
        return False

    print("M17b: Warte auf erfolgreiches Submit (Wechsel zu /email-verification)...")
    for i in range(60):  # Max 30 Sekunden
        url = getattr(t.target, "url", "") or ""
        
        if "email-verification" in url:
            print("M17b OK: OpenAI hat das Passwort akzeptiert und die Mail gesendet!")
            return True

        try:
            task = asyncio.create_task(t.get_content())
            done, _ = await asyncio.wait([task], timeout=1.5)
            if done:
                html = task.result()
                html_l = html.lower()
                
                # CAPTCHA/Bot detection
                if any(kw in html_l for kw in ["arkose", "puzzle", "prove you are human", "funCaptcha"]):
                    print("M17b FAIL: CAPTCHA aufgetaucht!")
                    return False
                    
                # Validation error - ONLY if visible error text, not from scripts
                # Check for visible error elements specifically
                has_error = await t.evaluate("""(function(){
                    var errorEls = document.querySelectorAll('[class*="error"], [class*="invalid"], .help-text, [aria-invalid="true"]');
                    for(var el of errorEls) {
                        var txt = (el.innerText || "").trim();
                        if(txt && txt.length > 3 && txt.length < 200) return txt;
                    }
                    return null;
                })()""")
                
                if has_error:
                    print(f"M17b FAIL: Validierungsfehler: {has_error}")
                    return False
                    
        except Exception:
            pass
            
        await asyncio.sleep(0.5)
        
    print("M17b FAIL: Timeout.")
    return False

if __name__ == "__main__":
    sys.exit(0 if asyncio.run(run()) else 1)
