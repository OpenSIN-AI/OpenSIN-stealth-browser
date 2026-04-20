import nodriver as uc
import asyncio
import random

# Shared condition polling lets onboarding advance on real UI readiness instead
# of hoping the next screen appears after an arbitrary number of seconds.
from micro_steps._wait import wait_for_condition


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    t = None
    for tab in b.tabs:
        tab_url = getattr(tab.target, "url", "") or ""
        if "about-you" in tab_url or "onboarding" in tab_url:
            t = tab
            break

    if not t:
        print("S13b SKIP: Kein Onboarding-Tab gefunden (nicht angezeigt)")
        return True

    await t.bring_to_front()
    await asyncio.sleep(1)

    print("S13b: Filling Onboarding form")
    try:
        await t.evaluate("""
            function setReactValue(selector, value) {
                var el = document.querySelector(selector);
                if (el) {
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, value);
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }
            setReactValue('input[name="name"]', 'Alex Meier');
            setReactValue('input[name="age"]', String(Math.floor(Math.random() * (45 - 25 + 1) + 25)));
        """)
        await asyncio.sleep(0.5)

        submit_btn = await t.select('button[type="submit"]')
        if submit_btn:
            await submit_btn.click()
            print("S13b OK: Clicked submit")
        else:
            print("S13b FAIL: Submit button not found")
            return False

        # Wait for the follow-up onboarding CTA to exist before trying to click
        # it. This removes the blind 4-second pause while keeping the same flow
        # and still tolerating slower page transitions.
        skip_ready = await wait_for_condition(
            t,
            "Array.from(document.querySelectorAll('button')).some(b => { const txt = (b.innerText || b.textContent || '').toLowerCase(); return txt.includes('überspringen') || txt.includes('skip'); })",
            timeout=15,
        )
        if skip_ready:
            print("S13b OK: Skip action became available")
        else:
            print("S13b WARN: Skip action did not appear within timeout")
        await asyncio.sleep(0.5)

        await t.evaluate("""
            var btns = Array.from(document.querySelectorAll('button'));
            var skipBtn = btns.find(b => b.innerText.includes('Überspringen') || b.innerText.includes('Skip') || b.innerText.includes('überspringen'));
            if (skipBtn) skipBtn.click();
        """)
        print("S13b OK: Clicked Skip on 'Was bringt dich zu ChatGPT'")

        # After skipping, poll for the final consent/continue CTA instead of
        # sleeping another fixed 4 seconds. This preserves the original action
        # but makes the wait conditional on the actual banner being present.
        lets_go_ready = await wait_for_condition(
            t,
            "Array.from(document.querySelectorAll('button')).some(b => { const txt = (b.innerText || b.textContent || '').toLowerCase(); return txt.includes('okay,') || txt.includes(\"let's go\") || txt.includes(\"los geht's\"); })",
            timeout=15,
        )
        if lets_go_ready:
            print("S13b OK: Final consent banner became available")
        else:
            print("S13b WARN: Final consent banner did not appear within timeout")
        await asyncio.sleep(0.5)

        await t.evaluate("""
            var btns = Array.from(document.querySelectorAll('button'));
            var letsgo = btns.find(b => b.innerText.includes('Okay,') || b.innerText.includes('let\'s go') || b.innerText.includes('Los geht\'s'));
            if (letsgo) letsgo.click();
        """)
        print("S13b OK: Handled final consent banner (if any)")

    except Exception as e:
        print(f"S13b ERROR: Failed to complete onboarding: {e}")
        return False

    await asyncio.sleep(0.5)
    return True


if __name__ == "__main__":
    asyncio.run(run())
