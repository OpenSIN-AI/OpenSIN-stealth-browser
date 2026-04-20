"""Shared OTP extraction helper with multi-strategy fallback.

This module centralizes the Temp-Mail email discovery and OTP extraction logic so
multiple micro-steps can reuse the exact same hardened behavior. The goal is to
improve reliability without changing the surrounding browser orchestration.
"""

import asyncio
import re
import time

# DOM selectors are kept in one place so the fallback strategies stay readable
# and future Temp-Mail markup changes only need to be updated here.
_EMAIL_ROW_SELECTORS = "tr.mail, div.mail, .inbox-dataList li, a.viewLink, a.title-subject, td > a"
_EMAIL_BODY_SELECTORS = ".inbox-data-content, .inboxView, .message-body, article, main, body"


async def find_openai_email(tab, timeout=60):
    """Find and open the most likely OpenAI email in Temp-Mail.

    Strategy order:
    1. Prefer inbox rows whose visible text looks like an OpenAI sender.
    2. Fall back to rows whose subject/body preview mentions OTP-like terms.
    3. Reload the inbox every few seconds until timeout expires.

    Returns True when an email was opened, otherwise False.
    """
    deadline = time.time() + timeout

    while time.time() < deadline:
        # Keep the backoff aligned with the remaining timeout so short polling
        # windows in the second-OTP flow do not accidentally sleep for too long.
        remaining = max(0, deadline - time.time())
        sleep_for = min(5, remaining) if remaining else 0

        try:
            # Strategy 1 + 2 run inside the page so we can inspect every visible
            # candidate row and click the best match in one DOM-consistent pass.
            opened = await tab.evaluate(
                f"""(function() {{
                    var candidates = Array.from(document.querySelectorAll({_EMAIL_ROW_SELECTORS!r}));
                    if (!candidates.length) return false;

                    function normalizedText(node) {{
                        return ((node && (node.innerText || node.textContent || node.title)) || '')
                            .replace(/\\s+/g, ' ')
                            .trim()
                            .toLowerCase();
                    }}

                    function isVisible(node) {{
                        if (!node) return false;
                        if (node.offsetParent !== null) return true;
                        var style = window.getComputedStyle(node);
                        return style && style.display !== 'none' && style.visibility !== 'hidden';
                    }}

                    function clickNode(node) {{
                        var target = node.closest('a, tr, li, div') || node;
                        target.click();
                        return true;
                    }}

                    var senderMatch = candidates.find(function(node) {{
                        var text = normalizedText(node);
                        return isVisible(node) && (
                            text.includes('openai') ||
                            text.includes('chatgpt') ||
                            text.includes('em.openai.com')
                        );
                    }});
                    if (senderMatch) return clickNode(senderMatch);

                    var subjectMatch = candidates.find(function(node) {{
                        var text = normalizedText(node);
                        return isVisible(node) && (
                            text.includes('verification') ||
                            text.includes('verify') ||
                            text.includes('code') ||
                            text.includes('otp') ||
                            text.includes('one-time')
                        );
                    }});
                    if (subjectMatch) return clickNode(subjectMatch);

                    return false;
                }})()"""
            )
            if opened:
                # Give Temp-Mail a short moment to render the opened message body
                # before the caller starts parsing the email content.
                await asyncio.sleep(1)
                return True

            # Strategy 3: force the inbox to refresh when no useful email row is
            # visible yet. location.reload() is intentionally simple and safe.
            await tab.evaluate("location.reload()")
            await asyncio.sleep(max(0.5, sleep_for))
        except Exception:
            # Temp-Mail is occasionally mid-navigation while polling. Sleeping and
            # retrying is safer than failing the whole OTP step on a transient DOM.
            await asyncio.sleep(max(0.5, sleep_for))

    return False


async def extract_otp_from_page(tab):
    """Extract the OTP from the currently displayed email.

    Multi-strategy extraction order:
    1. Read focused email-body containers and search for standalone 6-digit codes.
    2. Fall back to the full page text for the same strict numeric pattern.
    3. Inspect emphasized DOM nodes (<code>, <b>, <strong>, etc.) for a 6-char code.

    Returns the extracted code string or None when nothing reliable is found.
    """
    text_candidates = []

    try:
        # Strategy 1: prioritize the actual email container so unrelated sidebar
        # text or inbox chrome does not beat the real OTP in the regex scan.
        focused_text = await tab.evaluate(
            f"""(function() {{
                var nodes = Array.from(document.querySelectorAll({_EMAIL_BODY_SELECTORS!r}));
                var texts = nodes
                    .map(function(node) {{ return (node.innerText || node.textContent || '').trim(); }})
                    .filter(Boolean);
                return texts;
            }})()"""
        )
        if isinstance(focused_text, list):
            text_candidates.extend(focused_text)
    except Exception:
        pass

    try:
        # Strategy 2: use the entire page text as a broader fallback in case the
        # email body is rendered in a layout we do not explicitly target above.
        body_text = await tab.evaluate("document.body.innerText")
        if body_text:
            text_candidates.append(body_text)
    except Exception:
        pass

    # Numeric OTPs are the safest extraction target, so they get first priority.
    for text in text_candidates:
        matches = re.findall(r"(?<!\d)\d{6}(?!\d)", text)
        for match in matches:
            # Filter common false positives such as embedded years when possible.
            if not re.search(r"^(19|20)\d{2}$", match):
                return match

    try:
        # Strategy 3: many verification emails visually isolate the code inside a
        # bold or code-like element. We inspect those nodes separately as a last
        # resort before giving up.
        emphasized = await tab.evaluate(
            """(function() {
                var nodes = Array.from(document.querySelectorAll('code, b, strong, td, span, div'));
                return nodes
                    .map(function(node) { return (node.innerText || node.textContent || '').trim(); })
                    .filter(Boolean);
            })()"""
        )
        if isinstance(emphasized, list):
            for value in emphasized:
                if re.fullmatch(r"\d{6}", value):
                    return value
                if re.fullmatch(r"[A-Za-z0-9]{6}", value) and value.lower() != "google":
                    return value
    except Exception:
        pass

    return None


async def extract_otp_from_tempmail(tab, timeout=60):
    """Full Temp-Mail OTP flow: open the email first, then extract the code."""
    if await find_openai_email(tab, timeout=timeout):
        await asyncio.sleep(1)
        return await extract_otp_from_page(tab)
    return None
