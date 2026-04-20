import nodriver as uc
import asyncio
import os

# Shared URL polling avoids a fixed post-click sleep while still preserving a
# short human-style pause before the next interaction starts.
from micro_steps._wait import wait_for_url_contains


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    email = None
    if os.path.exists("/tmp/current_email.txt"):
        with open("/tmp/current_email.txt", "r") as f:
            email = f.read().strip()

    if not email:
        print("S11 FAIL: No email found in /tmp/current_email.txt")
        return False

    # Find ALL OpenAI-related tabs
    auth_tab = None
    chatgpt_tab = None
    for tab in b.tabs:
        url = getattr(tab.target, "url", "") or ""
        if "auth.openai.com" in url:
            auth_tab = tab
        if "chatgpt.com" in url:
            chatgpt_tab = tab

    # Check if we're already past the email step (on password page)
    if auth_tab:
        auth_url = getattr(auth_tab.target, "url", "") or ""
        if "/password" in auth_url or "/create-account/password" in auth_url:
            print(f"S11 SKIP: Already on password page ({auth_url[:80]})")
            print(f"S11 OK: Email step was already completed")
            return True

        # We're on auth.openai.com but not on password page — enter email
        t = auth_tab
        await t.bring_to_front()
        await asyncio.sleep(2)
    elif chatgpt_tab:
        # We're on ChatGPT landing — click Sign up and wait for redirect
        t = chatgpt_tab
        await t.bring_to_front()
        print("S11: On ChatGPT landing, trying to click Sign up...")
        try:
            await t.evaluate("""
                const cookieBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.includes('akzeptieren') || b.innerText.includes('Accept'));
                if(cookieBtn) cookieBtn.click();
            """)
            await asyncio.sleep(0.5)

            await t.evaluate("""
                const btn = document.querySelector('[data-testid="signup-button"]');
                if (btn) {
                    btn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, cancelable: true, view: window}));
                    btn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, cancelable: true, view: window}));
                    btn.click();
                }
            """)
            print("S11 OK: Clicked sign up, polling for auth.openai.com...")
        except Exception as e:
            print(f"S11 ERROR: Failed to click sign up: {e}")

        # Replace the fixed 5-second wait with URL-aware polling so we move on
        # as soon as the redirect lands, while still keeping the existing flow
        # unchanged when the auth tab takes a bit longer to appear.
        redirected = await wait_for_url_contains(t, 'auth.openai.com', timeout=10)
        if redirected:
            print("S11 OK: Redirect to auth.openai.com detected")
        else:
            print("S11 WARN: Redirect to auth.openai.com not detected within timeout")

        # Re-check tabs for auth.openai.com
        for tab in b.tabs:
            url = getattr(tab.target, "url", "") or ""
            if "auth.openai.com" in url:
                auth_tab = tab
                t = auth_tab
                await t.bring_to_front()
                break

        if not auth_tab:
            print("S11 WARN: auth.openai.com not opened, proceeding with current tab")
    else:
        print("S11 FAIL: No OpenAI/ChatGPT tab found")
        return False

    # Now enter the email
    print(f"S11: Typing email {email}")
    try:
        email_input = await t.select('input[name="email"], input[type="email"]')
        if email_input:
            # Clear existing value
            await t.evaluate(
                "(function(sel) { var el = document.querySelector(sel); if(el) { el.value = ''; el.dispatchEvent(new Event('input', {bubbles:true})); } })('input[name=\"email\"], input[type=\"email\"]')"
            )
            await asyncio.sleep(0.3)
            await email_input.send_keys(email)
            await asyncio.sleep(0.5)

            # Click Continue/Weiter
            clicked = await t.evaluate("""(function(){
                var btns = Array.from(document.querySelectorAll("button"));
                var submit = btns.find(b => {
                    var txt = (b.innerText || b.textContent || "").toLowerCase();
                    return txt === "weiter" || txt === "continue" || txt === "fortsetzen";
                });
                if(submit) { submit.click(); return true; }
                return false;
            })()""")

            if not clicked:
                await t.send(
                    uc.cdp.input_.dispatch_key_event(
                        type_="keyDown", key="Enter", windows_virtual_key_code=13
                    )
                )
                await t.send(
                    uc.cdp.input_.dispatch_key_event(
                        type_="keyUp", key="Enter", windows_virtual_key_code=13
                    )
                )

            print("S11 OK: Email submitted")
        else:
            # No email input found — check if we're already on password page
            current_url = await t.evaluate("window.location.href")
            if "/password" in current_url:
                print(f"S11 SKIP: Already on password page ({current_url[:80]})")
                return True
            print(f"S11 FAIL: Email input not found. URL: {current_url[:80]}")
            await t.save_screenshot("/tmp/fail_s11_no_email_input.png")
            return False
    except Exception as e:
        print(f"S11 FAIL: Email input error: {e}")
        await t.save_screenshot("/tmp/fail_s11_email_error.png")
        return False

    # Preserve only the minimal anti-bot delay after submission. The old fixed
    # multi-second wait is removed because the next step should key off real UI
    # state instead of idling here unconditionally.
    await asyncio.sleep(0.5)
    return True


if __name__ == "__main__":
    asyncio.run(run())
