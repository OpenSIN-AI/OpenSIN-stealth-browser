import nodriver as uc
import asyncio
import os

# The shared helper keeps the OTP inbox scanning and code parsing behavior in a
# single place so s13 and s18 stay aligned when we harden extraction logic.
from _otp_helper import extract_otp_from_tempmail


async def run():
    b = await uc.start(host="127.0.0.1", port=9334)
    b._browser_process = b._process_pid = None

    temp_tab = next(
        (
            tab
            for tab in b.tabs
            if "temp-mail" in (getattr(tab.target, "url", "") or "")
        ),
        None,
    )
    if not temp_tab:
        print("S13 FAIL: No Temp-Mail tab found")
        return False

    await temp_tab.bring_to_front()
    await asyncio.sleep(2)

    # OTP discovery is now delegated to the shared helper. That keeps the
    # extraction behavior hardened while leaving the later typing/submission
    # sequence completely untouched, as required by the issue.
    print("S13: Waiting for OpenAI email in Temp-Mail...")
    otp = await extract_otp_from_tempmail(temp_tab, timeout=60)

    if otp:
        # Preserve the existing hand-off contract for downstream steps by writing
        # the resolved OTP to the same temp file as before.
        with open("/tmp/current_otp.txt", "w") as f:
            f.write(otp)
        print(f"S13 OK: Extracted OTP: {otp}")
    else:
        print("S13 FAIL: Could not extract OTP within time")
        return False

    auth_tab = next(
        (
            tab
            for tab in b.tabs
            if "auth.openai.com" in (getattr(tab.target, "url", "") or "")
        ),
        None,
    )
    if not auth_tab:
        print("S13 FAIL: No OpenAI Auth tab found to paste OTP")
        return False

    await auth_tab.bring_to_front()
    await asyncio.sleep(2)

    print("S13: Typing OTP into OpenAI")
    code_input = await auth_tab.select('input[name="code"], input[type="text"]')
    if code_input:
        await code_input.click()
        await asyncio.sleep(0.2)
        await auth_tab.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyDown", key="a", windows_virtual_key_code=65, modifiers=8
            )
        )
        await auth_tab.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyUp", key="a", windows_virtual_key_code=65, modifiers=8
            )
        )
        await asyncio.sleep(0.2)
        await auth_tab.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyDown", key="Backspace", windows_virtual_key_code=8
            )
        )
        await auth_tab.send(
            uc.cdp.input_.dispatch_key_event(
                type_="keyUp", key="Backspace", windows_virtual_key_code=8
            )
        )
        await asyncio.sleep(0.2)

        # Intentionally unchanged OTP typing behavior: this issue only hardens
        # extraction, not how the code gets entered or submitted.
        await code_input.send_keys(otp)
        await asyncio.sleep(1)

        clicked = await auth_tab.evaluate("""(function(){
            var btns = Array.from(document.querySelectorAll("button"));
            var submit = btns.find(b => {
                var txt = (b.innerText || b.textContent || "").toLowerCase();
                return txt.includes("weiter") || txt.includes("continue");
            });
            if(submit) { submit.click(); return true; }
            return false;
        })()""")

        if not clicked:
            await auth_tab.send(
                uc.cdp.input_.dispatch_key_event(
                    type_="keyDown", key="Enter", windows_virtual_key_code=13
                )
            )
            await auth_tab.send(
                uc.cdp.input_.dispatch_key_event(
                    type_="keyUp", key="Enter", windows_virtual_key_code=13
                )
            )

        print("S13 OK: OTP submitted")
    else:
        print("S13 FAIL: OTP input not found")
        return False

    await asyncio.sleep(5)
    return True


if __name__ == "__main__":
    asyncio.run(run())
